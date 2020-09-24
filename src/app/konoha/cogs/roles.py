import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
import re
import pymysql
from typing import Optional, List, Union
from functools import partial
from pybooru import Danbooru

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.exceptions import to_japanese
from konoha.core.commands import checks
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class RoleError(commands.CommandError):
    pass


class Roles(commands.Cog):
    '''
    ロールの操作に関するコマンド
    '''
    order = 13

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.group(hidden=True)
    @checks.bot_has_perms(manage_roles=True)
    async def role(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}role add @role`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command.name)

    @role.command()
    @checks.has_perms(manage_roles=True)
    async def add(self, ctx: commands.Context, users: commands.Greedy[discord.Member], role: discord.Role, *, reason: str = None):
        '''
        指定のユーザー(複数指定可; 未指定の場合は自分)にロールを付与します
        '''
        if not users:
            users = [ctx.author]
        await asyncio.gather(*[user.add_roles(role, reason=reason) for user in users])
        await self.bot.send_notification(
            ctx, "ロールの追加が完了しました",
            ", ".join([f"{u.mention}" for u in users]) +
            f"に{role.mention}のロールを追加しました"
        )

    @role.command()
    @checks.has_perms(manage_roles=True)
    async def remove(self, ctx: commands.Context, users: commands.Greedy[discord.Member], role: discord.Role, *, reason: str = None):
        '''
        指定のユーザー(複数指定可; 未指定の場合は自分)からロールをはく奪します
        '''
        if not users:
            users = [ctx.author]
        await asyncio.gather(*[user.remove_roles(role, reason=reason) for user in users])
        await self.bot.send_notification(
            ctx, "ロールのはく奪が完了しました",
            ", ".join([f"{u.mention}" for u in users]) +
            f"に{role.mention}からロールをはく奪しました"
        )

    @role.group(hidden=True)
    @checks.has_perms(manage_roles=True)
    async def join(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}role add @role`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command.name)

    @join.command(name="add")
    async def join_add(self, ctx: commands.Context, roles: commands.Greedy[discord.Role]):
        '''
        サーバー参加時に付加されるロールを追加します
        '''
        for role in roles:
            try:
                await q.JoinRole.create(self.bot, ctx.guild.id, role.id)
            except pymysql.IntegrityError as e:
                errno = e.args[0]
                if errno == 1062:  # Duplicate Key
                    pass
                else:
                    raise e
        rs = await q.JoinRole(self.bot, ctx.guild.id).get()
        await self.bot.send_notification(
            ctx, "新規メンバー参加時の自動ロール付与",
            ", ".join([f"{r.mention}" for r in roles]) +
            "をこのサーバーに新しいメンバーが参加した際に自動的に付与される" +
            "ロールとして登録しました\n\n" +
            f"現在の登録ロール: {', '.join([f'<@&{r.role}>' for r in rs])}"
        )

    @join.command(name="remove")
    async def join_remove(self, ctx: commands.Context, roles: commands.Greedy[discord.Role]):
        '''
        サーバー参加時に付加されるロールを指定し，削除します
        '''
        missing = []
        found = []
        for role in roles:
            dbroles = await q.JoinRole.search(self.bot, guild=ctx.guild.id, role=role.id)
            if not dbroles:
                missing.append(role)
            else:
                found.append(role)
        if missing:
            await self.bot.send_warning(
                ctx, "未登録のロールです",
                ", ".join([f"{r.mention}" for r in missing]) +
                "は，参加時の自動付与ロールとして登録されていません"
            )
        if found:
            await asyncio.gather(*[q.JoinRole.remove(self.bot, ctx.guild.id, r.id) for r in found])
            rs = await q.JoinRole(self.bot, ctx.guild.id).get()
            await self.bot.send_notification(
                ctx, "新規メンバー参加時の自動ロール付与",
                ", ".join([f"{r.mention}" for r in found]) +
                "をこのサーバーに新しいメンバーが参加した際に自動的に付与される" +
                "ロールから削除しました\n\n" +
                f"現在の登録ロール: {', '.join([f'<@&{r.role}>' for r in rs])}"
            )

    @join.command(name="list")
    async def join_list(self, ctx: commands.Context):
        '''
        サーバー参加時に付加されるロールの一覧を表示します
        '''
        rs = await q.JoinRole(self.bot, ctx.guild.id).get()
        if rs is not None:
            await self.bot.send_notification(
                ctx, "新規メンバー参加時の自動ロール付与",
                ", ".join([f"{role.mention}" for r in rs if (role := ctx.guild.get_role(int(r.role))) is not None]) +
                "が自動付与ロールとして登録されています"
            )
        else:
            await self.bot.send_notification(
                ctx, "新規メンバー参加時の自動ロール付与",
                "現在は何も登録されていません"
            )

    @role.command()
    async def info(
        self,
        ctx: commands.Context,
        target: Union[discord.Member, discord.Role, None] = None,
        channel: Union[discord.TextChannel, discord.CategoryChannel,
                       discord.VoiceChannel, None] = None
    ):
        '''
        Targetに指定したUserまたはRoleの権限を表示します．channelを指定しない場合はサーバー全体での権限を表示します．
        '''
        if target is None:
            target = ctx.author
        if isinstance(target, discord.Member):
            if channel is None:
                embed = discord.Embed(
                    title=f"@{target.display_name}のサーバー全体の権限",
                    description="",
                    color=config.theme_color
                )
                perms = target.guild_permissions
            else:
                embed = discord.Embed(
                    title=f"@{target.display_name}の「#{channel.name}」での権限",
                    description="",
                    color=config.theme_color
                )
                perms = channel.permissions_for(target)
        elif isinstance(target, discord.Role):
            if channel is None:
                embed = discord.Embed(
                    title=f"@{target.name}のサーバー全体の権限",
                    description="",
                    color=config.theme_color
                )
                perms = target.permissions
            else:
                embed = discord.Embed(
                    title=f"@{target.name}の「#{channel.name}」での権限",
                    description="",
                    color=config.theme_color
                )
                overs = channel.overwrites_for(target)
                perms = {}
                for (ok, ov) in iter(overs):
                    pv = getattr(target.permissions, ok)
                    perms[ok] = ov if ov is not None else pv
                perms = discord.Permissions(**perms)
        for key in to_japanese.keys():
            if (perm := getattr(perms, key, None)) is not None:
                emoji = "✅" if perm else "❌"
                embed.description += f"{emoji} {to_japanese[key]}\n"
        await ctx.send(embed=embed)

    @role.group(hidden=True, name="all")
    @checks.has_perms(administrator=True)
    async def _all(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}role all add @role`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command.name)

    @_all.command(name="add")
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def all_add(self, ctx: commands.Context, roles: commands.Greedy[discord.Role]):
        '''
        全員にロールを付与します(要管理者権限; 10分に1度のみ利用可)
        '''
        if not roles:
            return await self.bot.send_error(
                ctx, "引数が不正です！",
                "全員に付与するロールを最低一つ指定してしてください"
            )
        try:
            await asyncio.gather(*[self.check_roles(ctx, ctx.me, ctx.author, role) for role in roles], return_exceptions=True)
        except:
            pass
        await asyncio.gather(*[m.add_roles(*roles) for m in ctx.guild.members])
        await self.bot.send_notification(
            ctx, "全員へのロール付加が完了しました",
            ", ".join([f"{r.mention}" for r in roles]) +
            "を全メンバーに付加しました"
        )

    @_all.command(name="remove")
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def all_remove(self, ctx: commands.Context, roles: commands.Greedy[discord.Role]):
        '''
        全員からロールをはく奪します(要管理者権限; 10分に1度のみ利用可)
        '''
        if not roles:
            return await self.bot.send_error(
                ctx, "引数が不正です！",
                "全員からはく奪するロールを最低一つ指定してしてください"
            )
        await asyncio.gather(*[self.check_roles(ctx, ctx.me, ctx.author, role) for role in roles])
        try:
            await asyncio.gather(*[m.remove_roles(*roles) for m in ctx.guild.members], return_exceptions=True)
        except:
            pass
        await self.bot.send_notification(
            ctx, "全員からのロールはく奪が完了しました",
            ", ".join([f"{r.mention}" for r in roles]) +
            "を全メンバーからはく奪しました"
        )

    @all_add.error
    @all_remove.error
    async def on_all_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(
                ctx, error, 1, 10
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        roles = await q.JoinRole(self.bot, member.guild.id).get()
        found = [r for role in roles
                 if (r := member.guild.get_role(int(role.role))) is not None]
        await member.add_roles(*found)

    async def check_roles(self, ctx, bot, author, role: discord.Role):
        if role >= bot.top_role:
            ctx.handled = True
            await ctx.bot.send_error(
                ctx, "権限がありません！",
                f"<@&{role.id}>がボットの最高ロールより同じか，高いロールであるため操作できません"
            )
            raise RoleError
        if role >= author.top_role:
            ctx.handled = True
            await ctx.bot.send_error(
                ctx, "権限がありません！",
                f"<@&{role.id}>があなたの最高ロールより同じか，高いロールであるため操作できません"
            )
            raise RoleError
        if role.managed:
            ctx.handled = True
            await ctx.bot.send_error(
                ctx, "権限がありません！",
                f"<@&{role.id}>は外部管理されているロールのため特定ユーザーに対しての付加や削除の操作は許可されていません"
            )
            raise RoleError

    @add.before_invoke
    @remove.before_invoke
    async def role_hierarchy_check(self, ctx: commands.Context):
        _, _, target, role, *_ = ctx.args
        author: discord.Member = ctx.author
        bot: discord.Member = ctx.me
        await self.check_roles(ctx, bot, author, role)

    @join_add.before_invoke
    @join_remove.before_invoke
    async def join_role_hierarchy_check(self, ctx: commands.Context):
        _, _, roles = ctx.args
        author: discord.Member = ctx.author
        bot: discord.Member = ctx.me
        await asyncio.gather(*[self.check_roles(ctx, bot, author, role) for role in roles])


def setup(bot):
    bot.add_cog(Roles(bot))
