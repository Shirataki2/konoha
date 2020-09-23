import discord
from discord.ext import commands

import traceback
import secrets
import jaconv
import MeCab
from typing import List
from dataclasses import dataclass
from datetime import datetime, timedelta

from konoha.core import config
from konoha.core import exceptions
from konoha.extensions.utils.timer import Timer
from konoha.core.bot.base import BotBase
from konoha.core.bot.emoji import CustomEmoji
from konoha.core.log.logger import get_module_logger
import konoha.models.crud2 as q

logger = get_module_logger(__name__)


class Konoha(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=self.get_prefix, *args, **kwargs)
        self.timer = Timer()
        self.timer.start(self)
        self.custom_emojis = CustomEmoji(self)
        self.tagger = MeCab.Tagger()
        self.wakati = MeCab.Tagger('-Owakati')

    @property
    def tomorrow(self):
        h = datetime.today().hour
        update_hour = 19
        update_time = datetime.today().replace(
            hour=update_hour, minute=0, second=0, microsecond=0
        )
        if h < update_hour:
            return update_time
        else:
            return update_time + timedelta(days=1)

    async def on_ready(self):
        ev = await q.Timer.search(self, event='daily')
        if not ev:
            logger.debug('Create Daily Event')
            await self.timer.create_event('daily', self.tomorrow, None)
        await super().on_ready()

    async def send_notification(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0x0000ff
        )
        embed.set_author(name="Konoha Bot", icon_url=self.user.avatar_url)
        await ctx.send(embed=embed)

    async def send_warning(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0xfec714
        )
        embed.set_author(name="Konoha Bot - Warning", icon_url=self.user.avatar_url)
        await ctx.send(embed=embed)

    async def send_error(self, ctx: commands.Context, title: str, description: str = None):
        embed = discord.Embed(
            title=f'**{title}**', description=description, color=0xff0000
        )
        embed.set_author(name="エラーが発生しました", icon_url=self.user.avatar_url)
        if ctx.guild:
            guild = await q.Guild(self, ctx.guild.id).get(verbose=2)
            pf = config.prefix
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

    async def morph(self, text: str) -> List['Word']:
        def _morph():
            node = self.tagger.parseToNode(text)
            words: List[Word] = []
            while node:
                word = node.surface
                feats = node.feature.split(',')
                if word != '':
                    words.append(Word(
                        name=word,
                        yomi=jaconv.kata2hira(feats[-2]),
                        pos=feats[0],
                        subpos1=feats[1],
                        subpos2=feats[2],
                        subpos3=feats[3],
                    ))
                node = node.next
            return words
        return await self.loop.run_in_executor(None, _morph)


@dataclass
class Word:
    name: str
    yomi: str
    pos: str
    subpos1: str
    subpos2: str
    subpos3: str
