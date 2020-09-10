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
    '''
    メッセージの操作に関するコマンド
    '''
    order = 14

    message_url = re.compile(
        'https://(?:ptb.|canary.)?discord(?:app)?\.com' +
        '/channels/(?P<guild>\d{18})/(?P<channel>\d{18})/(?P<message>\d{18})/?'
    )

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    def _build_embed(self, url, message: discord.Message):
        embed = discord.Embed(color=0x4060e3)
        embed.set_author(name=f'Message from {message.author.display_name}',
                         icon_url=message.author.avatar_url)
        embed.description = message.content
        embed.add_field(name=f'at #{message.channel.name}',
                        value=f'[元の投稿へ]({url})')
        if len(message.attachments) < 2:
            embed.set_footer(text=f'{message.guild.name} - {message.created_at.strftime("%Y/%m/%d %H:%M:%S")}',
                             icon_url=message.guild.icon_url)
        else:
            embed.set_footer(text=f'{message.guild.name} - {message.created_at.strftime("%Y/%m/%d %H:%M:%S")}',
                             icon_url=message.guild.icon_url)

        return embed

    async def _arg_check(self, ctx, num):
        if num > 1000:
            await self.bot.send_error(
                ctx, '一度に消せるメッセージの数は最大1000件です！',
                '消すメッセージの数は1000以下で指定してください'
            )
        elif num < 1:
            await self.bot.send_error(
                ctx, '引数が不正です！',
                '消すメッセージの数は1以上の整数で指定してください'
            )
        else:
            return True
        return False

    async def _delete_messages(self, ctx, num, check):
        with ctx.typing():
            while num > 0:
                await ctx.channel.purge(
                    limit=min(100, num),
                    check=check
                )
                num -= 100
        await asyncio.sleep(3)
        msg = await ctx.send('完了しました')
        await asyncio.sleep(3)
        await msg.delete()

    @commands.group()
    @commands.guild_only()
    async def expand(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}expand on`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            guild = await q.Guild(self.bot, ctx.guild.id).get()
            if guild:
                expand = '有効' if guild.expand else '無効'
                await ctx.send(f'メッセージ展開機能は**{expand}**です')
            await ctx.send_help("expand")

    @expand.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    async def on(self, ctx: commands.Context):
        '''
        メッセージリンク添付時の展開機能をオンにします
        '''
        await q.Guild(self.bot, ctx.guild.id).set(expand=True)
        await ctx.send('メッセージ展開機能を**有効**にしました')

    @expand.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    async def off(self, ctx: commands.Context):
        '''
        メッセージリンク添付時の展開機能をオフにします
        '''
        await q.Guild(self.bot, ctx.guild.id).set(expand=False)
        await ctx.send('メッセージ展開機能を**無効**にしました')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        guild = await q.Guild(self.bot, message.guild.id).get()
        if not guild.expand:
            return
        print(self.message_url.match(message.content))
        for url in re.finditer(self.message_url, message.content):
            if int(url['guild']) != message.guild.id:
                return
            channel = message.guild.get_channel(int(url['channel']))
            fetched_message = await channel.fetch_message(int(url['message']))
            if fetched_message.content:
                embed = self._build_embed(url.group(0), fetched_message)
                await message.channel.send(embed=embed)
            for embed in fetched_message.embeds:
                await message.channel.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.can_manage_messages()
    @checks.bot_can_manage_messages()
    async def purge(self, ctx: commands.Context, num: int):
        '''
        指定した件数のメッセージを一括で消去します

        Discord APIの仕様上2週間以上前のメッセージを消すことはできません
        '''
        if num > 1000:
            return await self.bot.send_error(
                ctx, '一度に消せるメッセージの数は最大1000件です！',
                '消すメッセージの数は1000以下で指定してください'
            )
        if num < 1:
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                '消すメッセージの数は1以上の整数で指定してください'
            )
        if ctx.invoked_subcommand is None:
            if await self._arg_check(ctx, num):
                await self._delete_messages(ctx, num, lambda m: True)

    @purge.command(name='bot')
    async def _bot(self, ctx: commands.Context, num: int):
        '''
        指定した件数のメッセージのうちから，ボットからのメッセージを一括で消去します

        Discord APIの仕様上2週間以上前のメッセージを消すことはできません
        '''
        if await self._arg_check(ctx, num):
            await self._delete_messages(ctx, num, lambda m: m.author.bot)

    @purge.command(name='user')
    async def _user(self, ctx: commands.Context, num: int):
        '''
        指定した件数のメッセージのうちから，非ボットユーザーからのメッセージを一括で消去します

        Discord APIの仕様上2週間以上前のメッセージを消すことはできません
        '''
        if await self._arg_check(ctx, num):
            await self._delete_messages(ctx, num, lambda m: not m.author.bot)


def setup(bot):
    bot.add_cog(Messages(bot))
