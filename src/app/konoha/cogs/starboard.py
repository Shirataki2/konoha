import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
import re
from functools import partial
from pybooru import Danbooru

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.commands import checks
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Starboard(commands.Cog):
    '''
    ⭐のリアクションが付いたメッセージを保管する機能
    '''
    order = 15

    star_color = 0xe7f214

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    def _create_embed(self, message: discord.Message):
        if message.embeds:
            embed = message.embeds.pop(0)
            embed.color = self.star_color
        else:
            embed = discord.Embed(color=self.star_color)
            embed.description = message.content
        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url)
        embed.set_footer(
            text=f'{message.guild.name} - {message.channel.name} at {message.created_at.strftime("%Y/%m/%d %H:%M:%S")}',
            icon_url=message.guild.icon_url
        )
        return embed

    @commands.group()
    @checks.can_manage_guild()
    @commands.guild_only()
    async def starboard(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}starboard enable #starboard`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            sbc = await q.StarboardConfig(self.bot, ctx.guild.id).get()
            if sbc:
                expand = '有効' if sbc.enabled else '無効'
                await ctx.send(f'スターボード機能は**{expand}**です')
            else:
                await ctx.send(f'スターボード機能は**未設定**です')
            await ctx.send_help("starboard")

    @starboard.command()
    async def enable(self, ctx: commands.Context, channel: discord.TextChannel, threshold: int = 1):
        '''
        スターボード機能を有効化します．`threshold`件以上の⭐のリアクションが付けられたメッセージを`channel`に別途投稿します
        '''
        sbc = await q.StarboardConfig(self.bot, ctx.guild.id).get()
        if sbc:
            await q.StarboardConfig(self.bot, ctx.guild.id).set(channel=channel.id, require=threshold, enabled=True)
        else:
            await q.StarboardConfig.create(self.bot, ctx.guild.id, channel=channel.id, require=threshold, enabled=True)
        embed = discord.Embed(color=self.star_color)
        embed.add_field(name='投稿先', value=channel.mention)
        embed.add_field(name='要求する⭐の数', value=str(threshold))
        await ctx.send(f'スターボード機能を**有効化**しました', embed=embed)

    @starboard.command()
    async def disable(self, ctx: commands.Context):
        '''
        スターボード機能を無効化します．
        '''
        sbc = await q.StarboardConfig(self.bot, ctx.guild.id).get()
        if sbc:
            await q.StarboardConfig(self.bot, ctx.guild.id).set(enabled=False)
        else:
            return await ctx.send(f'スターボード機能は**未設定**です')
        await ctx.send(f'スターボード機能を**無効化**しました')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.emoji.name != '⭐':
            return
        sbc = await q.StarboardConfig(self.bot, str(payload.guild_id)).get()
        if sbc is None or not sbc.enabled:
            return
        sb = await q.Starboard(self.bot, payload.message_id).get()
        guild = self.bot.get_guild(payload.guild_id)
        channel = await self.bot.fetch_channel(int(sbc.channel))
        msg_channel = await self.bot.fetch_channel(payload.channel_id)
        message: discord.Message = await msg_channel.fetch_message(payload.message_id)
        star: discord.Reaction = discord.utils.get(
            message.reactions, emoji='⭐')
        if star.count < sbc.require:
            return
        if sb:
            board_message = await channel.fetch_message(int(sb.board_message))
            await board_message.edit(content=f'⭐ **{star.count}**')
        else:
            msg = await channel.send(f'⭐ **{star.count}**', embed=self._create_embed(message))
            await q.Starboard.create(self.bot, payload.guild_id, payload.channel_id, payload.message_id, payload.user_id, msg.id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.emoji.name != '⭐':
            return
        sbc = await q.StarboardConfig(self.bot, str(payload.guild_id)).get()
        if sbc is None or not sbc.enabled:
            return
        sb = await q.Starboard(self.bot, payload.message_id).get()
        guild = self.bot.get_guild(payload.guild_id)
        channel = await self.bot.fetch_channel(int(sbc.channel))
        msg_channel = await self.bot.fetch_channel(payload.channel_id)
        message: discord.Message = await msg_channel.fetch_message(payload.message_id)
        star: discord.Reaction = discord.utils.get(
            message.reactions, emoji='⭐')
        if sb:
            print(star)
            board_message = await channel.fetch_message(int(sb.board_message))
            if star is None or star.count < sbc.require:
                await board_message.delete()
                await q.Starboard(self.bot, payload.message_id).delete()
            else:
                await board_message.edit(content=f'⭐ **{star.count}**')


def setup(bot):
    bot.add_cog(Starboard(bot))
