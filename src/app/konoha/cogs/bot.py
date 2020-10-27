import discord
from discord.ext import commands

import re
import os
import asyncio
import subprocess
import tabulate
import aiomysql
import glob
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from pathlib import Path
from time import perf_counter

import konoha
import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import DurationToSecondsConverter, ColorConverter
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


async def get_duration(coro, *args, **kwargs):
    start = perf_counter()
    ret = await coro(*args, **kwargs)
    end = perf_counter()
    return (end - start) * 1000, ret


class Bot(commands.Cog):
    '''
    Botに関する基本的な設定や機能
    '''
    order = 0

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def report(self, ctx: commands.Context, *, text):
        '''
        バグなど開発者に報告できます(荒らし防止のため3分以内での連投を禁止しています．ご了承ください．)
        '''
        channel = ctx.bot.get_channel(756841194293690418)
        embed = discord.Embed(title="報告", color=config.theme_color)
        embed.description = f"```\n{text}\n```"
        embed.add_field(
            name="サーバー", value=f"{ctx.guild.name} / {ctx.guild.id}")
        embed.add_field(
            name="チャンネル", value=f"{ctx.channel.name} / {ctx.channel.id}")
        embed.add_field(
            name="ユーザー", value=f"{ctx.author.name} / {ctx.author.id}")
        await channel.send(embed=embed)
        await ctx.send("報告が完了しました！", delete_after=5)

    @report.error
    async def on_report_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "バグ内容など報告したい内容を引数に入力してください"
            )
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 1, 3)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        '''
        通信遅延を計測します．

        __**Websocket遅延**__
        Discordと双方向通信する際に使われる回線の遅延です

        __**API通信遅延**__
        Discordから情報を得るためのAPIサーバーの遅延です

        __**メッセージ送信遅延**__
        当BotからDIscordクライアントにメッセージを送信するのにかかる遅延です 
        '''
        discord_dur, _ = await get_duration(
            self.bot.session.get, "https://discord.com/"
        )
        loading = self.bot.custom_emojis.loading
        embed = discord.Embed(
            color=config.theme_color, title=f"{loading} 計測中")
        embed.set_author(name="ping", icon_url=self.bot.user.avatar_url)
        message_dur, message = await get_duration(
            ctx.send, embed=embed
        )
        db_dur, g = await get_duration(
            q.Guild(self.bot, ctx.guild.id).get
        )
        embed.title = '🏓 Pong!'
        embed.description = f"{self.bot.user.mention}は正常稼働中です"
        embed.add_field(name="Websocket遅延",
                        value=f"{self.bot.latency * 1000:.2f} ms", inline=False)
        embed.add_field(
            name="API通信遅延", value=f"{discord_dur:.2f} ms", inline=False)
        embed.add_field(name="メッセージ送信遅延",
                        value=f"{message_dur:.2f} ms", inline=False)
        embed.add_field(name="データベース通信遅延",
                        value=f"{db_dur:.2f} ms", inline=False)
        await message.edit(embed=embed)

    @commands.command()
    async def invite(self, ctx: commands.Context):
        '''
        Bot招待用のURLを表示します．

        このURL先にアクセスするとBotをあなたのサーバーに招待する画面へと移行します．
        '''
        perms = discord.Permissions(permissions=808840278)
        return await ctx.send(
            discord.utils.oauth_url(
                ctx.bot.user.id,
                permissions=perms
            )
        )

    @commands.command(aliases=["server"])
    @commands.guild_only()
    async def guild(self, ctx: commands.Context):
        '''
        ギルド(サーバー)に関する情報を表示します．
        '''
        guild: discord.Guild = ctx.guild
        members = guild.members
        onlines = len(
            list(filter(lambda m: m.status == discord.Status.online, members)))
        idles = len(
            list(filter(lambda m: m.status == discord.Status.idle, members)))
        dnds = len(
            list(filter(lambda m: m.status == discord.Status.dnd, members)))
        offlines = len(
            list(filter(lambda m: m.status == discord.Status.offline, members)))
        emo_on = self.bot.custom_emojis.online
        emo_id = self.bot.custom_emojis.idle
        emo_dn = self.bot.custom_emojis.dnd
        emo_of = self.bot.custom_emojis.offline
        embed = discord.Embed(title=f'{guild.name}', colour=0x4060e3)
        embed.set_thumbnail(url=str(guild.icon_url))
        embed.add_field(name='地域', value=f'{guild.region}')
        embed.add_field(name='ID', value=f'{guild.id}')
        embed.add_field(name='オーナー', value=f'{guild.owner.mention}')
        embed.add_field(name='テキストチャンネル数', value=f'{len(guild.text_channels)}')
        embed.add_field(name='ボイスチャンネル数', value=f'{len(guild.voice_channels)}')
        embed.add_field(
            name='メンバー', value=f'{len(members)}\n{emo_on} {onlines} {emo_id} {idles} {emo_dn} {dnds} {emo_of} {offlines}', inline=False)
        embed.set_footer(
            text=f'作成: {guild.created_at.strftime("%Y/%m/%d %H:%M:%S")}')
        await ctx.send(embed=embed)

    @commands.command()
    async def user(self, ctx: commands.Context, member: discord.Member = None):
        '''
        あなた自身に関する情報を表示します(2分後に自動削除)．

        管理者ユーザーは引数を指定し，特定ユーザーの情報を表示することが可能です．
        '''
        if ctx.author.guild_permissions.value & 268435518:
            if member is None:
                member = ctx.author
        else:
            member = ctx.author
        embed = discord.Embed(title=f'{member.name}', colour=member.color)
        embed.set_thumbnail(url=str(member.avatar_url))
        embed.add_field(name='a.k.a.', value=f'{member.display_name}')
        embed.add_field(name='ID', value=f'{member.id}')
        embed.add_field(
            name='参加日時', value=f'{member.joined_at.strftime("%y/%m/%d %H:%M:%S")}')
        embed.add_field(name='状態', value=f'{member.status}')
        if member.activity:
            embed.add_field(name='アクティビティ', value=f'{member.activity.name}')
        embed.add_field(name='Bot/非Bot',
                        value=f'{"非" if not member.bot else ""}Bot')
        embed.add_field(
            name='役職', value=f'{", ".join([role.name for role in member.roles])}')
        embed.set_footer(
            text=f'ユーザー作成日時: {member.created_at.strftime("%y/%m/%d %H:%M:%S")}')
        await ctx.send(embed=embed, delete_after=120)

    @user.error
    async def on_user_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.BadArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "ユーザーが見つかりませんでした！",
                f"`{ctx.message.content.split()[1]}`というユーザーは見つかりませんでした..."
            )

    @commands.command()
    async def about(self, ctx: commands.Context):
        '''
        当Botに関する情報を表示します．
        '''
        bot = self.bot
        appinfo: discord.AppInfo = await bot.application_info()
        shard = f'{bot.shard_id}/{bot.shard_count}' if bot.shard_id else None
        embed = discord.Embed(
            title=f'{appinfo.name}', colour=config.theme_color)
        embed.set_thumbnail(url=str(appinfo.icon_url))
        embed.add_field(name='Version', value=f'**{konoha.__version__}**')
        embed.add_field(name='開発者', value=f'{appinfo.owner.mention}')
        embed.add_field(name='ギルド数', value=f'{len(bot.guilds)}')
        embed.add_field(name='総ユーザー数', value=f'{len(bot.users)}')
        if shard is not None:
            embed.add_field(name='シャード No.', value=shard)
        embed.add_field(
            name='公開状態', value=f'{"Public" if appinfo.bot_public else "Private" }')
        embed.add_field(name='ID', value=f'{appinfo.id}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Bot(bot))
