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
    async def tmp(self, ctx: commands.Context, num: int):
        discord.VoiceChannel.connect()


def setup(bot):
    bot.add_cog(Test(bot))
