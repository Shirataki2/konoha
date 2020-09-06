import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
import re
from functools import partial
from pybooru import Danbooru

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.commands import checks
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Messages(commands.Cog):
    order = 14

    message_url = re.compile(
        'https://(?:ptb.|canary.)?discord(?:app)?\.com' +
        '/channels/(?P<guild>\d{18})/(?P<channel>\d{18})/(?P<message>\d{18})/?'
    )

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    def _build_embed(self, message: discord.Message):
        embed = discord.Embed(color=0x4060e3)
        embed.set_author(name=f'Message from {message.author.display_name}',
                         icon_url=message.author.avatar_url)
        embed.description = message.content
        embed.set_footer(text=f'{message.guild.name} - {message.created_at.strftime("%Y/%m/%d %H:%M:%S")}',
                         icon_url=message.guild.icon_url)
        return embed

    @commands.group()
    @commands.guild_only()
    async def expand(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}expand on`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help("expand")

    @expand.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    async def on(self, ctx: commands.Context):
        '''
        メッセージリンク添付時の展開機能をオンにします
        '''
        await q.Guild(self.bot,ctx.guild.id).set(expand=True)
        await ctx.send('メッセージ展開機能を**有効**にしました')

    @expand.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    async def off(self, ctx: commands.Context):
        '''
        メッセージリンク添付時の展開機能をオフにします
        '''
        await q.Guild(self.bot,ctx.guild.id).set(expand=False)
        await ctx.send('メッセージ展開機能を**無効**にしました')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        guild = await q.Guild(self.bot,message.guild.id).get()
        if not guild.expand:
            return
        print(self.message_url.match(message.content))
        for url in re.finditer(self.message_url, message.content):
            print(url['guild'])
            if int(url['guild']) != message.guild.id:
                return
            channel = message.guild.get_channel(int(url['channel']))
            fetched_message = await channel.fetch_message(int(url['message']))
            print(fetched_message)
            if fetched_message.content or fetched_message.files:
                embed = self._build_embed(fetched_message)
                await channel.send(embed=embed)
            for embed in fetched_message.embeds:
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Messages(bot))
