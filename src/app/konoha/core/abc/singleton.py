import threading
import abc


class Singleton(object, metaclass=abc.ABCMeta):
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        raise NotImplementedError

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
