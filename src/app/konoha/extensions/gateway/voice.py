import aiohttp
import asyncio
import aiofiles
import json
import struct
import nacl.secret
import nacl.utils
import io
from discord.gateway import DiscordVoiceWebSocket, VoiceKeepAliveHandler
from discord.errors import ConnectionClosed
from konoha.extensions.rtp import Packet, RTPPacket
from konoha.extensions.opus import Decoder, BufferedDecoder


class ExtendedDiscordVoiceWabSocket:
    def __init__(self, original: DiscordVoiceWebSocket):
        self.original = original
        self.box = nacl.secret.SecretBox(
            bytes(self.original._connection.secret_key))
        self._lite_nonce = 1
        self.decoder = BufferedDecoder()

    @property
    def is_receiving(self):
        if hasattr(self, 'receive_task'):
            return not self.receive_task.cancelled() and not self.receive_task.done()
        return False

    def start_receive(self, path):
        self.receive_task = asyncio.create_task(self.receive_packets())
        self.decoder.start(path)

    def stop_receive(self):
        if hasattr(self, 'receive_task'):
            self.receive_task.cancel()
        self.decoder.stop()

    def decrypt_xsalsa20_poly1305(self, data):
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted = data[:8], data[8:]
            nonce = bytearray(24)
            nonce[:8] = header
        else:
            header, encrypted = data[:12], data[12:]
            nonce = bytearray(24)
            nonce[:12] = header
        return header, self.box.decrypt(bytes(encrypted), bytes(nonce))

    def decrypt_xsalsa20_poly1305_suffix(self, data):
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted, nonce = data[:8], data[8:-24], data[-24:]
        else:
            header, encrypted, nonce = data[:12], data[12:-24], data[-24:]
        return header, self.box.decrypt(bytes(encrypted), bytes(nonce))

    def decrypt_xsalsa20_poly1305_lite(self, data):
        is_rtcp = 200 <= data[1] < 205
        if is_rtcp:
            header, encrypted, _nonce = data[:8], data[8:-4], data[-4:]
        else:
            header, encrypted, _nonce = data[:12], data[12:-4], data[-4:]
        nonce = bytearray(24)
        nonce[:4] = _nonce
        return header, self.box.decrypt(bytes(encrypted), bytes(nonce))

    async def receive_packets(self):
        try:
            while True:
                state = self._connection
                recv = await self.loop.sock_recv(self._connection.socket, 2**16)
                decrypt_fn = getattr(self, f'decrypt_{state.mode}')
                pkt = Packet.from_data(recv)
                header, data = decrypt_fn(recv)
                pkt.decrypted = data
                if isinstance(pkt, RTPPacket):
                    pkt.calc_extention_header_length(data)
                    await self.decoder.push(pkt)
        except asyncio.CancelledError:
            while not self.buffer.empty():
                self.buffer.get_nowait()

    async def close(self, code=1000):
        if hasattr(self, 'io_task'):
            self.io_task.cancel()
        if hasattr(self, 'receive_task'):
            self.receive_task.cancel()
        await self.original.close(code)

    def __getattr__(self, attr):
        return getattr(self.original, attr)
