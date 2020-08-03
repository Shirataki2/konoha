import discord
from discord.ext import commands

from typing import List

from konoha.core import config
from konoha.core.utils.pagination import EmbedPaginator

class CustomHelpCommand(commands.HelpCommand): 
    def __init__(self):
        super(CustomHelpCommand, self).__init__(command_attrs={
            "help": "コマンドに関するヘルプを表示します"
        })

    def get_command_signature(self, command: commands.Command, detail=False):
        if not detail:
            if not command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name}`"
            if command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name}` `{command.signature}`"
            if not command.signature and command.parent:
                return f"`    {command.name}`"
            if command.signature and command.parent:
                return f"`    {command.name}` `{command.signature}`"
        else:
            if not command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name}`"
            if command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name}` `{command.signature}`"
            if not command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name}`"
            if command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name}` `{command.signature}`"
        

    def get_command_aliases(self, command: commands.Command):
        if not command.aliases:
            return ""
        else:
            return f"Alias: {', '.join(command.aliases)}"

    def get_command_description(self, command: commands.Command):
        if not command.short_doc:
            return "このコマンドの説明はありません"
        else:
            return command.short_doc.format(prefix=self.clean_prefix)

    def get_command_help(self, command: commands.Command):
        if not command.help:
            return "このコマンドの説明はありません"
        else:
            return command.help.format(prefix=self.clean_prefix)
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        cogs = list(bot.cogs)
        cogs.sort()
        paginator = EmbedPaginator(
            footer=f"[{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます]",
            author="Help | Page $p / $P",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        i = -1
        for cog_name in cogs:
            cog = bot.get_cog(cog_name)
            commands = [command for command in await self.filter_commands(bot.commands)]
            runnables = [c for c in cog.walk_commands() if await c.can_run(ctx) and not c.hidden]
            if len(runnables) == 0:
                continue
            i += 1
            prev = None
            paginator.new_page()
            paginator.content[i]["title"] = f"About [{cog.qualified_name}]"
            paginator.content[i]["description"] = cog.description
            cog: commands.Cog
            for c in runnables:
                if c.name == prev:
                    continue
                try:
                    s = self.get_command_signature(c)
                    d = self.get_command_description(c)
                    a = self.get_command_aliases(c)
                    if c.aliases:
                        paginator.add_row_manually(f"{s}    `({a})`", d, page=i)
                    else:
                        paginator.add_row_manually(f"{s}", d, page=i)
                except:
                    pass
                prev = c.name
        await paginator.paginate(ctx)

    async def send_cog_help(self, cog):
        ctx = self.context
        commands = [command for command in await self.filter_commands(cog.walk_commands())]
        paginator = EmbedPaginator(
            title=f"About [{cog.qualified_name}]",
            footer=f"[{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます]",
            author="Help",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        paginator.new_page()
        paginator.content[0]["description"] = cog.description
        prev = None
        for c in commands:
            if c.name == prev:
                continue
            try:
                if await c.can_run(ctx) and not c.hidden:
                    s = self.get_command_signature(c)
                    a = self.get_command_aliases(c)
                    d = self.get_command_description(c)
                    if c.aliases:
                        paginator.add_row_manually(f"{s}    `({a})`", d, page=0)
                    else:
                        paginator.add_row_manually(f"{s}", d, page=0)
            except:
                pass
            prev = c.name
        await paginator.paginate(ctx)

    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        paginator = EmbedPaginator(
            title=f"About [{self.clean_prefix}{command.qualified_name}]",
            footer=f"[{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます]",
            author="Help",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        paginator.new_page()
        if await command.can_run(ctx):
            s = self.get_command_signature(command, detail=True)
            a = self.get_command_aliases(command)
            d = self.get_command_help(command)
            if not a:
                paginator.content[0]["description"] = f"{s}\n\n{d}"
            else:
                paginator.content[0]["description"] = f"{s}\n\n`{a}`\n\n{d}"
        await paginator.paginate(ctx)

    async def send_group_help(self, group):
        ctx = self.context
        paginator = EmbedPaginator(
            title=group.name,
            footer=f"[{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます]",
            author="Help",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        paginator.new_page()
        if group.aliases:
            paginator.content[0]["description"] = f"`Alias: {', '.join(group.aliases)}`\n\n"
        paginator.content[0]["description"] += ctx.bot.get_command(group.name).help.format(prefix=self.clean_prefix)
        prev = None
        for c in group.walk_commands():
            if c.name == prev:
                continue
            if await c.can_run(ctx) and not c.hidden:
                s = self.get_command_signature(c)
                a = self.get_command_aliases(c)
                d = self.get_command_description(c)
                if c.aliases:
                    paginator.add_row_manually(f"{s}    `({a})`", d, page=0)
                else:
                    paginator.add_row_manually(f"{s}", d, page=0)
            prev = c.name
        await paginator.paginate(ctx)

    async def command_not_found(self, string):
        embed = discord.Embed(title='コマンドが見つかりませんでした',
                        description=f'**Error 404:** "{string}" という名のコマンドは存在しません',
                        color=0xff0000)
        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        pass