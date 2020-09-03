import discord
from discord.ext import commands

import traceback
import secrets

from konoha.core import config
from konoha.extensions.utils.timer import Timer
from konoha.core.bot.base import BotBase
from konoha.core.bot.emoji import CustomEmoji
from konoha.core.log.logger import get_module_logger
import konoha.models.crud as q

logger = get_module_logger(__name__)


class Konoha(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=self.get_prefix, *args, **kwargs)
        self.timer = Timer()
        self.timer.start(self)
        self.custom_emojis = CustomEmoji(self)

    async def send_notification(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0x0000ff
        )
        embed.set_author(name="Konoha Bot", icon_url=self.user.avatar_url)
        await ctx.send(embed=embed)

    async def send_error(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0xff0000
        )
        embed.set_author(name="エラーが発生しました", icon_url=self.user.avatar_url)
        if ctx.guild:
            guild = await q.Guild(ctx.guild.id).get(verbose=2)
            pf = guild.prefix
        else:
            pf = ""
        embed.set_footer(
            text=f"{pf}help {ctx.command} で使用方法を調べることができます")
        await ctx.send(embed=embed)

    async def send_cooldown_error(self, ctx: commands.Context, error: Exception, rate=2, per=1):
        try:
            sec = float(str(error).split("Try again in ")[-1][:-1])
        except:
            sec = 0
        if sec > 0:
            return await self.send_error(
                ctx, "実行回数制限を超過しています！",
                f"このコマンドは`{per}`分間に`{rate}`度以上呼び出すことはできません\n\n{int(sec)}秒後に再度お試しください．"
            )
        else:
            return await self.send_error(
                ctx, "実行回数制限を超過しています！",
                f"このコマンドは`{per}`分間に`{rate}`度以上呼び出すことはできません"
            )

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
        logger.error(str(error), exc_info=True)
        if hasattr(ctx, 'handled'):
            return
        if isinstance(error, commands.errors.CommandNotFound):
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
            await q.Error.create(id, guild, channel, user, message, command, name, detail, tb)
            return await self.send_error(
                ctx, "不明なエラーが発生しました",
                (
                    "ボット開発者に以下のエラーIDをお知らせください\n\n"
                    f"`{id}`"
                )
            )
