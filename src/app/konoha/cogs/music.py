import discord
from discord.ext import commands, tasks, menus

import asyncio
import aiohttp
import secrets
import copy
import wavelink
import os
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.commands import checks
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
from konoha.core.utils.pagination import EmbedPaginator
from konoha.extensions.voice_client import ExtendedVoiceClient

logger = get_module_logger(__name__)


class NoChannelProvidedException(commands.CommandError):
    pass


class InvalidChannelException(commands.CommandError):
    pass


class Track(wavelink.Track):
    __slot__ = ('requester',)

    def __init__(self, *args, **kwargs):
        self.requester = kwargs.pop('requester', None)
        super().__init__(*args, **kwargs)


class Queue(asyncio.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_paginator(self):
        paginator = EmbedPaginator(
            title="再生リスト", color=config.theme_color, footer="Page $p / $P")
        paginator.new_page()
        if self.qsize() == 0:
            return None
        for i, track in enumerate(self._queue.__iter__()):
            track: Track
            paginator.add_row(
                f"[{i+1}] {track.title}", f"Requested by {track.requester.mention}\n[元動画はこちら！]({track.uri})")
        return paginator


class PlayerController(menus.Menu):
    def __init__(self, *, embed: discord.Embed, player: 'Player'):
        super().__init__(timeout=None)
        self.embed = embed
        self.player = player

    def update_context(self, payload: discord.RawReactionActionEvent):
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member
        return ctx

    def reaction_check(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False
        if not payload.member:
            return False
        if payload.member.bot or payload.message_id != self.message.id:
            return False
        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.embed)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}')
    async def resume_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('resume')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{DOUBLE VERTICAL BAR}')
    async def pause_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('pause')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{BLACK SQUARE FOR STOP}')
    async def stop_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('stop')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def skip_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('skip')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{TWISTED RIGHTWARDS ARROWS}')
    async def shuffle_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('shuffle')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS WITH CIRCLED ONE OVERLAY}')
    async def repeat_single_track_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('loop_single_track')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}')
    async def repeat_queue_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('loop')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{HEAVY PLUS SIGN}')
    async def volume_up_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('volup')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)

    @menus.button('\N{HEAVY MINUS SIGN}')
    async def volume_down_command(self, payload: discord.RawReactionActionEvent):
        ctx = self.update_context(payload)
        command = self.bot.get_command('voldown')
        ctx.command = command
        channel = ctx.bot.get_channel(int(payload.channel_id))
        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        await self.bot.invoke(ctx)


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        self.context: commands.Context = kwargs.pop('context', None)
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        self.waiting = False
        self.updating = False
        self.next = None
        self.loop_single_track = False
        self.loop = False

    async def play_next(self):
        if self.loop and self.next:
            await self.queue.put(self.next)
        if self.is_playing or self.waiting:
            return
        try:
            if self.loop_single_track:
                track = self.next
            else:
                track = await asyncio.wait_for(
                    self.queue.get(), 180,
                    loop=self.context.bot.loop
                )
        except asyncio.TimeoutError:
            return await self.teardown()
        await self.play(track)
        self.next = track
        self.waiting = False
        await self.invoke_controller()

    async def invoke_controller(self):
        if self.updating:
            return
        self.updating = True
        if not hasattr(self, 'controller'):
            self.controller = PlayerController(
                embed=self._build_embed(), player=self)
            await self.controller.start(self.context)
        elif not await self._is_fresh_position():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass
            self.controller.stop()
            self.controller = PlayerController(
                embed=self._build_embed(), player=self)
            await self.controller.start(self.context)
        else:
            embed = self._build_embed()
            await self.controller.message.edit(embed=embed)
        self.updating = False

    def _build_embed(self):
        track: Track = self.current
        if not track:
            return
        channel = self.bot.get_channel(int(self.channel_id))
        embed = discord.Embed(
            title=f'Music Controller | {channel.name}', color=config.theme_color)
        embed.description = f'Now Playing...\n```\n{track.title}\n```\n'
        embed.set_image(url=track.thumb)
        embed.add_field(name='Duration', value=str(
            timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Volume', value=f'**`{self.volume} %`**')
        embed.add_field(name='Requester', value=track.requester.mention)
        embed.add_field(name='動画URL', value=f'[元動画にアクセス！]({track.uri})')
        embed.add_field(name='ループ', value='ON' if self.loop else 'OFF')
        embed.add_field(
            name='1曲ループ', value='ON' if self.loop_single_track else 'OFF')
        return embed

    async def _is_fresh_position(self):
        try:
            async for msg in self.context.channel.history(limit=3):
                if msg.id == self.controller.message.id:
                    return True
        except (AttributeError, discord.HTTPException):
            return False
        return False

    async def teardown(self):
        try:
            await self.controller.message.delete()
        except discord.HTTPException:
            pass
        self.controller.stop()
        try:
            await self.destroy()
        except KeyError:
            pass


class Music(commands.Cog, wavelink.WavelinkMixin):
    """
    音楽の再生を行います
    """
    order = 4

    URL_REG = re.compile(r'https?://(?:www\.)?.+')

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        if not hasattr(self, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        if self.bot.wavelink.nodes:
            prev = self.bot.wavelink.nodes.copy()
            for node in prev.values():
                await node.destroy()
        nodes = [
            {
                'host': 'lavalink',
                'port': 22222,
                'rest_uri': 'http://lavalink:22222',
                'password': config.lava_password,
                'identifier': 'MAIN',
                'region': 'japan'
            },
        ]
        await asyncio.gather(*[
            self.bot.wavelink.initiate_node(**node) for node in nodes
        ], loop=self.bot.loop)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        logger.debug(f'Wavelink Node {node.identifier} ... 準備完了')

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node, payload):
        await payload.player.play_next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        player: Player = self.bot.wavelink.get_player(
            member.guild.id, cls=Player)
        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

    async def cog_command_error(self, ctx, error):
        if isinstance(error, NoChannelProvidedException):
            ctx.handled = True
            return await self.bot.send_error(
                ctx, 'どこで再生すればいいかわかりません！',
                '先にボイスチャンネルに入室するか，接続先のボイスチャンネルを指定する必要があります！'
            )
        if isinstance(error, discord.NotFound):
            ctx.handled = True
            return

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx)
        if player.context and player.context.channel != ctx.channel:
            ctx.handled = True
            await self.send_error(
                ctx, '呼び出したチャンネル以外から音楽を操作することはできません！'
                f'音楽を操作するには呼び出したチャンネル({player.context.channel.mention})にてコマンドを呼び出してください'
            )
            raise InvalidChannelException
        try:
            channel = self.bot.get_channel(int(player.channel_id))
        except TypeError:
            channel = None

        if any([
            ctx.command.name == 'connect' and not player.context,
            not player.channel_id,
            not channel
        ]):
            return
        if player.is_connected and ctx.author not in channel.members:
            await self.send_error(
                ctx, 'ボイスチャンネル未入室状態で音楽を操作することはできません！'
                f'音楽を操作するにはボイスチャンネル {channel.name} に入室してください'
            )
            raise InvalidChannelException

    @commands.command(aliases=['join'])
    async def connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        '''
        あなたが接続してるボイスチャンネルに参加します

        引数にボイスチャンネルを指定した場合はそちらに参加します
        '''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx)
        if player.is_connected:
            return await ctx.send('既に接続済みです')
        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            raise NoChannelProvidedException
        await player.connect(channel.id)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        '''
        URLや曲名から検索し曲をプレイリストに追加し，再生します
        '''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            await ctx.invoke(self.connect)
        if not self.URL_REG.match(query):
            query = f'ytsearch:{query}'
        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
            return await ctx.send('検索しましたが，指定の曲を見つけることができませんでした', delete_after=10)
        if isinstance(tracks, wavelink.TrackPlaylist):
            await ctx.send(embed=self._playlist_to_embed(tracks), delete_after=15)
            for track in tracks.tracks:
                track = Track(track.id, track.info, requester=ctx.author)
                await ctx.send(embed=self._song_to_embed(player, track), delete_after=15)
                await player.queue.put(track)
        else:
            track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
            await ctx.send(embed=self._song_to_embed(player, track), delete_after=15)
            await player.queue.put(track)
        if not player.is_playing:
            await player.play_next()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        '''再生中の曲を一時停止します'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if player.is_paused or not player.is_connected:
            return
        try:
            await ctx.message.add_reaction('\N{DOUBLE VERTICAL BAR}')
        except:
            pass
        await player.set_pause(True)
        await asyncio.sleep(3)
        try:
            await ctx.message.remove_reaction('\N{DOUBLE VERTICAL BAR}', self.bot.user)
        except:
            pass

    @commands.command()
    async def resume(self, ctx: commands.Context):
        '''一時停止中の曲を再度再生します'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_paused or not player.is_connected:
            return
        try:
            await ctx.message.add_reaction('\N{BLACK RIGHT-POINTING TRIANGLE}')
        except:
            pass
        await player.set_pause(False)
        await asyncio.sleep(3)
        try:
            await ctx.message.remove_reaction('\N{BLACK RIGHT-POINTING TRIANGLE}', self.bot.user)
        except:
            pass

    @commands.command()
    async def skip(self, ctx: commands.Context):
        '''再生中の曲を飛ばし，次の曲を再生します'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        try:
            await ctx.message.add_reaction('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
        except:
            pass
        await player.stop()
        await asyncio.sleep(3)
        try:
            await ctx.message.remove_reaction('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.bot.user)
        except:
            pass

    @commands.command()
    async def stop(self, ctx: commands.Context):
        '''再生を停止し，Botをボイスチャンネルから退出させます'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        try:
            await ctx.message.add_reaction('\N{BLACK SQUARE FOR STOP}')
        except:
            pass
        await player.teardown()
        await asyncio.sleep(3)
        try:
            await ctx.message.remove_reaction('\N{BLACK SQUARE FOR STOP}', self.bot.user)
        except:
            pass

    @commands.command()
    async def loop(self, ctx: commands.Context):
        '''プレイリスト中の曲を連続再生します'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        player.loop = not player.loop
        await player.invoke_controller()

    @commands.command()
    async def loop_single_track(self, ctx: commands.Context):
        '''再生中の曲のみをループさせます'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        player.loop_single_track = not player.loop_single_track
        await player.invoke_controller()

    @commands.command()
    async def remove(self, ctx: commands.Context, index: int):
        '''プレイリストの番号を指定し，その曲をプレイリストから削除させます'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        index -= 1
        qsize = player.queue.qsize()
        if not 0 <= index < qsize:
            return await ctx.send('指定した番号の曲はまだ追加されていません')
        track = player.queue._queue[index]
        del player.queue._queue[index]
        embed = self._song_to_embed(player, track)
        embed.title = '曲を削除しました'
        embed.color = 0xff0000
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(aliases=["vol"])
    async def volume(self, ctx: commands.Context, *, vol: int):
        '''曲のボリュームを0-100 (%)に変更させます'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        if not 0 <= vol <= 100:
            return await ctx.send('音量は**0から100**(%)の間で指定してください')
        await player.set_volume(vol)
        await player.invoke_controller()
        return await ctx.send(f'音量を**{vol}%**に設定しました', delete_after=5)

    @commands.command(hidden=True)
    async def volup(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        vol = player.volume + 10
        if vol > 100:
            return await ctx.send('最大音量に達しました', delete_after=5)
        await player.set_volume(vol)
        await player.invoke_controller()
        return await ctx.send(f'音量を**{vol}%**に設定しました', delete_after=5)

    @commands.command(hidden=True)
    async def voldown(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        vol = player.volume - 10
        if vol < 0:
            return await ctx.send('既に音量は最小です', delete_after=5)
        await player.set_volume(vol)
        await player.invoke_controller()
        return await ctx.send(f'音量を**{vol}%**に設定しました', delete_after=5)

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        '''プレイリスト中の曲をシャッフルします'''
        player: Player = self.bot.wavelink.get_player(
            ctx.guild.id, cls=Player, context=ctx
        )
        if not player.is_connected:
            return
        if player.queue.qsize() < 1:
            return await ctx.send('プレイリストに曲がありません')
        await ctx.message.add_reaction('\N{TWISTED RIGHTWARDS ARROWS}')
        random.shuffle(player.queue._queue)
        await asyncio.sleep(3)
        await ctx.message.remove_reaction('\N{TWISTED RIGHTWARDS ARROWS}', self.bot.user)

    @commands.command(aliases=['eq'])
    async def equalizer(self, ctx: commands.Context, *, equalizer: str):
        '''イコライザを設定します． (対応イコライザ: Flat, Boost, Metal, Piano)'''
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx)
        if not player.is_connected:
            return
        eqs = {'flat': wavelink.Equalizer.flat(),
               'boost': wavelink.Equalizer.boost(),
               'metal': wavelink.Equalizer.metal(),
               'piano': wavelink.Equalizer.piano()}
        eq = eqs.get(equalizer.lower(), None)
        if not eq:
            joined = ", ".join(eqs.keys())
            return await ctx.send(f'イコライザーは以下の形式のみサポートしています\n\n**{joined}**')
        await ctx.send(f'イコライザーを設定しました: **{equalizer}**', delete_after=15)
        await player.set_eq(eq)

    @commands.command(aliases=["queue"])
    async def playlist(self, ctx: commands.Context):
        '''プレイリストを表示します'''
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx)
        if not player.is_connected:
            return
        await player.queue.to_paginator().paginate(ctx)

    def _song_to_embed(self, player, track: Track):
        embed = discord.Embed(title='曲を追加しました', color=config.theme_color)
        embed.description = f'```\n{track.title}\n```\n'
        embed.set_thumbnail(url=track.thumb)
        embed.add_field(name='Duration', value=str(
            timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Requester', value=track.requester.mention)
        embed.add_field(name='動画URL', value=f'[元動画にアクセス！]({track.uri})')
        return embed

    def _playlist_to_embed(self, tracks: wavelink.TrackPlaylist):
        embed = discord.Embed(title='プレイリストを追加しました', color=config.theme_color)
        embed.description = f'```\n{tracks.data["playlistInfo"]["name"]}\n```\n'
        embed.add_field(name='総曲数', value=f'**`{len(tracks.tracks)}`**')
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
