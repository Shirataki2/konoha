import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, List

import konoha.models.crud2 as q
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

    async def mod_check(self, ctx: commands.Context, users: List[discord.Member]):
        can_mod_user = []
        bot_role = ctx.me.top_role
        src_role = ctx.author.top_role
        for user in users:
            if await self.bot.is_owner(user):
                continue
            tgt_role = user.top_role
            if tgt_role > bot_role:
                continue
            elif tgt_role > src_role and not await self.bot.is_owner(ctx.author):
                continue
            can_mod_user.append(user)
        return can_mod_user

    @commands.command()
    @checks.can_ban()
    async def ban(self, ctx: commands.Context, users: commands.Greedy[discord.Member], *, reason: Optional[str]):
        '''
        ユーザーをBANします
        '''
        users = await self.mod_check(ctx, users)
        if not users:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "BANを実行するには対象のユーザーを適切に指定する必要があります．\n\n" +
                "ユーザーが存在するか，対象ユーザーのロールがこのBotやあなたより低いかをもう一度ご確認ください"
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
    async def unban(self, ctx: commands.Context, users: commands.Greedy[discord.User], *, reason: Optional[str]):
        '''
        ユーザーのBANを解除します
        '''
        users = await self.mod_check(ctx, users)
        if users is None:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "BANしたユーザーをBANリストから取り消すには対象のユーザーを適切に指定する必要があります．\n\n" +
                "ユーザーが存在するか，対象ユーザーのロールがこのBotやあなたより低いかをもう一度ご確認ください"
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
        users = await self.mod_check(ctx, users)
        if users is None:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "Kickを実行するには対象のユーザーを適切に指定する必要があります．\n\n" +
                "ユーザーが存在するか，対象ユーザーのロールがこのBotやあなたより低いかをもう一度ご確認ください"
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

    @commands.command()
    @checks.can_ban()
    async def tempban(self, ctx: commands.Context, users: commands.Greedy[discord.Member], duration: DurationToSecondsConverter, *, reason: Optional[str]):
        '''
        ユーザーを指定した期間だけBANします
        '''
        users = await self.mod_check(ctx, users)
        if not users:
            return await self.bot.send_error(
                ctx, "ユーザーが指定されていません",
                "ユーザーを引数にとっていない，またはユーザーを特定する情報が不正です" +
                "BANを実行するには対象のユーザーを適切に指定する必要があります．\n\n" +
                "ユーザーが存在するか，対象ユーザーのロールがこのBotやあなたより低いかをもう一度ご確認ください"
            )
        embed = discord.Embed(title="以下のユーザーをBANします．よろしいですか？", color=0xff0000)
        print(duration)
        embed.description = " ".join(f"{user.mention}" for user in users)
        embed.add_field(
            name="理由", value=reason if reason else "無し", inline=False)
        embed.add_field(name="期間", value=duration["original"], inline=False)
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

            await self.bot.timer.create_event(
                'mod',
                datetime.utcnow() + timedelta(seconds=duration["seconds"]),
                {
                    'type': 'BAN',
                    'users': [user.id for user in users],
                    'channel': ctx.channel.id,
                    'guild': ctx.guild.id
                }
            )
        else:
            await ctx.send('BANをキャンセルしました')
            await msg.delete()

    @commands.Cog.listener()
    async def on_mod_completed(self, payload):
        payload = json.loads(payload)
        guild: discord.Guild = await self.bot.fetch_guild(payload['guild'])
        users = await asyncio.gather(*[self.bot.fetch_user(user) for user in payload['users']])
        if payload['type'] == 'BAN':
            coro = guild.unban
        await asyncio.gather(*[coro(user) for user in users])
        channel = await self.bot.fetch_channel(payload['channel'])
        await channel.send(
            ','.join(f"{user.mention}" for user in users) +
            f'の一時{payload["type"]}を解除しました'
        )


def setup(bot):
    bot.add_cog(Mod(bot))
