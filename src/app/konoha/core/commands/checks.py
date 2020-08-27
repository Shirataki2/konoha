import discord
from discord.ext import commands

import asyncio

import konoha.models.crud as q


def can_ban(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.ban_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_kick(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.kick_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_mute(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.mute_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_manage_guild(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.manage_guild:
            return True
        else:
            return False
    return commands.check(predicate)


def can_manage_message(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.manage_messages:
            return True
        else:
            return False
    return commands.check(predicate)


def is_admin(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.administrator:
            return True
        else:
            return False
    return commands.check(predicate)


def user(column):
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        loop = asyncio.get_event_loop()
        try:
            perm = await q.User(ctx.author.id).get(verbose=0)
        except:
            return False
        return getattr(perm, column, False)
    return commands.check(predicate)
