import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
from konoha.core.utils import user_reaction_check
from konoha.core.converters import DurationToSecondsConverter
logger = get_module_logger(__name__)


class Mod(commands.Cog):
    '''
    モデレーション用のコマンドです
    '''
    order = 6

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command()
    @checks.can_ban()
    async def ban(self, ctx: commands.Context, users: commands.Greedy[discord.Member], *, reason: Optional[str]):
        '''
        ユーザーをBANします
        '''
        if users is None:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "BANを実行するには対象のユーザーを適切に指定する必要があります．"
            )
        embed = discord.Embed(title="以下のユーザーをBANします．よろしいですか？", color=0xff0000)
        embed.description = " ".join(f"{user.mention}" for user in users)
        embed.add_field(name="理由", value=reason if reason else "無し")
        emojis = ("✅", "❌")
        msg: discord.Message = await ctx.send(embed=embed)
        await asyncio.gather(*[msg.add_reaction(emoji) for emoji in emojis])
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=user_reaction_check(msg, emojis, ctx), timeout=60)
        except:
            return await ctx.send('しばらく応答がないためBANをキャンセルしました')
        if reaction.emoji == emojis[0]:
            await asyncio.gather(*[ctx.guild.ban(user, reason=reason)
                                   for user in users])
            await msg.clear_reactions()
            await ctx.send('BANが完了しました')
        else:
            await ctx.send('BANをキャンセルしました')
            await msg.delete()

    @commands.command()
    @checks.can_ban()
    async def unban(self, ctx: commands.Context, users: commands.Greedy[discord.Member], *, reason: Optional[str]):
        '''
        ユーザーのBANを解除します
        '''
        if users is None:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "BANしたユーザーをBANリストから取り消すには対象のユーザーを適切に指定する必要があります．"
            )
        embed = discord.Embed(
            title="以下のユーザーをBANリストから削除します．よろしいですか？", color=0xff0000)
        embed.description = " ".join(f"{user.mention}" for user in users)
        embed.add_field(name="理由", value=reason if reason else "無し")
        emojis = ("✅", "❌")
        msg: discord.Message = await ctx.send(embed=embed)
        await asyncio.gather(*[msg.add_reaction(emoji) for emoji in emojis])
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=user_reaction_check(msg, emojis, ctx), timeout=60)
        except:
            return await ctx.send('しばらく応答がないためUNBANをキャンセルしました')
        if reaction.emoji == emojis[0]:
            await asyncio.gather(*[ctx.guild.unban(user, reason=reason)
                                   for user in users])
            await msg.clear_reactions()
            await ctx.send('BANリストからの削除が完了しました')
        else:
            await ctx.send('UNBANをキャンセルしました')
            await msg.delete()

    @commands.command()
    @checks.can_kick()
    async def kick(self, ctx: commands.Context, users: commands.Greedy[discord.Member], *, reason: Optional[str]):
        '''
        ユーザーをサーバーから追放します
        '''
        if users is None:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "Kickを実行するには対象のユーザーを適切に指定する必要があります．"
            )
        embed = discord.Embed(
            title="以下のユーザーをサーバーから追放します．よろしいですか？", color=0xff0000)
        embed.description = " ".join(f"{user.mention}" for user in users)
        embed.add_field(name="理由", value=reason if reason else "無し")
        emojis = ("✅", "❌")
        msg: discord.Message = await ctx.send(embed=embed)
        await asyncio.gather(*[msg.add_reaction(emoji) for emoji in emojis])
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=user_reaction_check(msg, emojis, ctx), timeout=60)
        except:
            return await ctx.send('しばらく応答がないためKickをキャンセルしました')
        if reaction.emoji == emojis[0]:
            await asyncio.gather(*[ctx.guild.kick(user, reason=reason)
                                   for user in users])
            await msg.clear_reactions()
            await ctx.send('Kickが完了しました')
        else:
            await ctx.send('Kickをキャンセルしました')
            await msg.delete()


def setup(bot):
    bot.add_cog(Mod(bot))
