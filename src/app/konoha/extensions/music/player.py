from discord.player import FFmpegAudio, PCMVolumeTransformer
from discord.opus import Encoder as OpusEncoder
import shlex


class FFmpegPCMAudio(FFmpegAudio):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        args = []
        subprocess_kwargs = {
            'stdin': source if pipe else None, 'stderr': stderr}

        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))

        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000',
                     '-ac', '2', '-loglevel', 'warning'))

        if isinstance(options, str):
            args.extend(shlex.split(options))

        args.append('pipe:1')

        super().__init__(source, executable=executable, args=args, **subprocess_kwargs)

    def read(self):
        ret = self._stdout.read(OpusEncoder.FRAME_SIZE)
        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

    def is_opus(self):
        return False
