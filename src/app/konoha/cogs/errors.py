import discord
from discord.ext import commands

import os
import asyncio
import glob
import json
import traceback
import secrets
from datetime import datetime, timedelta

import konoha
import konoha.models.crud2 as q
from konoha.core import config
from konoha.core import exceptions
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import DurationToSecondsConverter, ColorConverter
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Errors(commands.Cog):
    order = -1

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        try:
            logger.error(
                f"[{ctx.guild.name}@{ctx.guild.id}] [{ctx.author.name}@{ctx.author.id}] [{error.__class__.__name__}]"
            )
        except:
            logger.error(
                f"[DM] [{ctx.author.id}] [{error.__class__.__name__}]"
            )
        logger.error(str(error), exc_info=True)
        if hasattr(ctx, 'handled'):
            return
        if isinstance(error, commands.errors.CommandNotFound):
            return
        if isinstance(error, commands.errors.NoPrivateMessage):
            return await self.bot.send_error(
                ctx, "DM上で実行はできません",
                "このコマンドはサーバー上で実行してください"
            )
        if isinstance(error, exceptions.MissingPermissions):
            return await self.bot.send_error(
                ctx, "権限がありません",
                str(error)
            )
        if isinstance(error, exceptions.BotMissingPermissions):
            return await self.bot.send_error(
                ctx, "Botの権限が不足しています",
                str(error)
            )
        if isinstance(error, commands.errors.NotOwner):
            await self.bot.send_error(
                ctx, "権限がありません",
                "このコマンドはBot開発者のみ実行可能です"
            )
            raise error
        try:
            raise error
        except:
            logger.error('*' * 60)
            logger.error(str(error), exc_info=True)
            tb = traceback.format_exc()
            if len(tb) > 1800:
                tb = tb[-1800:]
                tb = "...\n" + tb
            id = secrets.token_hex(64)[:24]
            guild = ctx.guild.id if ctx.guild else None
            channel = ctx.channel.id if ctx.channel else None
            message = ctx.message.id
            user = ctx.author.id
            name = error.__class__.__name__
            command = str(ctx.command)
            detail = str(error)
            await q.Error.create(self.bot, id, guild, channel, user, message, command, name, detail, tb)
            return await self.bot.send_error(
                ctx, "不明なエラーが発生しました",
                (
                    "ボット開発者に以下のエラーIDをお知らせください\n\n"
                    f"`{id}`"
                )
            )


def setup(bot):
    bot.add_cog(Errors(bot))
