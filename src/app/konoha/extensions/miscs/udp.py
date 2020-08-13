import asyncio
import warnings


class VCDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def connection_made(self, transport):
        self.endpoint.transport = transport

    def connection_lost(self, exc):
        assert exc is None
        if self.endpoint.write_ready_future is not None:
            self.endpoint.write_ready_future.set_result(None)
        self.endpoint.close()

    def datagram_received(self, data, addr):
        self.endpoint.feed_datagram(data, addr)

    def error_received(self, exc):
        msg = 'Endpoint received an error: {!r}'
        warnings.warn(msg.format(exc))

    def pause_writing(self):
        assert self.endpoint.write_ready_future is None
        loop = self.endpoint.transport._loop
        self.endpoint.write_ready_future = loop.create_future()

    def resume_writing(self):
        assert self.endpoint.write_ready_future is not None
        self.endpoint.write_ready_future.set_result(None)
        self.endpoint.write_ready_future = None


class UDPClient:
    def __init__(self, queue_size=0):
        self.queue = asyncio.Queue(queue_size)
        self.is_closed = False
        self.transport = None
        self.write_ready_future = None

    def feed_datagram(self, data, addr):
        try:
            self.queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            warnings.warn("Client Queue is Full!")

    def close(self):
        if self.is_closed:
            return
        self.is_closed = True
        if self.queue.empty():
            self.feed_datagram(None, None)
        if self.transport:
            self.transport.close()

    def send(self, data, addr=None):
        if self.is_closed:
            raise IOError("client session is closed")
        self.transport.sendto(data, addr)

    async def receive(self):
        if self.queue.empty() and self.is_closed:
            raise IOError("client session is closed")
        data, addr = await self.queue.get()
        if data is None:
            raise IOError("client session is closed")
        return data, addr

    def abort(self):
        if self.is_closed:
            raise IOError("client session is closed")
        self.transport.abort()
        self.close()

    async def drain(self):
        if self.write_ready_future is not None:
            return self.write_ready_future

    @property
    def address(self):
        return self.transport.get_extra_info("socket").getsockname()

    @classmethod
    async def create(cls, host, port, remote=True, **kwargs):
        loop = asyncio.get_event_loop()
        client = cls()
        kwargs['remote_addr' if remote else 'local_addr'] = host, port
        kwargs['protocol_factory'] = lambda: VCDatagramProtocol(client)
        await loop.create_datagram_endpoint(**kwargs)
        return client
