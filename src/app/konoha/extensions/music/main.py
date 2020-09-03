import asyncio
import itertools
import random
from discord.ext import commands
from discord import VoiceClient, Embed, PCMVolumeTransformer, FFmpegPCMAudio
from typing import Union
from konoha.extensions.music.downloader import YTDLDownloader, Video
from konoha.core.bot.konoha import Konoha
from konoha.core import config, KonohaException
from konoha.core.utils.pagination import EmbedPaginator


class MusicException(KonohaException):
    pass


class Song:
    def __init__(self, src: Video, ctx: commands.Context):
        self.src = src
        self.ctx = ctx
        self.requester = ctx.author

    def get_duration(self):
        dur = int(self.src.duration)
        M, S = divmod(dur, 60)
        H, M = divmod(M, 60)
        D, H = divmod(H, 24)
        W, D = divmod(D, 7)
        t = ""
        if W > 0:
            t += f"{W}週"
        if D > 0:
            t += f"{D}日 "
        if H > 0:
            t += f"{H}h "
        if M > 0:
            t += f"{M}m "
        if S > 0:
            t += f"{S}s"
        return t

    def get_source(self):
        return PCMVolumeTransformer(
            FFmpegPCMAudio(
                self.src.url,
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                options=f'-vn'
            )
        )

    def to_embed(self, *, embed=None):
        if embed is None:
            embed = Embed()
        embed.title = self.src.title
        embed.url = self.src.webpage_url
        embed.set_author(
            name="Now Playing...",
            icon_url=self.ctx.bot.user.avatar_url
        )
        embed.add_field(
            name="動画時間",
            value=self.get_duration()
        )
        embed.add_field(
            name="投稿者",
            value=f"[{self.src.uploader}]({self.src.uploader_url})"
        )
        embed.add_field(
            name="Request by",
            value=self.requester
        )
        embed.set_thumbnail(url=self.src.thumbnail)
        return embed


class PlayList(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, idx):
        del self._queue[idx]

    def to_paginator(self):
        paginator = EmbedPaginator(
            title="再生リスト", color=config.theme_color, footer="Page $p / $P")
        paginator.new_page()
        if self.qsize() == 0:
            return None
        for i, v in enumerate(self._queue.__iter__()):
            paginator.add_row(
                f"[{i+1}] {v.src.title}", f"[{v.get_duration()}, Requested by {v.requester.mention}]({v.src.webpage_url})")
        return paginator


class VoiceState:
    def __init__(self, bot: Konoha, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx
        self.loop = False
        self.loop_queue = False
        self.play = asyncio.Event()
        self._volume = 1.0
        self.vc = None
        self.cur = None
        self.queue = PlayList()
        self.playback = self.bot.loop.create_task(self.playback_loop())

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        self.vc.source.volume = volume
        self._volume = volume

    def __del__(self):
        self.playback.cancel()

    @property
    def is_playing(self):
        return self.vc and self.cur

    async def playback_loop(self):
        while True:
            self.play.clear()
            if not self.loop:
                try:
                    self.cur = await asyncio.wait_for(self.queue.get(), 180)
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return
            self.cur: Song
            source = self.cur.get_source()
            source.volume = self.volume
            self.vc.play(source, after=self.play_next)
            await self.cur.ctx.channel.send(embed=self.cur.to_embed())
            await self.play.wait()

    def play_next(self, err=None):
        if err:
            raise MusicException(str(err))
        if self.loop_queue and self.cur:
            self.queue.put_nowait(self.cur)
        self.play.set()

    def skip(self):
        if self.is_playing:
            self.vc.stop()

    async def stop(self):
        self.queue.clear()
        if self.vc:
            await self.vc.disconnect()
            self.vc = None
