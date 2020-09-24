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
                return f"`{self.clean_prefix}{command.name} {command.signature}`"
            if not command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name}`"
            if command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name} {command.signature}`"
        else:
            if not command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name}`"
            if command.signature and not command.parent:
                return f"`{self.clean_prefix}{command.name} {command.signature}`"
            if not command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name}`"
            if command.signature and command.parent:
                return f"`{self.clean_prefix}{command.parent} {command.name} {command.signature}`"

    def get_command_aliases(self, command: commands.Command):
        if not command.aliases:
            return ""
        else:
            return f"Alias: {', '.join(command.aliases)}"

    def get_command_description(self, command: commands.Command):
        if not command.short_doc:
            return "このコマンドの説明はありません\n\n"
        else:
            return command.short_doc.format(prefix=self.clean_prefix) + "\n\n"

    def get_command_help(self, command: commands.Command):
        if not command.help:
            return "このコマンドの説明はありません"
        else:
            return command.help.format(prefix=self.clean_prefix)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        cogs = [bot.get_cog(cog) for cog in bot.cogs]
        cogs.sort(key=lambda cog: cog.order)
        commands = [command for command in await self.filter_commands(bot.commands)]
        paginator = EmbedPaginator(
            footer=f"{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます",
            author=f"Help | Page $p / $P ({len(commands)} commands)",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        i = -1
        for cog in cogs:
            runnables = []
            for c in cog.walk_commands():
                try:
                    if await c.can_run(ctx) and not c.hidden:
                        runnables.append(c)
                except:
                    continue
            if len(runnables) == 0:
                continue
            j = 0
            i += 1
            prev = None

            def new_page():
                paginator.new_page()
                paginator.content[i]["title"] = f"Category: {cog.qualified_name}"
                if cog.description:
                    paginator.content[i]["description"] = cog.description \
                        .split('\n')[0] \
                        .format(prefix=self.clean_prefix)
                else:
                    paginator.content[i]["description"] = None
            new_page()
            cog: commands.Cog
            for c in runnables:
                if c.name == prev:
                    continue
                try:
                    s = self.get_command_signature(c)
                    d = self.get_command_description(c)
                    a = self.get_command_aliases(c)
                    j += 1
                    if j > 0 and j % 10 == 0:
                        i += 1
                        new_page()
                    if c.aliases:
                        paginator.add_row_manually(
                            f"{s}    `({a})`", d, page=i)
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
            title=f"Category: {cog.qualified_name}",
            footer=f"{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます",
            author="Help",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        paginator.new_page()
        paginator.content[0]["description"] = cog.description.format(
            prefix=self.clean_prefix)
        prev = None
        prev2 = None
        for c in commands:
            if c.name == prev and c.parent == prev2:
                continue
            try:
                if await c.can_run(ctx) and not c.hidden:
                    s = self.get_command_signature(c)
                    a = self.get_command_aliases(c)
                    d = self.get_command_description(c)
                    if c.aliases:
                        paginator.add_row_manually(
                            f"{s}    `({a})`", d, page=0)
                    else:
                        paginator.add_row_manually(f"{s}", d, page=0)
            except:
                pass
            prev = c.name
            prev2 = c.parent
        await paginator.paginate(ctx)

    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        paginator = EmbedPaginator(
            title=f"Command: {self.clean_prefix}{command.qualified_name}",
            footer=f"{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます",
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
            footer=f"{self.clean_prefix}help コマンド名 でコマンドの詳細が表示されます",
            author="Help",
            icon=str(ctx.bot.user.avatar_url),
            color=config.theme_color
        )
        paginator.new_page()
        if group.aliases:
            paginator.content[0]["description"] = f"`Alias: {', '.join(group.aliases)}`\n\n"
        paginator.content[0]["description"] += ctx.bot.get_command(
            group.name).help.format(prefix=self.clean_prefix)
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
                              description=f'"{string}" という名のコマンドは存在しません',
                              color=0xff0000)
        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        pass
