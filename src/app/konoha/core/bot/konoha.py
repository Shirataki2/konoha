import discord
from discord.ext import commands

from konoha.core.bot.base import BotBase
from konoha.core.log.logger import get_module_logger

logger = get_module_logger(__name__)
class Konoha(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=self.get_prefix, *args, **kwargs)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """The event triggered when an error is raised while invoking a command"""
        if isinstance(error, commands.MissingRequiredArgument):
            logger.info('Missing Required Argument Error')
            title = '🥺 引数が不足しています'
        elif isinstance(error, commands.CommandOnCooldown):
            logger.info('Missing a required argument')
            title = '🔥 クールダウン時間中です'
        elif isinstance(error, commands.BadArgument):
            logger.info(f'Bad Argument Error: {ctx.guild.id}')
            title = '😵 不正な引数です'
        elif isinstance(error, commands.MissingRequiredArgument):
            logger.info(f'Missing Argument Error: {ctx.guild.id}')
            title = '🥴 引数がありません'
        elif isinstance(error, commands.NotOwner):
            logger.warning(f'Not Owner Error: {ctx.guild.id}')
            title = '🚫 Botの開発者のみが実行可能なコマンドです'
        elif isinstance(error, commands.MissingPermissions):
            logger.warning(f'Permission Error: {ctx.guild.id}')
            title = '🚫 実行するための権限がありません'
        elif isinstance(error, commands.CommandNotFound):
            logger.info(f'Command Not Found Error: {ctx.guild.id}')
            return
        elif isinstance(error, discord.Forbidden):
            logger.info(f'403 Error: {ctx.guild.id}')
            title = '🚫 403: このリソースへのアクセスは許可されていません'
            return
        elif isinstance(error, commands.CommandInvokeError):
            logger.error('Invoke error')
            title = '⚠ エラーが発生しました'
            embed = discord.Embed(title=f'**{title}**', description=str(error.original),
                                  color=0xff0000)
            await ctx.send(embed=embed)
            raise error.original
        else:
            title = 'Unspecified error'
        try:
            pf = await self.get_prefix(ctx.message)
            embed = discord.Embed(title=f'**{title}**', description=str(error), color=0xff0000)
            embed.set_footer(text=f"{pf}help {ctx.command} で使用方法を調べることができます")
        finally:
            await ctx.send(embed=embed)
        # raise error
