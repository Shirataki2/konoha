import discord
from discord.ext import commands

import traceback
import secrets

from konoha.core.bot.base import BotBase
from konoha.core.log.logger import get_module_logger
import konoha.models.crud as q

logger = get_module_logger(__name__)


class Konoha(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=self.get_prefix, *args, **kwargs)

    async def send_error(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0xff0000
        )
        if ctx.guild:
            guild = await q.Guild(ctx.guild.id).get(verbose=0)
            pf = guild.prefix
        else:
            pf = ""
        embed.set_footer(
            text=f"{pf}help {ctx.command} で使用方法を調べることができます")
        await ctx.send(embed=embed)

    async def on_command(self, ctx: commands.Context):
        logger.debug("== [コマンド実行] ==")
        if ctx.guild:
            logger.debug(
                f"[{ctx.guild.name}@{ctx.guild.id}] [{ctx.author.name}@{ctx.author.id}]"
            )
        else:
            logger.debug(
                f"[DM] [{ctx.author.name}@{ctx.author.id}]"
            )
        logger.debug(f"{ctx.message.content}")
        logger.debug("===================")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        try:
            logger.error(
                f"[{ctx.guild.name}@{ctx.guild.id}] [{ctx.author.name}@{ctx.author.id}] [{error.__class__.__name__}]"
            )
        except:
            logger.error(
                f"[DM] [{ctx.author.id}] [{error.__class__.__name__}]"
            )
        logger.error(str(error))
        if hasattr(ctx, 'handled'):
            return
        if isinstance(error, commands.errors.NoPrivateMessage):
            return await self.send_error(
                ctx, "DM上で実行はできません",
                "このコマンドはサーバー上で実行してください"
            )
        if isinstance(error, commands.errors.NotOwner):
            await self.send_error(
                ctx, "権限がありません",
                "このコマンドはBot開発者のみ実行可能です"
            )
            raise error
        try:
            raise error
        except:
            tb = traceback.format_exc()
            if len(tb) > 1800:
                tb = tb[-1800:]
                tb = "...\n" + tb
            id = secrets.token_hex(64)[:24]
            guild = ctx.guild.id if ctx.guild else None
            channel = ctx.channel.id if ctx.channel else None
            user = ctx.author.id
            name = error.__class__.__name__
            command = str(ctx.command)
            detail = str(error)
            await q.Error.create(id, guild, channel, user, command, name, detail, tb)
            return await self.send_error(
                ctx, "不明なエラーが発生しました",
                (
                    "ボット開発者に以下のエラーIDをお知らせください\n\n"
                    f"`{id}`"
                )
            )
