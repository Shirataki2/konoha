import discord
from discord.ext import commands

import re
import os
import subprocess
import tabulate
import aiomysql
from pathlib import Path
from time import perf_counter

import konoha
import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)

async def get_duration(coro, *args, **kwargs):
    start = perf_counter()
    ret = await coro(*args, **kwargs)
    end = perf_counter()
    return (end - start) * 1000, ret

class Utils(commands.Cog):
    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        '''
        通信遅延を計測します
        '''
        logger.info("'Ping'コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        discord_dur, _ = await get_duration(
            self.bot.session.get, "https://discord.com/"
        )
        embed = discord.Embed(color=config.theme_color).set_author(name="⏳計測中...")
        message_dur, message = await get_duration(
            ctx.send, embed=embed
        )
        embed.set_author(name='Pong!', icon_url=self.bot.user.avatar_url)
        embed.description = f"{self.bot.user.mention}は正常稼働中です"
        embed.add_field(name="Websocket遅延", value=f"{self.bot.latency * 1000:.2f} ms")
        embed.add_field(name="API通信遅延", value=f"{discord_dur:.2f} ms")
        embed.add_field(name="メッセージ送信遅延", value=f"{message_dur:.2f} ms")
        await message.edit(embed=embed)
            
    @commands.command()
    @checks.can_manage_guild()
    async def prefix(self, ctx: commands.Context, prefix: str):
        '''
        Botを呼び出すための接頭文字(Prefix)を変更します
        '''
        logger.info("'Prefix' コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        if prefix:
            if len(prefix) > 8:
                return await ctx.send("prefixは8文字以内である必要があります")
            logger.debug(f"\t変更後のPrefix: {prefix}")
            await q.Guild(ctx.guild.id).set(prefix=prefix)
        embed = discord.Embed(color=config.theme_color)
        embed.set_author(name='Prefix変更', icon_url=self.bot.user.avatar_url)
        embed.description = f"{self.bot.user.mention}のPrefixを`{prefix}`に変更しました"
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx: commands.Context):
        '''
        Bot招待用のURLを表示します
        '''
        logger.info("'Invite' コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        return await ctx.send(f"{config.oauth2_url}")

    @commands.command()
    @commands.guild_only()
    async def guild(self, ctx: commands.Context):
        '''
        ギルド(サーバー)に関する情報を表示します
        '''
        logger.info("'Guild' コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        guild: discord.Guild = ctx.guild
        members = guild.members
        onlines = len(list(filter(lambda m:m.status==discord.Status.online,members)))
        idles = len(list(filter(lambda m:m.status==discord.Status.idle,members)))
        dnds = len(list(filter(lambda m:m.status==discord.Status.dnd,members)))
        offlines = len(list(filter(lambda m:m.status==discord.Status.offline,members)))
        emo_on = self.bot.get_emoji(706276692465025156)
        emo_id = self.bot.get_emoji(706276692678934608)
        emo_dn = self.bot.get_emoji(706276692674609192)
        emo_of = self.bot.get_emoji(706276692662157333)
        embed = discord.Embed(title=f'{guild.name}', colour=0x4060e3)
        embed.set_thumbnail(url=str(guild.icon_url))
        embed.add_field(name='地域', value=f'{guild.region}')
        embed.add_field(name='ID', value=f'{guild.id}')
        embed.add_field(name='オーナー', value=f'{guild.owner.mention}')
        embed.add_field(name='テキストチャンネル数', value=f'{len(guild.text_channels)}')
        embed.add_field(name='ボイスチャンネル数', value=f'{len(guild.voice_channels)}')
        embed.add_field(name='メンバー', value=f'{len(members)}\n{emo_on} {onlines} {emo_id} {idles} {emo_dn} {dnds} {emo_of} {offlines}', inline=False)
        embed.set_footer(text=f'作成: {guild.created_at.strftime("%Y/%m/%d %H:%M:%S")}')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx: commands.Context, user=None):
        '''
        ユーザーに関する情報を表示
        引数を指定しない場合は送信者の情報が表示されます
        '''
        logger.info("'User' コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        def mention_to_id(mention):
            if members := re.findall(r'<@[\!&]?([0-9]+)?>', mention):
                return [int(member) for member in members]
            else:
                return None
        try:
            member = await ctx.guild.fetch_member(mention_to_id(user)[0])
        except:
            member = ctx.author
        embed = discord.Embed(title=f'{member.name}', colour=member.color)
        embed.set_thumbnail(url=str(member.avatar_url))
        embed.add_field(name='a.k.a.', value=f'{member.display_name}')
        embed.add_field(name='ID', value=f'{member.id}')
        embed.add_field(name='参加日時', value=f'{member.joined_at.strftime("%y/%m/%d %H:%M:%S")}')
        embed.add_field(name='状態', value=f'{member.status}')
        if member.activity:
            embed.add_field(name='アクティビティ', value=f'{member.activity.name}')
        embed.add_field(name='Bot/非Bot', value=f'{"非" if not member.bot else ""}Bot')
        embed.add_field(name='役職', value=f'{", ".join([role.name for role in member.roles])}')
        embed.set_footer(text=f'ユーザー作成日時: {member.created_at.strftime("%y/%m/%d %H:%M:%S")}')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def about(self, ctx: commands.Context):
        '''
        当Botに関する情報を表示します
        '''
        logger.info("'About' コマンドが実行されました")
        logger.debug(f"\t{ctx.guild.name}({ctx.guild.id})")
        bot = self.bot
        appinfo: discord.AppInfo = await bot.application_info()
        shard = f'{bot.shard_id}/{bot.shard_count}' if bot.shard_id else None
        embed = discord.Embed(title=f'{appinfo.name}', colour=config.theme_color)
        embed.set_thumbnail(url=str(appinfo.icon_url))
        embed.add_field(name='Version', value=f'**{konoha.__version__}**')
        embed.add_field(name='開発者', value=f'{appinfo.owner.mention}')
        embed.add_field(name='ギルド数', value=f'{len(bot.guilds)}')
        embed.add_field(name='総ユーザー数', value=f'{len(bot.users)}')
        if shard is not None:
            embed.add_field(name='シャード No.', value=shard)
        embed.add_field(name='公開状態', value=f'{"Public" if appinfo.bot_public else "Private" }')
        embed.add_field(name='ID', value=f'{appinfo.id}')
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(hidden=True)
    @commands.cooldown(1, 1)
    async def reload(self, ctx: commands.Context):
        '''
        Cogを再読み込みします
        '''
        logger.info("'Reload' コマンドが実行されました")
        self.bot.get_all_cogs(True)
        await ctx.send('Cogの再読み込みが終了しました')


    @commands.is_owner()
    @commands.command(hidden=True)
    async def migrate(self, ctx: commands.Context):
        '''
        データベースのマイグレーションを行います
        '''
        logger.info("'Migrate' コマンドが実行されました")
        alembic_path = Path(os.path.abspath(konoha.__file__)).parent / "models"
        print(alembic_path)
        proc = subprocess.run(
            (
                f'cd {alembic_path};'
                f'PYTHONPATH="." alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\";'
                f'PYTHONPATH="." alembic upgrade head'
            ),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        for l in proc.stdout.split("\n"):
            logger.info(l)
        for l in proc.stderr.split("\n"):
            logger.warn(l)
        await ctx.send('マイグレーションが終了しました')

    @commands.is_owner()
    @commands.command(hidden=True)
    @commands.cooldown(1, 1)
    async def sql(self, ctx: commands.Context, *, query):
        '''
        生のSQLを実行します
        '''
        logger.info("'SQL' コマンドが実行されました")
        logger.info(f"\t{query}")
        async with q.DB() as db:
            result = await db.execute(query)
            try:
                data = await result.fetchall()
                table = tabulate.tabulate([r.as_tuple() for r in data], headers=data[0].keys(), tablefmt="fancy_grid")
                return await ctx.send(f"```\n{table}\n```")
            except aiomysql.sa.ResourceClosedError:
                return await ctx.send(f"正常に実行されました")

def setup(bot):
    bot.add_cog(Utils(bot))