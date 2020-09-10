import discord
from discord.ext import commands

import asyncio

import konoha.models.crud2 as q
from konoha.core.exceptions import MissingPermissions, BotMissingPermissions


def _has_permissions(ctx, **perms):
    ch = ctx.channel
    permissions = ch.permissions_for(ctx.author)

    missing = [perm for perm, value in perms.items(
    ) if getattr(permissions, perm) != value]

    if not missing:
        return True

    raise MissingPermissions(missing)


def _bot_has_permissions(ctx, **perms):
    guild = ctx.guild
    me = guild.me if guild is not None else ctx.bot.user
    permissions = ctx.channel.permissions_for(me)

    missing = [perm for perm, value in perms.items(
    ) if getattr(permissions, perm) != value]

    if not missing:
        return True

    raise BotMissingPermissions(missing)


def can_ban():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _has_permissions(ctx, ban_members=True)
        return True
    return commands.check(predicate)


def bot_can_ban():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _bot_has_permissions(ctx, ban_members=True)
        return True
    return commands.check(predicate)


def can_kick():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _has_permissions(ctx, kick_members=True)
        return True
    return commands.check(predicate)


def bot_can_kick():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _bot_has_permissions(ctx, kick_members=True)
        return True
    return commands.check(predicate)


def can_manage_guild():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _has_permissions(ctx, manage_guild=True)
        return True
    return commands.check(predicate)


def bot_can_manage_guild():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _bot_has_permissions(ctx, manage_guild=True)
        return True
    return commands.check(predicate)


def can_manage_messages():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _has_permissions(ctx, manage_messages=True)
        return True
    return commands.check(predicate)


def bot_can_manage_messages():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _bot_has_permissions(ctx, manage_messages=True)
        return True
    return commands.check(predicate)


def has_perms(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _has_permissions(ctx, **perms)
        return True
    return commands.check(predicate)


def bot_has_perms(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        _bot_has_permissions(ctx, **perms)
        return True
    return commands.check(predicate)
