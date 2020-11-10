import discord
from discord.ext import commands

import re
import os
import sys
import io
import subprocess
import tabulate
import aiomysql
import psutil
import platform
import textwrap
import traceback
from contextlib import redirect_stdout
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


class Administrator(commands.Cog):
    """
    Bot管理用のコマンド
    """
    order = 999

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx: commands.Context):
        '''
        Cogを再読み込みします
        '''
        self.bot.get_all_cogs(True)
        await self.bot.send_notification(ctx, 'Cogの再読み込みが終了しました')

    @commands.is_owner()
    @commands.command()
    async def migrate(self, ctx: commands.Context):
        '''
        データベースのマイグレーションを行います
        '''
        msg = await ctx.send(f'マイグレーションの実行中です {self.bot.custom_emojis.loading}')
        alembic_path = Path(os.path.abspath(konoha.__file__)).parent / "models"
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
        description = ""
        if proc.stdout:
            description += f"**stdout >**\n```\n{proc.stdout}\n```"
        if proc.stderr:
            description += f"**stderr >**\n```\n{proc.stderr}\n```"
        for l in proc.stdout.split("\n"):
            logger.info(l)
        for l in proc.stderr.split("\n"):
            logger.warn(l)
        await msg.edit(content='マイグレーションが終了しました')
        if description:
            await ctx.send(content=description)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def add_user_as(self, ctx: commands.Context, user: discord.User, role: str):
        '''
        ユーザーを指定した役職へ任命します
        '''
        if user is None:
            return await ctx.send(f"Userが見つかりません")
        if await q.User(self.bot, user.id).get():
            await q.User(self.bot, user.id).set(**{role: True})
        else:
            await q.User.create(self.bot, user.id, **{role: True})
        await ctx.message.add_reaction('✅')

    @commands.is_owner()
    @commands.command()
    async def sql(self, ctx: commands.Context, *, query):
        '''
        生のSQLを実行します
        '''
        result = await self.bot.execute(query)
        try:
            data = await result.fetchall()
            table = tabulate.tabulate(
                [r.as_tuple() for r in data], headers=data[0].keys(), tablefmt="fancy_grid")
            return await ctx.send(f"```\n{table}\n```")
        except aiomysql.sa.ResourceClosedError:
            return await ctx.send(f"正常に実行されました")

    @commands.is_owner()
    @commands.command()
    async def restart(self, ctx: commands.Context):
        '''
        Botを再起動します
        '''
        try:
            embed = discord.Embed(title="⚠ 再起動します", color=0xff0000)
            await ctx.send(embed=embed)
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            return await self.bot.send_error(
                ctx, f'{e.__class__.__name__}',
                f'```py\n{traceback.format_exc()[:2000]}\n```'
            )
        python = sys.executable
        args = '-m konoha config.ini'.split()
        os.execl(python, 'python', *args)

    @commands.is_owner()
    @commands.command(aliases=["e"])
    async def error_log(self, ctx: commands.Context, id: str):
        '''
        エラーログを取得します
        '''
        error = await q.Error(self.bot, id).get()
        if error:
            embed = discord.Embed(title=error.name, color=0xff0000)
            embed.set_author(
                name=f"Error: {error.id}", icon_url=self.bot.user.avatar_url)
            embed.description = f"**Traceback**\n```python\n{error.traceback}\n```"
            g = await ctx.bot.fetch_guild(error.guild)
            c = await ctx.bot.fetch_channel(error.channel)
            embed.add_field(name="サーバー", value=f"{g.name} ({error.guild})")
            embed.add_field(
                name="チャンネル", value=f"{c.mention} ({error.channel})")
            if error.guild:
                embed.add_field(
                    name="メッセージ", value=f"[{error.message}](https://discord.com/channels/{error.guild}/{error.channel}/{error.message})")
            embed.add_field(name="投稿者", value=f"<@{error.user}>")
            embed.add_field(
                name="詳細", value=f"```\n{error.detail}\n```", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("該当のエラーはありません")

    def render_percent(self, p, preline=None, postline=None):
        if p < 50:
            lang = "ini"
        elif p < 85:
            lang = "fix"
        else:
            lang = "css"
        L = 40
        l = int(L * p / 100)
        bar = f"[{'|' * l + ' ' * (L - l)}] [{p:5.2f} %]"
        if preline and postline:
            return f"```{lang}\n{preline}\n{bar}\n{postline}\n```"
        elif preline and not postline:
            return f"```{lang}\n{preline}\n{bar}\n```"
        elif not preline and postline:
            return f"```{lang}\n{bar}\n{postline}\n```"
        else:
            return f"```{lang}\n{bar}\n```"

    @commands.is_owner()
    @commands.command()
    async def status(self, ctx: commands.Context):
        '''
        ホストPCの情報を表示します
        '''
        def to_B(byte):
            if byte < 1024:
                return f"{byte} Byte"
            elif byte < 1024 ** 2:
                return f"{byte / 1024:7.2f} KB"
            elif byte < 1024 ** 3:
                return f"{byte / (1024 ** 2):7.2f} MB"
            elif byte < 1024 ** 4:
                return f"{byte / (1024 ** 3):7.2f} GB"
            elif byte < 1024 ** 5:
                return f"{byte / (1024 ** 4):7.2f} TB"
            else:
                return f"{byte / (1024 ** 5):7.2f} PB"

        def to_T(s):
            s = int(s)
            if s < 120:
                return f"{s:3d} 秒"
            elif s < 60 * 120:
                return f"{s // 60:3d} 分 {s % 60:3d} 秒"
            elif s < 60 * 60 * 24 * 2:
                return f"{s // (60*60):2d} 時間 {(s % 3600)// 60:3d} 分 {s % 60:3d} 秒"
            elif s < 60 * 60 * 24 * 365:
                return f"{s // (60*60*24):3d} 日 {(s % (60*60*24)) // 3600:2d} 時間"
            else:
                return f"{int(s // (60*60*24*365)):2d} 年 {int((s % (60*60*24*365)) // (3600*24)):2d} 日 {int((s % (60*60*24)) // 3600):2d} 時間"
        paginator = EmbedPaginator(
            title="Host PCの使用状況 ",
            footer=f"Page $p / $P [{datetime.now().astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S %Z')}]")
        # CPU
        p = 0
        paginator.new_page()
        paginator.content[p]["title"] += "[CPU]"
        cpu = psutil.cpu_percent()
        paginator.add_row_manually("CPU", self.render_percent(cpu), page=p)
        for i, cpu in enumerate(psutil.cpu_percent(percpu=True)):
            paginator.add_row_manually(
                f"CPU #{i}", self.render_percent(cpu), page=p)
        # Memory
        paginator.new_page()
        p = 1
        vm = psutil.virtual_memory()
        paginator.content[p]["title"] += "[RAM]"
        paginator.add_row_manually(
            "仮想メモリ",
            self.render_percent(
                vm.percent,
                preline=f"[{to_B(vm.total - vm.available)} / {to_B(vm.total)}]",
                postline=(
                    f"\n\n"
                    f"[Available : {to_B(vm.available)}]\n\n"
                    f"[Total     : {to_B(vm.total)}]\n\n"
                    f"[Free      : {to_B(vm.free)}]\n\n"
                    f"[Buffer    : {to_B(vm.buffers)}]\n\n"
                    f"[Cache     : {to_B(vm.cached)}]"
                )
            ),
            page=p
        )
        sm = psutil.swap_memory()
        paginator.add_row_manually(
            "スワップメモリ",
            self.render_percent(
                sm.percent,
                preline=f"[{to_B(sm.used)} / {to_B(sm.total)}]"
            ),
            page=p
        )
        # Disk
        paginator.new_page()
        p = 2
        paginator.content[p]["title"] += "[Others]"
        disk = psutil.disk_usage("/")
        paginator.add_row_manually(
            "Disk使用率",
            self.render_percent(
                disk.percent,
                preline=f"[{to_B(disk.used)} / {to_B(disk.total)}]"
            ),
            page=p
        )
        paginator.add_row_manually(
            "起動時間",
            f"```python\n{to_T(int(datetime.now().timestamp()) - psutil.boot_time())}\n```",
            page=p
        )
        paginator.add_row_manually(
            "OS",
            f"```\n{platform.platform()}\n```",
            page=p
        )
        await paginator.paginate(ctx)

    @commands.is_owner()
    @commands.command(name='eval')
    async def _eval(self, ctx: commands.Context, *, body: str):
        '''
        任意のコマンドを実行します
        '''
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }
        env.update(globals())
        body = self.cleanup_code(body)
        cmd = f'async def func():\n{textwrap.indent(body, "  ")}'
        try:
            exec(cmd, env)
            await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.message.add_reaction('😲')
            return await self.bot.send_error(ctx, f'{e.__class__.__name__}', str(e))
        func = env['func']
        stdout = io.StringIO()
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            return await self.bot.send_error(
                ctx, f'{e.__class__.__name__}',
                f'```py\n{value}{traceback.format_exc()[:3000]}\n```'
            )
        else:
            value = stdout.getvalue()
            value = value.replace(config.bot_token ,"[TOKEN]")
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Administrator(bot))
