import discord
from discord.ext import commands

import re
import os
import subprocess
import tabulate
import asyncio
import aiomysql
import secrets
import io
import psutil
import platform
import matplotlib.pyplot as plt
from pathlib import Path
from pytz import timezone
from datetime import datetime
from time import perf_counter

import konoha
import konoha.models.crud2 as q
from konoha.core.utils.consts import alphabet_emojis
from konoha.core.utils.pagination import EmbedPaginator
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Vote(commands.Cog):
    """
    リアクション機能を用いた投票機能です
    """
    order = 2

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command(aliases=["poll", "vc", "pc"])
    @commands.guild_only()
    async def vote(self, ctx: commands.Context, description, *options):
        '''
        リアクションを使用した投票を作成します．

        選択肢の数は最大20個まで増やすことが可能です．

        __**使用方法**__

        {prefix}vote 集合何時にする？ 12時 2時 5時
        '''
        id = secrets.token_hex(16)[:6]
        if len(options) > 20:
            return await self.bot.send_error(
                ctx, "引数の数が多すぎます",
                "選択肢は20個以内である必要があります"
            )
        if any([len(opt) > 50 for opt in options]):
            return await self.bot.send_error(
                ctx, "選択肢の文字数が長すぎます",
                "選択肢は50文字未満である必要があります"
            )
        if len(description) > 50:
            return await self.bot.send_error(
                ctx, "題名の文字数が長すぎます",
                "題名は50文字未満である必要があります"
            )
        embed = discord.Embed(title="投票", color=config.theme_color)
        embed.set_author(name=f"投票ID: {id}",
                         icon_url=self.bot.user.avatar_url)
        embed.description = f"**{description}**\n\n"
        ln_len = 0
        if not options:
            options = ('はい', 'いいえ')
        for emoji, option in zip(alphabet_emojis, options):
            c = f"{emoji} {option}　"
            ln_len += len(c)
            embed.description += c
            if ln_len > 30:
                embed.description += "\n\n"
                ln_len = 0
        embed.description = embed.description.rstrip("\n")
        embed.set_footer(text=f"vote_listコマンドで投票の一覧を確認できます")
        msg: discord.Message = await ctx.send(embed=embed)
        for emoji in alphabet_emojis[:len(options)]:
            await msg.add_reaction(emoji)
        await q.Vote.create(
            self.bot,
            id,
            guild=ctx.guild.id,
            channel=ctx.channel.id,
            message=msg.id,
            user=ctx.author.id,
            description=description,
        )

    @commands.command(aliases=["poll1", "vc1", "pc1"])
    @commands.guild_only()
    @checks.bot_can_manage_messages()
    async def vote1(self, ctx: commands.Context, description, *options):
        '''
        リアクションを使用した1人1表の投票を作成します．

        選択肢の数は最大20個まで増やすことが可能です．

        __**使用方法**__

        {prefix}vote 集合何時にする？ 12時 2時 5時
        '''
        id = secrets.token_hex(16)[:6]
        if len(options) > 20:
            return await self.bot.send_error(
                ctx, "引数の数が多すぎます",
                "選択肢は20個以内である必要があります"
            )
        if any([len(opt) > 50 for opt in options]):
            return await self.bot.send_error(
                ctx, "選択肢の文字数が長すぎます",
                "選択肢は50文字未満である必要があります"
            )
        if len(description) > 50:
            return await self.bot.send_error(
                ctx, "題名の文字数が長すぎます",
                "題名は50文字未満である必要があります"
            )
        embed = discord.Embed(title="投票", color=config.theme_color)
        embed.set_author(name=f"投票ID: {id} (1人1票)",
                         icon_url=self.bot.user.avatar_url)
        embed.description = f"**{description}**\n\n"
        ln_len = 0
        if not options:
            options = ('はい', 'いいえ')
        for emoji, option in zip(alphabet_emojis, options):
            c = f"{emoji} {option}　"
            ln_len += len(c)
            embed.description += c
            if ln_len > 30:
                embed.description += "\n\n"
                ln_len = 0
        embed.description = embed.description.rstrip("\n")
        embed.set_footer(text=f"vote_listコマンドで投票の一覧を確認できます")
        msg: discord.Message = await ctx.send(embed=embed)
        for emoji in alphabet_emojis[:len(options)]:
            await msg.add_reaction(emoji)
        await q.Vote.create(
            self.bot,
            id,
            guild=ctx.guild.id,
            channel=ctx.channel.id,
            message=msg.id,
            user=ctx.author.id,
            description=description,
            opov=True
        )

    @vote.error
    @vote1.error
    async def on_vc_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, '引数が不足しています！',
                '投票を作成する場合は投票に関する説明を引数に取る必要があります'
            )

    @commands.command(name="vote_list", aliases=["poll_list", "vl", "pl"])
    @commands.guild_only()
    async def vote_list(self, ctx: commands.Context):
        '''
        作成した投票のリストを表示します
        '''
        paginator = EmbedPaginator(title="投票一覧", color=config.theme_color,
                                   icon=str(self.bot.user.avatar_url), footer="Page $p / $P")
        paginator.new_page()
        votes = await q.Vote.search(self.bot, guild=ctx.guild.id)
        if not votes:
            return await ctx.send("投票はまだ作成していません")
        for vote in votes:
            url = f"https://discord.com/channels/{vote.guild}/{vote.channel}/{vote.message}"
            paginator.add_row(
                k=f"{vote.description}", v=f"ID: `{vote.id}` by <@{vote.user}> | [[メッセージへジャンプ！]]({url})")
        await paginator.paginate(ctx)

    @commands.command(name="vote_delete", aliases=["poll_delete", "vd", "pd"])
    @commands.guild_only()
    @checks.can_manage_messages()
    async def vote_delete(self, ctx: commands.Context, id):
        '''
        作成した投票を削除します
        '''
        vote = await q.Vote(self.bot, id).get()
        if not vote:
            return await ctx.send('指定したIDの投票はありません')
        await q.Vote(self.bot, id).delete()
        await ctx.message.add_reaction('✅')

    @commands.command(name="vote_analyze", aliases=["poll_analyze", "va", "pa"])
    @commands.cooldown(5, 120, commands.BucketType.guild)
    async def vote_analyze(self, ctx: commands.Context, id: str):
        '''
        投票の集計結果を表示します
        '''
        msg1 = await ctx.send(f'集計中 {self.bot.custom_emojis.loading}')
        vote = await q.Vote(self.bot, id).get()
        if vote is None:
            return await ctx.send("該当の投票は存在しません")
        with ctx.typing():
            try:
                msg: discord.Message = await ctx.fetch_message(vote.message)
            except discord.NotFound:
                return await self.bot.send_error(ctx, 'メッセージが見つかりません', '該当のメッセージは削除されているようです')
            args = [
                arg[2:]
                for arg in
                "".join(
                    msg.embeds[0]
                    .description
                    .split("\n\n")[1:]
                ).split("　")
                if arg != ''
            ]
            if not args:
                args = ['はい', 'いいえ']
            points = {i: [k, 0, "", None] for i, k in enumerate(args)}
            for reaction in msg.reactions:
                try:
                    idx = alphabet_emojis.index(reaction.emoji)
                except ValueError:
                    continue
                points[idx][3] = reaction.emoji
                points[idx][1] = reaction.count - 1
                us = [u for u in await reaction.users().flatten() if u.id != self.bot.user.id]
                t = 5
                if len(us) == 0:
                    points[idx][2] = '-'
                elif len(us) > t:
                    points[idx][2] = ' '.join(
                        [f'{u.mention}' for u in us[:t]]) + f' ほか{len(us) - t}名'
                else:
                    points[idx][2] = ' '.join(
                        [f'{u.mention}' for u in us])
            if sum([point[1] for point in points.values()]) == 0:
                return await ctx.send("まだ誰も投票していないようです")

            def create_image(vt, pts):
                plt.style.use('dark_background')
                plt.figure(figsize=(7, 4))
                plt.axes().set_aspect('equal')
                x = [v[1] for v in pts.values()]
                l = [f"{v[0]}: {v[1]}" for v in pts.values()]
                f = io.BytesIO()
                plt.title(vote.description, fontsize=16)
                plt.rcParams["font.size"] = 14
                plt.pie(x, labels=l, startangle=90)
                plt.savefig(f, format="png")
                f.seek(0)
                return discord.File(f, filename="chart.png")
            file = await self.bot.loop.run_in_executor(None, create_image, vote, points)
            url = f"https://discord.com/channels/{vote.guild}/{vote.channel}/{vote.message}"
            embed = discord.Embed(title="投票集計", color=config.theme_color)
            embed.description = f"[{vote.description}]({url}) by <@{vote.user}>"
            for idx, point in points.items():
                if point[3]:
                    embed.add_field(
                        name=f"{point[3]}: {point[0]} ({point[1]})", value=point[2], inline=False)
            embed.set_author(name=f"投票ID: {id}",
                             icon_url=self.bot.user.avatar_url)
            await msg1.edit(content='', embed=embed)
            await ctx.send(file=file)

    @vote_analyze.error
    async def on_va_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 3, 1)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or not payload.emoji.name in alphabet_emojis:
            return
        votes = await q.Vote.search(self.bot, message=payload.message_id)
        if len(votes) > 0:
            vote = votes[0]
            if not vote.opov:
                return
            guild: discord.Guild = self.bot.get_guild(payload.guild_id)
            channel: discord.TextChannel = guild.get_channel(
                payload.channel_id)
            member: discord.Member = guild.get_member(payload.user_id)
            message: discord.Message = await channel.fetch_message(payload.message_id)
            tasks = []
            for reaction in message.reactions:
                if reaction.emoji != payload.emoji.name:
                    tasks.append(message.remove_reaction(
                        reaction.emoji, member))
            await asyncio.gather(*tasks)


def setup(bot):
    bot.add_cog(Vote(bot))
