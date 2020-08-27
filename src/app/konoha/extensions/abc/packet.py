from abc import ABCMeta, abstractmethod
from typing import Tuple
import nacl.secret

__all__ = [
    'PacketBase',
    'ComparablePacketMixin'
]


class PacketBase:
    pass


class ComparablePacketMixin(metaclass=ABCMeta):
    @property
    @abstractmethod
    def timestamp(self):
        raise NotImplementedError

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    def __eq__(self, other):
        return self.timestamp == other.timestamp
