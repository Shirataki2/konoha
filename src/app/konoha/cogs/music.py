import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
from typing import Dict, List

import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
from konoha.extensions.music import VoiceState, YTDLDownloader, Video, Song

logger = get_module_logger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        self.voice_states: Dict[str, VoiceState] = {}

    def get_voice_state(self, ctx):
        if vs := self.voice_states.get(ctx.guild.id):
            return vs
        vs = VoiceState(self.bot, ctx)
        self.voice_states[ctx.guild.id] = vs
        return vs

    def cog_unload(self):
        for vs in self.voice_states.values():
            self.bot.loop.create_task(vs.stop())

    async def cog_before_invoke(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('このコマンドはDM上では実行できません')
        ctx.vs = self.get_voice_state(ctx)

    @commands.command(invoked_subcommand=True)
    async def join(self, ctx: commands.Context):
        '''
        Botがボイスチャンネルに参加します

        このコマンドを呼び出したユーザが入っているボイスチャンネルに入室するので
        呼び出す前に特定のボイスチャンネルに参加している必要があります
        '''
        ch = ctx.author.voice.channel
        if ctx.vs.vc:
            return await ctx.vs.vc.move_to(ch)
        ctx.vs.vc = await ch.connect()
        print(ctx.vs.vc)

    @commands.command()
    async def leave(self, ctx: commands.Context):
        '''
        Botを退出させてプレイリストを空にします
        '''
        if not ctx.vs.vc:
            return await ctx.send('まだボイスチャンネルに参加していません')
        await ctx.vs.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command()
    async def volume(self, ctx: commands.Context, *, volume: int):
        '''
        再生ボリューム変更します

        0%から300%の範囲で指定可能です
        '''
        if 0 > volume > 300:
            return await ctx.send('ボリュームは0~300%の間で指定可能です')
        ctx.vs.volume = volume / 100
        return await ctx.send(f'ボリュームを **{volume}%** に変更しました')

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if ctx.vs.is_playing and ctx.vs.vc.is_playing():
            ctx.vs.vc.pause()
            await ctx.message.add_reaction('⏸')

    @commands.command()
    async def resume(self, ctx: commands.Context):
        if not ctx.vs.is_playing and not ctx.vs.vc.is_playing():
            ctx.vs.vc.pause()
            await ctx.message.add_reaction('▶')

    async def song_select(self, songs: List[Video], ctx: commands.Context):
        embed = discord.Embed(title="曲を選んでください", color=config.theme_color)
        emojis = ("1⃣", "2⃣", "3⃣", "4⃣", "5⃣")
        for emoji, song in zip(emojis, songs):
            embed.add_field(name=f"{emoji} {song.title}",
                            value=song.webpage_url, inline=False)
        message = await ctx.send(embed=embed)
        for emoji, _ in zip(emojis, songs):
            await message.add_reaction(emoji)

        def check_reaction(r: discord.Reaction, u: discord.Member):
            return all([
                r.message.id == message.id,
                str(r.emoji) in emojis,
                u.id != ctx.bot.user.id
            ])
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=30, check=check_reaction)
            except asyncio.TimeoutError:
                for emoji in emojis:
                    await message.clear_reaction(emoji)
                break
            for i, emoji in enumerate(emojis):
                if reaction.emoji == emoji:
                    await message.delete()
                    return i

    @commands.command()
    async def play(self, ctx: commands.Context, *, query):
        '''
        与えられたクエリから曲を検索してプレイリストに追加します
        '''
        if not ctx.vs.vc:
            await ctx.invoke(self.join)
        ytdl = YTDLDownloader(ctx)
        async with ctx.typing():
            songs = await ytdl.search(query)
        if not songs:
            return await ctx.send("曲が見つかりませんでした")
        elif len(songs) == 1:
            song = Song(songs[0], ctx)
        else:
            song = Song(songs[await self.song_select(songs, ctx)], ctx)
        await ctx.vs.queue.put(song)
        embed = song.to_embed()
        embed.set_author(name="New Song", icon_url=self.bot.user.avatar_url)
        await ctx.send("曲を追加しました", embed=embed)

    @commands.command()
    async def stop(self, ctx: commands.Context):
        '''
        曲の再生を止めプレイリストを空にします
        '''
        ctx.vs.queue.clear()
        if not ctx.vs.is_playing:
            ctx.vs.vc.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """
        曲をスキップさせます
        """

        if not ctx.vs.is_playing:
            return await ctx.send('何も再生していません')
        ctx.vs.skip()
        return await ctx.message.add_reaction('⏭')

    @commands.command(aliases=["playlist"])
    async def queue(self, ctx: commands.Context):
        """
        再生リストを表示します
        """
        paginator = ctx.vs.queue.to_paginator()
        if paginator:
            await paginator.paginate(ctx)
        else:
            await ctx.send("現在プレイリストに曲はありません")

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        """
        再生リストをシャッフルします
        """

        if len(ctx.vs.queue) == 0:
            return await ctx.send('プレイリストは空です')

        ctx.vs.queue.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def remove(self, ctx: commands.Context, index: int):
        """
        指定したインデックスの曲をプレイリストから削除します
        """

        if len(ctx.vs.queue) == 0:
            return await ctx.send('The playlist is empty.')

        ctx.vs.queue.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def loop(self, ctx: commands.Context):
        """
        現在再生中の曲をループします
        """

        if not ctx.vs.is_playing:
            return await ctx.send('何も再生していません')
        ctx.vs.loop = not ctx.vs.loop
        await ctx.message.add_reaction('✅')
        await ctx.send(f'ループを{"有" if ctx.vs.loop else "無"}効にしました')

    @commands.command()
    async def loop_queue(self, ctx: commands.Context):
        """
        プレイリスト内の曲目をループし続けます
        """

        if not ctx.vs.is_playing:
            return await ctx.send('何も再生していません')
        ctx.vs.loop_queue = not ctx.vs.loop_queue
        await ctx.message.add_reaction('✅')
        await ctx.send(f'ループを{"有" if ctx.vs.loop else "無"}効にしました')

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('ボイスチャンネルに参加していません')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('既に入室しています')


def setup(bot):
    bot.add_cog(Music(bot))
