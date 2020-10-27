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
import wavelink
from datetime import datetime, timedelta
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
import aiohttp
logger = get_module_logger(__name__)


async def get_duration(coro, *args, **kwargs):
    start = perf_counter()
    ret = await coro(*args, **kwargs)
    end = perf_counter()
    return (end - start) * 1000, ret


class Test(commands.Cog):
    '''
    実験中の機能
    '''
    order = 100

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command(hidden=True)
    async def tmp(self, ctx: commands.Context):
        msg = await self.bot.wait_for(
            'message',
            check=lambda m: \
                m.channel.id == 756602618918469645 and
                m.author.id == 756592679160119386 and 
                m.embeds and
                m.embeds[0].fields
        )
        print(msg)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id == 756602618918469645 and message.attachments and len(message.attachments) >= 2:
            api_key = "ea4e09a2-733b-40d0-9af1-a3a3679c780f"
            async with self.bot.session.post(
                "https://api.deepai.org/api/fast-style-transfer", 
                data={
                    'content': message.attachments[0].url,
                    'style': message.attachments[1].url
                }, 
                headers={
                    "Api-Key": api_key,
                }
            ) as resp:
                data = await resp.json()
                await message.channel.send(data["output_url"])
            try:
                print(data)
            except KeyError:
                pass

def setup(bot):
    bot.add_cog(Test(bot))
