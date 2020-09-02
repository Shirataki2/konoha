import asyncio
import aiofiles
import threading
import itertools
import wave
import time
import tempfile
import secrets
import os
from pathlib import Path
from subprocess import Popen, PIPE
from konoha.extensions.opus.opus import Decoder
from konoha.core.log.logger import get_module_logger
from functools import partial

logger = get_module_logger(__name__)


class PacketQueue(asyncio.Queue):
    def __init__(self, buffer_size):
        super().__init__(buffer_size)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return itertools.islice(
                self._queue, item.start, item.stop, item.step)
        else:
            return self._queue[item]


class BufferedDecoder:
    DELAY = Decoder.FRAME_LENGTH / 1000.0

    def __init__(self, *, buffer_size=10000):
        if buffer_size < 40:
            raise ValueError(
                'Buffer sizeは40以上を指定してください.(指定値: %d)' % buffer_size)
        self.decoder = Decoder()
        self.buffer_size = buffer_size // self.decoder.FRAME_LENGTH
        self.buffer = PacketQueue(buffer_size)
        self.last = None
        self.decoded = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    async def push(self, packet):
        await self.buffer.put(packet)

    async def pop(self):
        pkt = await self.buffer.get()
        return pkt

    async def write_buffer(self, path):
        try:
            fp = '/tmp/' + secrets.token_hex(8) + '.wav'
            f = wave.open(fp, "wb")
            f.setnchannels(Decoder.CHANNELS)
            f.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
            f.setframerate(Decoder.SAMPLING_RATE)
            while True:
                pkt = await self.pop()
                if self.last is None:
                    f.writeframes(self.decoder.decode(pkt.decrypted))
                else:
                    data = self.decoder.decode(pkt.decrypted)
                    logger.debug(str(pkt))
                    elapsed = (pkt.timestamp - self.last) / \
                        Decoder.SAMPLING_RATE
                    if elapsed > 0.02:
                        margin = bytes(2*int(Decoder.SAMPLE_SIZE *
                                             (elapsed - 0.02) *
                                             Decoder.SAMPLING_RATE))
                        await self.loop.run_in_executor(None, partial(f.writeframes, margin))
                    f.writeframes(data)
                self.last = pkt.timestamp
        except asyncio.CancelledError:
            f.close()
            main_proc = await asyncio.create_subprocess_shell(
                f'ffmpeg -i {fp} -y -vn -ar 44100 -ac 2 -b:a 192k -loglevel warning {path}',
            )
            await main_proc.wait()
            os.remove(fp)
            self.decoded.set()
        except Exception as e:
            print(e)

    def stop(self):
        if self.task:
            self.task.cancel()

    def start(self, path='tmp'):
        self.task = asyncio.create_task(self.write_buffer(path))
