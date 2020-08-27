from discord import VoiceClient
from konoha.extensions.gateway import ExtendedDiscordVoiceWabSocket


class ExtendedVoiceClient:
    def __init__(self, original: VoiceClient):
        self.original = original
        self.original.ws = ExtendedDiscordVoiceWabSocket(original.ws)

    def __getattr__(self, attr):
        return getattr(self.original, attr)
