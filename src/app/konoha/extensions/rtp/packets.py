from konoha.extensions.abc import (
    PacketBase,
    ComparablePacketMixin
)
import struct

__all__ = [
    'RTPPacket',
    'RTCPPacket',
    'Packet'
]


class RTPPacket(PacketBase, ComparablePacketMixin):
    def __init__(self, data):
        self.version = (data[0] & 0b11000000) >> 6
        self.padding = (data[0] & 0b00100000) >> 5
        self.extend = (data[0] & 0b00010000) >> 4
        self.cc = data[0] & 0b00001111
        self.marker = data[1] >> 7
        self.payload_type = data[1] & 0b01111111
        (
            self.seq,
            self._timestamp,
            self.ssrc
        ) = struct.unpack_from('>HII', data, 2)
        self.header = data[:12]
        self.offset = 0
        self.decrypted = None

    def calc_extention_header_length(self, data):
        if self.cc:
            self.csrcs = struct.unpack_from(
                '>%dI' % self.cc, data, self.offset)
            self.offset += self.cc * 4
        if self.extend:
            self.profile, self.ext_length = struct.unpack_from(
                '>HH', data)
            self.ext_header = struct.unpack_from(
                '>%dI' % self.ext_length, data, 4)
            self.offset += self.ext_length * 4 + 4
        self.decrypted = self.decrypted[self.offset:]

    @property
    def timestamp(self):
        return self._timestamp

    def __repr__(self):
        return (f'<RTPPacket timestamp={self.timestamp!r} '
                f'ssrc={self.ssrc!r} seq={self.seq!r} '
                f'payload_type={self.payload_type!r} '
                f'cc={self.cc!r}>')


class RTCPPacket(PacketBase):
    def __init__(self, data):
        self.version = (data[0] & 0b11000000) >> 6
        self.padding = (data[0] & 0b00100000) >> 5
        self.rc = data[0] & 0b00011111
        self.type = data[1]
        self.length = struct.unpack_from('>H', data, 2)[0]
        self.ssrc = struct.unpack_from('>I', data, 4)[0]
        self.header = data[:8]
        self.data = data[8:]
        self.decrypted = None

    def __repr__(self):
        return (f'<RTCPPacket type={self.type!r} '
                f'ssrc={self.ssrc!r}>')


class Packet(PacketBase):
    @classmethod
    def from_data(cls, data):
        if 200 <= data[1] <= 204:
            return RTCPPacket(data)
        return RTPPacket(data)
