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


class DebugLogging(commands.Cog):
    '''
    開発用の実行ログ
    '''
    order = -1
    log_channel = 754991343960326174

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        self._channel = None

    @property
    def channel(self):
        if self._channel is None:
            self._channel = self.bot.get_channel(self.log_channel)
        return self._channel


def setup(bot):
    bot.add_cog(DebugLogging(bot))
