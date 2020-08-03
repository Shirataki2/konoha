import discord
from discord.ext import commands


def can_ban(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.ban_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_kick(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.kick_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_mute(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.mute_members:
            return True
        else:
            return False
    return commands.check(predicate)


def can_manage_guild(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.manage_guild:
            return True
        else:
            return False
    return commands.check(predicate)


def can_manage_message(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.manage_messages:
            return True
        else:
            return False
    return commands.check(predicate)


def is_admin(**perms):
    def predicate(ctx):
        p: discord.Permissions = ctx.message.author.guild_permissions
        if p.administrator:
            return True
        else:
            return False
    return commands.check(predicate)
