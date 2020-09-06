import discord
from discord.ext import commands

import asyncio
import os
import glob
from aiomysql.sa import create_engine
from aiohttp import ClientSession
from typing import List

import konoha
import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.commands.help import CustomHelpCommand
from konoha.core.log.logger import get_module_logger

logger = get_module_logger(__name__)


class BotBase(commands.Bot):
    def __init__(self, *args, **kwargs):
        super(BotBase, self).__init__(
            help_command=CustomHelpCommand(), *args, **kwargs)
        self.loop.slow_callback_duration = 0.02
        self.get_all_cogs()

    @property
    def session(self) -> ClientSession:
        if not hasattr(self, '_sess'):
            self._sess = ClientSession(loop=self.loop)
        return self._sess

    @property
    async def pool(self):
        if not hasattr(self, '_pool'):
            self._pool = await create_engine(
                user=config.db_user,
                db=config.db_name,
                host=config.db_host,
                password=config.db_password,
                charset='utf8',
                autocommit=True,
                loop=self.loop
            )
        return self._pool

    async def execute(self, query, verbose=1, *args, **kwargs):
        logger.debug("DB接続開始")
        s = str(query)
        for l in s.split("\n"):
            logger.debug(f"\t{l}")
        async with (await self.pool).acquire() as conn:
            result = await conn.execute(query)
        logger.debug("DB接続終了")
        return result

    async def on_ready(self):
        logger.info("Ready.")
        logger.info("Bot Name : %s", self.user)
        logger.info("Bot  ID  : %s", self.user.id)
        logger.info("Version  : %s", konoha.__version__)
        await self.change_presence(status=discord.Status.online)
        await self.change_presence(activity=discord.Game(name=f"{config.prefix}help"))

    async def get_prefix(self, message: discord.Message):
        if message.guild:
            return commands.when_mentioned_or(config.prefix)(self, message)
        else:
            return ['']

    async def set_prefix(self, message: discord.Message, prefix: str):
        await q.Guild(self, guild_id=message.guild.id).set(prefix=prefix)

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"ギルド加入: {guild.name}({guild.id})")
        await q.Guild.create(self, guild.id)

    async def on_guild_remove(self, guild: discord.Guild):
        logger.info(f"ギルド退出: {guild.name}({guild.id})")
        await q.Guild(self, guild_id=guild.id).delete()

    def get_all_cogs(self, reload=False):
        dirname = os.path.dirname(os.path.abspath(__file__))
        cogs = glob.glob(f'{dirname}/../../cogs/**.py')
        logger.debug(f"Cogを{'再' if reload else ''}読込中...")
        for cog in cogs:
            cogname = os.path.basename(os.path.splitext(cog)[0])
            if cogname[:2] == "__":
                continue
            modulename = f'konoha.cogs.{cogname}'
            try:
                if reload:
                    self.reload_extension(modulename)
                else:
                    self.load_extension(modulename)
                logger.debug(f'\t{modulename} ... 成功')
            except Exception as e:
                logger.error(f'\t{modulename} ... 失敗')
                raise e

    def run(self, *args, **kwargs):
        try:
            self.loop.run_until_complete(self.start(config.bot_token))
        except discord.LoginFailure:
            logger.critical("Discord Tokenが不正です")
        except KeyboardInterrupt:
            logger.error("Keyboard Interrupt")
        except:
            logger.critical("不明なエラーが発生しました", exc_info=True)
        finally:
            logger.info("Botを終了中です...")
            self.loop.run_until_complete(self.logout())
            logger.debug("\tログアウト完了")
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
                logger.debug(f"\tTask: {task.get_name()}をキャンセルしました")
            try:
                self.loop.run_until_complete(
                    asyncio.gather(*asyncio.all_tasks(self.loop)))
            except asyncio.CancelledError:
                logger.debug("すべてのタスクをキャンセルしました")
            finally:
                self.loop.run_until_complete(self.session.close())
                logger.info("Bye")
