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
    グローバルチャットは他のサーバーのメンバーと疑似的に会話ができる機能です．

    他のサーバーのユーザーからの通知には[ボット]と名前につきますが相手はボットではなくユーザーです

    失礼な言動等を見かけた場合には`{prefix}gc report (ユーザー)`で通報してください
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

    @gc.command()
    async def report(self, ctx: commands.Context, user: discord.Member):
        '''
        グローバルチャットにて不審な行動を起こした方がいた際の通報機能です．

        通報の際は必ず理由を書くようにしてください．

        理由にはスクリーンショットのURL，メッセージのURL，メッセージIDを書くことで特定しやすくなります．
        '''
        if user is None:
            return await self.bot.send_error(
                ctx, "ユーザーが見つかりません",
                "名前や`@`付きでのメンション，またはIDなどのユーザーに関する情報を引数に与えてください"
            )
        await ctx.send(
            (
                "通報理由を教えてください:\n\n"
                "@\u200Beveryoneの連発,誹謗中傷 など\n```\n"
                "キャンセルの場合は cancel と送信してください\n\n"
                "スクリーンショットのURL，メッセージのURL，メッセージIDを書くことで特定しやすくなります．\n"
                "```"
            )
        )

        def user_check(message: discord.Message):
            return all([
                message.author == ctx.author
            ])
        try:
            message: discord.Message = await self.bot.wait_for("message", check=user_check, timeout=600)
        except asyncio.TimeoutError:
            return await ctx.send("メッセージの送信がしばらくないため受付を終了します")
        if message.content == "cancel":
            return await ctx.send("通報をキャンセルしました")
        embed = discord.Embed(title="通報内容の確認", color=0xffff00)
        embed.description = f"{user.mention} を以下の理由で通報します．\nよろしいですか？\n\n{message.content}"
        confirm_message: discord.Message = await ctx.send(embed=embed)

        def reaction_check(reaction: discord.Reaction, user: discord.Member):
            return all([
                reaction.emoji in ("✅", "❎"),
                ctx.author == user,
                reaction.message.id == confirm_message.id
            ])
        for emoji in ("✅", "❎"):
            await confirm_message.add_reaction(emoji)
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=reaction_check, timeout=600)
        except asyncio.TimeoutError:
            return await ctx.send("送信の確認がないため通報の受付を終了します")
        if reaction.emoji == "✅":
            channel: discord.Channel = await self.bot.fetch_channel(config.log_channel)
            embed = discord.Embed(title="通報ログ", color=0xff0000)
            embed.description = f"{message.content}"
            embed.add_field(name="通報者", value=ctx.author.mention)
            embed.add_field(name="通報対象", value=user.mention)
            try:
                embed.add_field(name="サーバー", value=ctx.guild.id)
            except:
                embed.add_field(name="サーバー", value="不明")
            await channel.send(embed=embed)
            try:
                await confirm_message.clear_reactions()
            except:
                pass
            await ctx.send("通報が完了しました")
        if reaction.emoji == "❎":
            await confirm_message.clear_reactions()
            return await ctx.send("通報をキャンセルしました")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        await asyncio.sleep(0.2)
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

    @report.error
    async def on_report_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が足りません",
                f"`{ctx.command.name}`の引数として通報対象のユーザーを指定してください"
            )


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
