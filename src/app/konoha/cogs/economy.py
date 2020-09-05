import discord
from discord.ext import commands, tasks

import asyncio
import re
import io
import os
import aiohttp
import random
import secrets
import random
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Pattern

import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import ColorConverter, FontConverter
from konoha.core.utils import TextImageGenerator
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


supported_langs = [
    "DE", "EN-GB", "EN-US", "EN", "FR", "IT",
    "JA", "ES", "NL", "PL", "PT-PT", "PT-BR",
    "PT", "RU", "ZH"
]


class Economy(commands.Cog):
    '''
    疑似通貨(ゲームなどで使用)に関するコマンドです．通貨はサーバー間で共有されます
    '''
    order = 10

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    async def get_money(self, user: discord.Member):
        money = await q.Money(user.guild.id, user.id).get()
        if money:
            return money
        else:
            money = await q.Money.create(user.id, user.guild.id, amount=1000)
            return await money.get()

    async def get_money_by_id(self, guild_id, user_id):
        money = await q.Money(guild_id, user_id).get()
        if money:
            return money
        else:
            money = await q.Money.create(user_id, guild_id, amount=1000)
            return await money.get()

    async def update_money(self, user: discord.Member, diff: int, force=False):
        money = await self.get_money(user)
        if money.amount + diff < 0 and not force:
            return None
        else:
            await q.Money(user.guild.id, user.id).set(amount=money.amount + diff)

    async def update_money_by_id(self, guild_id, user_id, diff: int, force=False):
        money = await self.get_money_by_id(guild_id, user_id)
        if money.amount + diff < 0 and not force:
            return None
        else:
            await q.Money(guild_id, user_id).set(amount=money.amount + diff)

    @commands.command()
    @commands.guild_only()
    async def wallet(self, ctx: commands.Context):
        '''サーバー内疑似通貨の所持量を表示します．'''
        money = await self.get_money(ctx.author)
        await ctx.send(f"所持金\n💴 **{money.amount}**ペリカ")

    @commands.command()
    @commands.guild_only()
    async def daily(self, ctx: commands.Context):
        '''
        サーバー内疑似通貨のデイリーログインボーナスを貰えます．

        リアルマネーには換算されませんが沢山ログインして稼ごう！！

        朝4時にリセットです
        '''
        money = await self.get_money(ctx.author)
        if money.bonus and money.bonus > 0:
            return await ctx.send('今日はもうお金もらったでしょ！また明日の4時以降に試してね！')
        p = random.random()
        if p < .65:
            salary = random.randint(250, 350)
            prefix = ''
        elif p < .85:
            salary = random.randint(350, 500)
            prefix = '少し多めにボーナス！'
        elif p < .97:
            salary = random.randint(500, 1000)
            prefix = 'かなり運がいいぞ！'
        else:
            salary = random.randint(1000, 3000)
            prefix = '超大当たり！'
        await ctx.send(f'{prefix}{salary}ペリカGET!\n所持金💴 **{money.amount+salary}**ペリカ')
        await self.update_money(ctx.author, salary)
        await q.Money(ctx.guild.id, ctx.author.id).set(bonus=1)

    @commands.Cog.listener()
    async def on_daily_completed(self, payload):
        await q.Money.reset()
        await self.bot.timer.create_event('daily', self.bot.tomorrow, None)


def setup(bot):
    bot.add_cog(Economy(bot))
