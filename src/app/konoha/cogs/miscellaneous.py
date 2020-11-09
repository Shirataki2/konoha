import discord
from discord.ext import commands

import re
import os
import asyncio
import subprocess
import tabulate
import aiomysql
import glob
import json
from datetime import datetime, timedelta
from unicodedata import east_asian_width
from itertools import cycle
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from pathlib import Path
from time import perf_counter

import konoha
import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import DurationToSecondsConverter, ColorConverter
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


async def get_duration(coro, *args, **kwargs):
    start = perf_counter()
    ret = await coro(*args, **kwargs)
    end = perf_counter()
    return (end - start) * 1000, ret


class Miscellaneous(commands.Cog):
    '''
    他のカテゴリに属さないちょっとした機能です
    '''
    order = 17

    deny_all = discord.AllowedMentions(
        everyone=False, users=False, roles=False)

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command()
    async def echo(self, ctx: commands.Context, *, body: str):
        '''
        オウム返しをします
        '''
        await ctx.send(body, allowed_mentions=self.deny_all)

    @commands.command()
    async def timer(self, ctx: commands.Context, duration: DurationToSecondsConverter):
        '''
        指定した秒数後にあなた宛てにメンションを送信します
        '''
        print(duration)
        if duration["seconds"] < 0:
            return await ctx.send("負の時間待たせるとはどういうことなのでしょう(哲学)")
        if duration["seconds"] < 0.1:
            return await ctx.send(f"無の時間のタイマーを設定しました! {ctx.author.mention}\n\n解釈できない文字列とか入れてませんか?")
        if duration["seconds"] > 60 * 60 * 24 * 365 * 3:
            return await ctx.send("あいにく3年より長くは待ってられません")
        await self.bot.timer.create_event(
            'timer',
            datetime.utcnow() + timedelta(seconds=duration["seconds"]),
            {
                "mention": str(ctx.author.mention),
                "channel": str(ctx.channel.id),
                "timer": duration
            }
        )
        await ctx.send(f"{duration['original']}のタイマーを設定しました")

    @commands.Cog.listener()
    async def on_timer_completed(self, payload):
        payload = json.loads(payload)
        channel = await self.bot.fetch_channel(payload['channel'])
        if channel:
            await channel.send(f'{payload["mention"]} {payload["timer"]["original"]}経過しました')


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
