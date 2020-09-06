import discord
from discord.ext import commands

import re
import os
import subprocess
import tabulate
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
from konoha.core.utils.pagination import EmbedPaginator
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


emojis = [
    "🇦", "🇧", "🇨", "🇩", "🇪",
    "🇫", "🇬", "🇭", "🇮", "🇯",
    "🇰", "🇱", "🇲", "🇳", "🇴",
    "🇵", "🇶", "🇷", "🇸", "🇹",
    "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"
]


class Reaction(commands.Cog):
    """
    リアクション機能を用いた便利機能です
    """
    order = 2

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command(aliases=["poll", "vc", "pc"])
    @commands.guild_only()
    async def vote(self, ctx: commands.Context, description, *options):
        '''
        リアクションを使用した投票を作成します．

        選択肢の数は最大26個まで増やすことが可能です．

        __**使用方法**__

        {prefix}vote 集合何時にする？ 12時 2時 5時
        '''
        id = secrets.token_hex(16)[:6]
        if len(options) > 26:
            return await self.bot.send_error(
                ctx, "引数の数が多すぎます",
                "選択肢は26個以内である必要があります"
            )
        if len(options) < 1:
            return await self.bot.send_error(
                ctx, "引数の数が少なぎます",
                "選択肢は1個以上である必要があります"
            )
        if any([len(opt) > 15 for opt in options]):
            return await self.bot.send_error(
                ctx, "選択肢の文字数が長すぎます",
                "選択肢は15文字未満である必要があります"
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
        for emoji, option in zip(emojis, options):
            c = f"{emoji} {option}　"
            ln_len += len(c)
            embed.description += c
            if ln_len > 30:
                embed.description += "\n\n"
                ln_len = 0
        embed.description = embed.description.rstrip("\n")
        embed.set_footer(text=f"vote_listコマンドで投票の一覧を確認できます")
        msg: discord.Message = await ctx.send(embed=embed)
        for emoji in emojis[:len(options)]:
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

    @commands.command(name="vote_list", aliases=["poll_list", "vl", "pl"])
    @commands.guild_only()
    async def vote_list(self, ctx: commands.Context):
        '''
        作成した投票のリストを表示します
        '''
        paginator = EmbedPaginator(title="投票一覧", color=config.theme_color,
                                   icon=str(self.bot.user.avatar_url), footer="Page $p / $P")
        paginator.new_page()
        votes = await q.Vote.search(self.bot,guild=ctx.guild.id)
        if not votes:
            return await ctx.send("投票はまだ作成していません")
        for vote in votes:
            url = f"https://discord.com/channels/{vote.guild}/{vote.channel}/{vote.message}"
            paginator.add_row(
                k=f"{vote.description}", v=f"ID: `{vote.id}` by <@{vote.user}> | [[メッセージへジャンプ！]]({url})")
        await paginator.paginate(ctx)

    @commands.command(name="vote_analyze", aliases=["poll_analyze", "va", "pa"])
    @commands.cooldown(5, 120, commands.BucketType.guild)
    async def vote_analyze(self, ctx: commands.Context, id: str):
        '''
        投票の集計結果を表示します
        '''
        vote = await q.Vote(self.bot,id).get()
        if vote is None:
            return await ctx.send("該当の投票は存在しません")
        with ctx.typing():
            msg: discord.Message = await ctx.fetch_message(vote.message)
            args = [
                arg[2:]
                for arg in
                "".join(
                    msg.embeds[0]
                    .description
                    .split("\n\n")[1:]
                ).split("　")
            ]
            points = {i: [k, 0, []] for i, k in enumerate(args)}
            for reaction in msg.reactions:
                try:
                    idx = emojis.index(reaction.emoji)
                except ValueError:
                    continue
                points[idx][1] = reaction.count - 1
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
            embed = discord.Embed(title="投票集計")
            embed.description = f"[{vote.description}]({url}) by <@{vote.user}>"
            embed.set_author(name=f"投票ID: {id}", color=config.theme_color,
                             icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            await ctx.send(file=file)

    @vote_analyze.error
    async def on_va_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 3, 1)


def setup(bot):
    bot.add_cog(Reaction(bot))
