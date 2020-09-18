import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class GlobalChat(commands.Cog):
    '''
    他のサーバーのメンバーと疑似的に会話ができるグローバルチャットに関するコマンドです．

    他のサーバーのユーザーからの通知には[ボット]と名前につきますが相手はボットではなくユーザーです
    '''
    order = 3

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.group()
    async def gc(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}gc register`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help("GlobalChat")

    @gc.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    @checks.bot_has_perms(manage_webhooks=True)
    async def register(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        '''
        指定したチャンネル(何も指定しない場合はコマンドを投稿したチャンネル)をグローバルチャット用チャンネルとして登録します

        チャンネルの指定方法は`#`と入力し，続いて表示されるサジェストから選択してください．

        (熟練者の方へ)チャンネルID等でも指定は可能です
        '''
        if channel is None:
            channel = ctx.channel
        guild = await q.Guild(self.bot, ctx.guild.id).get()
        if guild.gc_channel is None:
            hook = await channel.create_webhook(
                name="Global Chat"
            )
            await q.Guild(self.bot, ctx.guild.id).set(gc_url=hook.url, gc_channel=channel.id)
            await ctx.send(f"グローバルチャットの投稿先を{channel.mention}に設定しました")
        else:
            async with aiohttp.ClientSession() as session:
                hook = discord.Webhook.from_url(
                    guild.gc_url, adapter=discord.AsyncWebhookAdapter(session))
                newhook = await channel.create_webhook(
                    name="Global Chat"
                )
                await q.Guild(self.bot, ctx.guild.id).set(gc_channel=channel.id, gc_url=newhook.url)
                await ctx.send(f"グローバルチャットの投稿先{channel.mention}に変更しました")
                await hook.delete()

    @gc.command()
    @commands.guild_only()
    @checks.can_manage_guild()
    @checks.bot_has_perms(manage_webhooks=True)
    async def unregister(self, ctx: commands.Context):
        '''
        グローバルチャットの登録を解除します
        '''
        guild = await q.Guild(self.bot, ctx.guild.id).get()
        if guild.gc_channel is None:
            await ctx.send(f"グローバルチャットサービスはまだ利用していません")
        else:
            async with aiohttp.ClientSession() as session:
                hook = discord.Webhook.from_url(
                    guild.gc_url, adapter=discord.AsyncWebhookAdapter(session))
                await q.Guild(self.bot, ctx.guild.id).set(gc_channel=None, gc_url=None)
                await ctx.send(f"グローバルチャットサービスの利用を終了しました")
                await hook.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        guild = await q.Guild(self.bot, message.guild.id).get(verbose=2)
        if int(guild.gc_channel) != message.channel.id:
            return
        guilds = [
            g
            for g in await q.Guild.get_all(self.bot, verbose=2)
            if (int(g.id) != message.guild.id) and (g.gc_channel is not None)
        ]
        await asyncio.gather(*[
            send_global_message(g, message)
            for g in guilds
        ])
        await message.add_reaction("✅")
        await asyncio.sleep(3)
        try:
            await message.clear_reactions()
        except:
            pass


async def send_global_message(guild, message):
    async with aiohttp.ClientSession() as session:
        hook = discord.Webhook.from_url(
            guild.gc_url, adapter=discord.AsyncWebhookAdapter(session))
        await hook.send(
            message.content,
            username=message.author.name,
            avatar_url=message.author.avatar_url_as(format="png"),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=False, roles=False)
        )


def setup(bot):
    bot.add_cog(GlobalChat(bot))
