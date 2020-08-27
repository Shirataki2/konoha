import ctypes
import array
import os
import math
import sys
from ctypes.util import find_library
from discord import DiscordException

libopus = None
c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)


class OpusError(DiscordException):
    """An exception that is thrown for libopus related errors.
    Attributes
    ----------
    code: :class:`int`
        The error code returned.
    """

    def __init__(self, code):
        self.code = code
        msg = libopus.opus_strerror(self.code).decode('utf-8')
        # log.info('"%s" has happened', msg)
        super().__init__(msg)


class OpusNotLoaded(DiscordException):
    """An exception that is thrown for when libopus is not loaded."""
    pass


class EncoderStruct(ctypes.Structure):
    pass


class DecoderStructure(ctypes.Structure):
    pass


EncoderStructPtr = ctypes.POINTER(EncoderStruct)
DecoderStructPtr = ctypes.POINTER(DecoderStructure)


def _err_lt(result, func, args):
    if result < 0:
        # log.info('error has happened in %s', func.__name__)
        raise OpusError(result)
    return result


def _err_ne(result, func, args):
    ret = args[-1]._obj
    if ret.value != 0:
        # log.info('error has happened in %s', func.__name__)
        raise OpusError(ret.value)
    return result


exported_functions = [
    ('opus_strerror',
        [ctypes.c_int], ctypes.c_char_p, None),
    ('opus_encoder_get_size',
        [ctypes.c_int], ctypes.c_int, None),
    ('opus_encoder_create',
        [ctypes.c_int, ctypes.c_int, ctypes.c_int, c_int_ptr], EncoderStructPtr, _err_ne),
    ('opus_encode',
        [EncoderStructPtr, c_int16_ptr, ctypes.c_int, ctypes.c_char_p, ctypes.c_int32], ctypes.c_int32, _err_lt),
    ('opus_encoder_ctl',
        None, ctypes.c_int32, _err_lt),
    ('opus_encoder_destroy',
        [EncoderStructPtr], None, None),

    ('opus_packet_get_bandwidth',
        [ctypes.c_char_p], ctypes.c_int, _err_lt),
    ('opus_packet_get_nb_channels',
        [ctypes.c_char_p], ctypes.c_int, _err_lt),
    ('opus_packet_get_nb_frames',
        [ctypes.c_char_p, ctypes.c_int], ctypes.c_int, _err_lt),
    ('opus_packet_get_samples_per_frame',
        [ctypes.c_char_p, ctypes.c_int], ctypes.c_int, _err_lt),
    ('opus_packet_get_nb_samples',
        [DecoderStructPtr, ctypes.c_char_p, ctypes.c_int32], ctypes.c_int, _err_lt),

    ('opus_decoder_get_size',
        [ctypes.c_int], ctypes.c_int, None),
    ('opus_decoder_create',
        [ctypes.c_int, ctypes.c_int, c_int_ptr], DecoderStructPtr, _err_ne),
    ('opus_decode',
        [DecoderStructPtr, ctypes.c_char_p, ctypes.c_int32, c_int16_ptr, ctypes.c_int, ctypes.c_int], ctypes.c_int, _err_lt),
    ('opus_decoder_ctl',
        None, ctypes.c_int32, _err_lt),
    ('opus_decoder_destroy',
        [DecoderStructPtr], None, None),

]

OK = 0
APPLICATION_AUDIO = 2049
APPLICATION_VOIP = 2048
APPLICATION_LOWDELAY = 2051
CTL_SET_BITRATE = 4002
CTL_SET_BANDWIDTH = 4008
CTL_SET_FEC = 4012
CTL_SET_PLP = 4014
CTL_SET_SIGNAL = 4024

CTL_SET_GAIN = 4034
CTL_LAST_PACKET_DURATION = 4039

band_ctl = {
    'narrow': 1101,
    'medium': 1102,
    'wide': 1103,
    'superwide': 1104,
    'full': 1105,
}

signal_ctl = {
    'auto': -1000,
    'voice': 3001,
    'music': 3002,
}


def libopus_loader(name):
    # create the library...
    lib = ctypes.cdll.LoadLibrary(name)

    # register the functions...
    for item in exported_functions:
        func = getattr(lib, item[0])

        try:
            if item[1]:
                func.argtypes = item[1]

            func.restype = item[2]
        except KeyError:
            pass

        try:
            if item[3]:
                func.errcheck = item[3]
        except KeyError:
            pass
            # log.exception("Error assigning check function to %s", func)

    return lib


def _load_default():
    global libopus
    try:
        if sys.platform == 'win32':
            _basedir = os.path.dirname(os.path.abspath(__file__))
            _bitness = 'x64' if sys.maxsize > 2**32 else 'x86'
            _filename = os.path.join(
                _basedir, 'bin', 'libopus-0.{}.dll'.format(_bitness))
            libopus = libopus_loader(_filename)
        else:
            libopus = libopus_loader(ctypes.util.find_library('opus'))
    except Exception:
        libopus = None

    return libopus is not None


def load_opus(name):
    global libopus
    libopus = libopus_loader(name)


def is_loaded():
    global libopus
    return libopus is not None


class OpusBaseStruct:
    SAMPLING_RATE = 48000
    CHANNELS = 2
    FRAME_LENGTH = 20
    SAMPLE_SIZE = 4  # (bit_rate / 8) * CHANNELS (bit_rate == 16)
    SAMPLES_PER_FRAME = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)
    FRAME_SIZE = SAMPLES_PER_FRAME * SAMPLE_SIZE


class Encoder(OpusBaseStruct):
    def __init__(self, application=APPLICATION_AUDIO):
        self.application = application

        if not is_loaded():
            if not _load_default():
                raise OpusNotLoaded()

        self._state = self._create_state()
        self.set_bitrate(128)
        self.set_fec(True)
        self.set_expected_packet_loss_percent(0.15)
        self.set_bandwidth('full')
        self.set_signal_type('auto')

    def __del__(self):
        if hasattr(self, '_state'):
            libopus.opus_encoder_destroy(self._state)
            self._state = None

    def _create_state(self):
        ret = ctypes.c_int()
        return libopus.opus_encoder_create(self.SAMPLING_RATE, self.CHANNELS, self.application, ctypes.byref(ret))

    def set_bitrate(self, kbps):
        kbps = min(512, max(16, int(kbps)))

        libopus.opus_encoder_ctl(self._state, CTL_SET_BITRATE, kbps * 1024)
        return kbps

    def set_bandwidth(self, req):
        if req not in band_ctl:
            raise KeyError('%r is not a valid bandwidth setting. Try one of: %s' % (
                req, ','.join(band_ctl)))

        k = band_ctl[req]
        libopus.opus_encoder_ctl(self._state, CTL_SET_BANDWIDTH, k)

    def set_signal_type(self, req):
        if req not in signal_ctl:
            raise KeyError('%r is not a valid signal setting. Try one of: %s' % (
                req, ','.join(signal_ctl)))

        k = signal_ctl[req]
        libopus.opus_encoder_ctl(self._state, CTL_SET_SIGNAL, k)

    def set_fec(self, enabled=True):
        libopus.opus_encoder_ctl(self._state, CTL_SET_FEC, 1 if enabled else 0)

    def set_expected_packet_loss_percent(self, percentage):
        libopus.opus_encoder_ctl(self._state, CTL_SET_PLP, min(
            100, max(0, int(percentage * 100))))

    def encode(self, pcm, frame_size):
        max_data_bytes = len(pcm)
        pcm = ctypes.cast(pcm, c_int16_ptr)
        data = (ctypes.c_char * max_data_bytes)()

        ret = libopus.opus_encode(
            self._state, pcm, frame_size, data, max_data_bytes)

        return array.array('b', data[:ret]).tobytes()


class Decoder(OpusBaseStruct):
    def __init__(self):
        if not is_loaded():
            if not _load_default():
                raise OpusNotLoaded()
        self._state = self._create_state()

    def _create_state(self):
        ret = ctypes.c_int()
        return libopus.opus_decoder_create(self.SAMPLING_RATE, self.CHANNELS, ctypes.byref(ret))

    @staticmethod
    def packet_get_bandwidth(data):
        d_ptr = ctypes.c_char_p(data)
        return libopus.opus_packet_get_bandwidth(d_ptr)

    @staticmethod
    def packet_get_nb_channel(data):
        d_ptr = ctypes.c_char_p(data)
        return libopus.opus_packet_get_nb_channels(d_ptr)

    @staticmethod
    def packet_get_nb_frames(data):
        d_ptr = ctypes.c_char_p(data)
        length = len(data)
        return libopus.opus_packet_get_nb_frames(d_ptr, ctypes.c_int(length))

    def packet_get_samples_per_frame(self, data):
        d_ptr = ctypes.c_char_p(data)
        return libopus.opus_packet_get_samples_per_frame(d_ptr, self.SAMPLING_RATE)

    def packet_get_nb_samples(self, data):
        d_ptr = ctypes.c_char_p(data)
        length = len(data)
        return libopus.opus_packet_get_nb_samples(self._state, d_ptr, ctypes.c_int(length))

    def _get_last_packet_duration(self):
        ret = ctypes.c_int32()
        libopus.opus_decoder_ctl(
            self._state, CTL_LAST_PACKET_DURATION, ctypes.byref(ret))
        return ret.value

    def _set_gain(self, adjustment):
        return libopus.opus_decoder_ctl(self._state, CTL_SET_GAIN, adjustment)

    def set_gain(self, dB):
        # dB * 2^n where n is 8 (Q8)
        dB_Q8 = max(-32768, min(32767, round(dB * 256)))
        return self._set_gain(dB_Q8)

    def set_volume(self, mult):
        return self.set_gain(20 * math.log10(mult))  # amplitude ratio

    def decode(self, data, /, *, fec=False):
        if data is None:
            frame_size = self._get_last_packet_duration()
        else:
            frames = self.packet_get_nb_frames(data)
            samples_per_frame = self.packet_get_samples_per_frame(data)
            frame_size = frames * samples_per_frame
        pcm = (ctypes.c_int16 * (frame_size * self.CHANNELS))()
        pcm_ptr = ctypes.cast(pcm, c_int16_ptr)
        decode_fec = int(bool(fec))
        libopus.opus_decode(
            self._state, data, len(data), pcm_ptr, self.FRAME_SIZE, decode_fec
        )
        return array.array('h', pcm).tobytes()
