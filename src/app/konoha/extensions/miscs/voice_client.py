from udp import UDPClient
import aiohttp
from aiohttp import ClientWebSocketResponse
import asyncio
import aiofiles
import asyncore
import threading
import json
import time
import struct
import enum
import nacl.secret
import nacl.encoding


class OPCode(enum.Enum):
    Dispatch = 0  # R
    Heartbeat = 1  # S / R
    Identify = 2  # S
    PresenceUpdate = 3  # S
    VoiceStateUpdate = 4  # S
    Resume = 6  # S
    Reconnect = 7  # R
    RequestGuildMembers = 8  # S
    InvalidSession = 9  # R
    Hello = 10  # R
    HeartbeatACK = 11  # R


class VoiceOPCode(enum.Enum):
    Identify = 0  # C
    SelectProtocol = 1  # C
    Ready = 2  # S
    Heartbeat = 3  # C
    SessionDescription = 4  # S
    Speaking = 5  # C / S
    HeartbeatACK = 6  # S
    Resume = 7  # C
    Hello = 8  # S
    Resumed = 9  # S
    ClientDisconnect = 13  # S


class VC:
    def __init__(self):
        self.connected = False
        self.authenticated = False
        self.established = False
        self.is_ready = False
        self.payload_selected = False
        self.started = False
        self.client = None
        self.ws = None
        self.voice_ws = None
        self.udp = None
        self.endpoint = ''
        self.udp_endpoint = ''
        self.udp_endpoint_port = 0
        self.session_id = ''
        self.token = ''
        self.ssrc = ''
        self.ip = ''
        self.port = 0
        self.secret_key = []
        self.enc_modes = []
        self.enc_mode = "xsalsa20_poly1305"
        self.server_id = '705052322761277540'
        self.channel_id = '705052323335897180'
        self.user_id = '740158924476645396'
        self.bot_token = ''

    async def heartbeat(self, ms):
        while True:
            await asyncio.sleep(ms / 1000)
            await self.ws.send_json({"op": 1, "d": None})

    async def heartbeat_vc(self, ms):
        while True:
            print("Heartbeat")
            await asyncio.sleep(ms / 1000)
            await self.voice_ws.send_json({"op": 3, "d": int(time.time()*1000)})

    async def auth(self):
        await self.ws.send_json({
            "op": OPCode.Identify.value,
            "d": {
                "token": self.bot_token,
                "properties": {
                    "$os": "linux",
                    "$browser": "vc_connection",
                    "$device": "vc_connection",
                }
            }
        })
        self.authenticated = True

    async def connect(self):
        await self.ws.send_json({
            "op": OPCode.VoiceStateUpdate.value,
            "d": {
                "guild_id": self.server_id,
                "channel_id": self.channel_id,
                "self_mute": False,
                "self_deaf": False,
            }
        })
        self.connected = True

    async def establish(self):
        await self.voice_ws.send_json({
            "op": 0,
            "d": {
                "server_id": self.server_id,
                "user_id": self.user_id,
                "session_id": self.session_id,
                "token": self.token
            }
        })
        self.established = True

    async def select_udp_payload(self):
        await self.voice_ws.send_json({
            "op": 1,
            "d": {
                "protocol": "udp",
                "data": {
                    "address": self.udp_endpoint,
                    "port": self.udp_endpoint_port,
                    "mode": self.enc_mode
                }
            }
        })
        self.payload_selected = True

    def decrypt_xsalsa20_poly1305(self, data, type):
        nonce = bytearray(24)
        if type == "RTP":
            nonce[:12] = data[:12]
            raw_audio = self.box.decrypt(bytes(data[12:]), bytes(nonce))
        else:
            nonce[:8] = data[:8]
            raw_audio = self.box.decrypt(bytes(data[8:]), bytes(nonce))
        return raw_audio

    def parse_header(self, data):
        # RTCPヘッダはpayload_typeが200-204 (Receiveは201)
        payload_type = struct.unpack_from('>B', data, 1)[0]
        if 201 <= payload_type <= 204:
            return "RTCP"
        return "RTP"

    async def receive_data(self):
        async with aiofiles.open('tmp.of', 'wb') as f:
            while True:
                data, addr = await self.client.receive()
                type = self.parse_header(data)
                audio = self.decrypt_xsalsa20_poly1305(data, type)
                await f.write(audio)

    async def handle_vc_message(self, msg):
        print(f"vc: {msg}")
        op = msg["op"]
        d = msg["d"]
        t = msg.get("t")
        if op == 2:
            print(d)
            self.ssrc = d["ssrc"]
            self.ip = d["ip"]
            self.port = d["port"]
            self.enc_modes = d["modes"]
        if op == 4:
            print(d)
            self.secret_key = d["secret_key"]
        if op == 8:
            asyncio.create_task(self.heartbeat_vc(d["heartbeat_interval"]))
        if not self.established:
            print("Establish")
            await self.establish()
        elif self.ssrc != "" and not self.payload_selected:
            packet = self.to_ping_packet()
            self.client = await UDPClient.create(self.ip, self.port)
            self.client.send(packet)
            data, addr = await self.client.receive()
            print(data)
            self.from_ping_packet(data)
            await self.select_udp_payload()
            print("UDP Selected")
        if self.secret_key and not self.started:
            self.started = True
            self.box = nacl.secret.SecretBox(bytes(self.secret_key))
            asyncio.create_task(self.receive_data())

    def to_ping_packet(self):
        p = bytearray(74)
        p[:2] = struct.pack(">H", 1)
        p[2:4] = struct.pack(">H", 70)
        p[4:8] = struct.pack(">I", self.ssrc)
        p[72:] = struct.pack(">H", self.port)
        return p

    def from_ping_packet(self, data):
        self.udp_endpoint = struct.unpack_from(
            '>64s', data, 8)[0].decode('ascii').rstrip('\x00')
        self.udp_endpoint_port = struct.unpack_from('>H', data, 72)[0]

    async def connect_vc(self):
        try:
            sess = aiohttp.ClientSession()
            self.voice_ws = await sess.ws_connect(f"wss://{self.endpoint.replace(':80', '')}/?v=4")
            while True:
                msg = await self.voice_ws.receive()
                if msg.type == aiohttp.WSMsgType.text:
                    if msg.data == 'close':
                        break
                    else:
                        await self.handle_vc_message(json.loads(msg.data))
                elif msg.type == aiohttp.WSMsgType.closed:
                    break
                elif msg.type == aiohttp.WSMsgType.error:
                    break
        except:
            await self.voice_ws.close()
            await sess.close()

    async def handle_message(self, msg):
        # print(f"main: {str(msg)[:200]}")
        op = msg["op"]
        d = msg["d"]
        t = msg.get("t")
        if op == OPCode.Hello.value:
            asyncio.create_task(self.heartbeat(d["heartbeat_interval"]))
        if op == OPCode.Dispatch.value:
            if t == "VOICE_STATE_UPDATE":
                self.session_id = d["session_id"]
            if t == "VOICE_SERVER_UPDATE":
                print(d)
                self.token = d["token"]
                self.endpoint = d["endpoint"]
        if not self.authenticated:
            print("Auth")
            await self.auth()
        if not self.connected:
            print("Conn")
            await self.connect()
        if self.endpoint != '' and self.session_id != '' and not self.is_ready:
            print("VC")
            self.is_ready = True
            asyncio.create_task(self.connect_vc())
            return True

    async def start(self):
        try:
            sess = aiohttp.ClientSession()
            self.ws = await sess.ws_connect('wss://gateway.discord.gg/?v=6&encoding=json')
            while True:
                msg = await self.ws.receive()
                if msg.type == aiohttp.WSMsgType.text:
                    if msg.data == 'close':
                        break
                    else:
                        await self.handle_message(json.loads(msg.data))
                elif msg.type == aiohttp.WSMsgType.closed:
                    break
                elif msg.type == aiohttp.WSMsgType.error:
                    break
        except:
            await self.voice_ws.close()
            await sess.close()


if __name__ == "__main__":
    vc = VC()
    asyncio.run(vc.start())
