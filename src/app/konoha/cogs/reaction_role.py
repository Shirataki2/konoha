import discord
from discord.ext import commands

import re
import os
import asyncio
import subprocess
import tabulate
import aiomysql
import glob
import secrets
import json
from copy import deepcopy
from itertools import chain
from emoji import UNICODE_EMOJI, EMOJI_UNICODE, demojize, emojize  # type: ignore
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List, Union
from pathlib import Path
from time import perf_counter

import konoha
import konoha.models.crud2 as q
from konoha.core.utils.consts import alphabet_emojis, number_emojis
from konoha.core.utils.pagination import EmbedPaginator
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


class ReactionRole(commands.Cog):
    '''
    リアクションでロール付与を行うメッセージを作成します
    '''
    order = 20

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.group(aliases=["rp"])
    @checks.bot_has_perms(manage_messages=True, manage_roles=True)
    async def role_panel(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}role_panel new`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help("RolePanel")

    @role_panel.command(
        name='new',
        usage=('<description> <emoji1> <role1> '
               '[emoji2] [role2]...')
    )
    @checks.has_perms(manage_roles=True)
    async def _new(self, ctx: commands.Context, *arg_tuple):
        '''
        新たにReaction Role Panelを作成します．
        '''
        args: List[str] = list(arg_tuple)
        if len(args) == 0:
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                'このコマンドは`Reaction Role Panelに載せる説明`の後に，`役職を表す絵文字`,`役職名`' +
                'を対で指定する必要があります．\n\n' +
                '例:\nkd:rp new どちらが好きですか? 🍄 @きのこ 🎋 @たけのこ'
            )
        description = args.pop(0)
        if len(args) % 2 != 0 or not args:
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                'このコマンドは`Reaction Role Panelに載せる説明`の後に，`役職を表す絵文字`,`役職名`' +
                'を対で指定する必要があります．\n\n' +
                '例:\nkd:rp new どちらが好きですか? 🍄 @きのこ 🎋 @たけのこ'
            )
        emojis, roles = args[::2], args[1::2]
        if len(emojis) != len(set(emojis)):
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                '絵文字が重複しています！'
            )
        role_table = []
        if len(emojis) > 20:
            return await self.bot.send_error(
                ctx, "引数が多すぎです！"
                "ロールは最大20個まで指定可能です"
            )
        for _emoji, _role in zip(emojis, roles):
            if not isinstance(_role, discord.Role):
                role: discord.Role = await commands.RoleConverter().convert(ctx, _role)
            else:
                role = _role
            try:
                emoji: discord.Emoji = await commands.EmojiConverter().convert(ctx, _emoji)
                role_table.append(
                    {'emoji': emoji.id, 'custom': True, 'role': role.id, 'original': emoji})
            except commands.BadArgument:
                if _emoji in UNICODE_EMOJI:  # types: ignore
                    emoji = UNICODE_EMOJI[_emoji]  # types: ignore
                else:
                    return await self.bot.send_error(
                        ctx, '引数が不正です！',
                        f'{_emoji}を絵文字として解釈できませんでした' +
                        '\n\nカスタム絵文字はBotがそのサーバーに入っていない場合，使用することはできません'
                    )
                role_table.append(
                    {'emoji': emoji, 'custom': False, 'role': role.id, 'original': _emoji})
        embed = discord.Embed(title='Reaction Role Panel',
                              description=description+'\n\n',
                              color=config.theme_color)
        panel_id = secrets.token_hex(12)[:12]
        embed.set_author(
            name=f'Panel ID: {panel_id}', icon_url=self.bot.user.avatar_url)
        for d in role_table:
            embed.description += f'{d["original"]} <@&{d["role"]}>\n'
        msg = await ctx.send(embed=embed)
        payload = [{'emoji': e["emoji"], 'custom': e["custom"],
                    'role': e["role"]} for e in role_table]
        await q.RolePanel.create(self.bot, panel_id, ctx.guild.id, ctx.channel.id, msg.id, ctx.author.id, json.dumps(payload))
        for d in role_table:
            await msg.add_reaction(d['original'])

    @role_panel.command(
        name='simple',
        usage=('[description] <role1> [role2]...')
    )
    @checks.has_perms(manage_roles=True)
    async def simple(self, ctx: commands.Context, description: Union[discord.Role, str], *roles: commands.Greedy[discord.Role]):
        '''
        A, B, C ... が選択肢のReaction Role Panelを新たに作成します
        '''
        if isinstance(description, str):
            args = [description] + \
                list(chain.from_iterable(zip(alphabet_emojis, roles)))
        else:
            args = [" "] + list(chain.from_iterable(
                zip(alphabet_emojis, [description]+list(roles))))
        await self._new(ctx, *args)

    @role_panel.command(
        name='num',
        usage=('[description] <role1> [role2]...')
    )
    @checks.has_perms(manage_roles=True)
    async def num(self, ctx: commands.Context, description: Union[discord.Role, str], *roles: commands.Greedy[discord.Role]):
        '''
        1, 2, 3 ... が選択肢のReaction Role Panelを新たに作成します
        '''
        if isinstance(description, str):
            l = len(roles)
            args = [description] + \
                list(chain.from_iterable(zip(number_emojis[1:], roles)))
        else:
            l = len(roles) + 1
            args = [" "] + list(chain.from_iterable(
                zip(number_emojis[1:], [description]+list(roles))))
        if l > 10:
            return await self.bot.send_error(
                ctx, "引数が多すぎです！"
                "ロールは最大10個まで指定可能です"
            )
        await self._new(ctx, *args)

    @role_panel.command(name='list')
    async def _list(self, ctx: commands.Context):
        '''
        作成したReaction Role Panelの一覧を表示します
        '''
        rps = await q.RolePanel.search(self.bot, guild=ctx.guild.id)
        paginator = EmbedPaginator(
            title="Reaction Role Panel List", footer="Page $p / $P")
        paginator.new_page()
        for rp in rps:
            user = ctx.guild.get_member(int(rp.user))
            channel = ctx.guild.get_channel(int(rp.channel))
            rp_payload = json.loads(rp.payload)
            roles = ", ".join(
                ["<@&{role}>".format(role=item["role"]) for item in rp_payload]
            )
            try:
                message = await channel.fetch_message(int(rp.message))
                paginator.add_row(
                    k=f"ID: {rp.id} by {user.name}",
                    v=f"[メッセージへジャンプ！]({message.jump_url})\n{roles}"
                )
            except discord.NotFound:
                paginator.add_row(
                    k=f"ID: {rp.id} by {user.name}",
                    v=f"メッセージは削除されているようです\n{roles}"
                )
        await paginator.paginate(ctx)

    @role_panel.command()
    async def delete(self, ctx: commands.Context, id: str):
        '''
        指定したIDのReaction Role Panelを削除します
        '''
        rps = await q.RolePanel.search(self.bot, id=id)
        if not rps:
            return await ctx.send('指定したIDのReaction Role Panelはありません', delete_after=3.)
        rp = rps[0]
        channel = ctx.guild.get_channel(int(rp.channel))
        try:
            _, message = await asyncio.gather(
                q.RolePanel(self.bot, rp.message).delete(),
                channel.fetch_message(int(rp.message))
            )
            await message.delete()
        except discord.NotFound:
            await q.RolePanel(self.bot, rp.message).delete(),
        await ctx.send('指定したIDのReaction Role Panelを削除しました', delete_after=3.)

    @delete.error
    async def on_delete_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が足りません！",
                "削除するメッセージのIDを指定してください"
            )

    @role_panel.command()
    async def add(self, ctx: commands.Context, id: str, emoji: str, role: discord.Role):
        '''
        指定したIDのReaction Role Panelに新たに選択肢を追加します
        '''
        rps = await q.RolePanel.search(self.bot, id=id)
        if not rps:
            return await ctx.send('指定したIDのReaction Role Panelはありません', delete_after=3.)
        rp = rps[0]
        rp_payload = json.loads(rp.payload)
        channel = ctx.guild.get_channel(int(rp.channel))
        try:
            message: discord.Message = await channel.fetch_message(int(rp.message))
        except discord.NotFound:
            return await self.bot.send_error(
                ctx, "メッセージは既に削除されています",
                "ロールを付与するメッセージが削除されてしまっているようです"
            )
        embed = message.embeds[0]
        try:
            r_emoji: discord.Emoji = await commands.EmojiConverter().convert(ctx, emoji)
            rp_payload.append(
                {'emoji': r_emoji.id, 'custom': True,
                    'role': role.id}
            )
            orig = r_emoji
            embed.description += f'\n{r_emoji} <@&{role.id}>\n'
        except commands.BadArgument:
            if emoji in UNICODE_EMOJI:  # types: ignore
                r_emoji = UNICODE_EMOJI[emoji]  # types: ignore
            else:
                return await self.bot.send_error(
                    ctx, '引数が不正です！',
                    f'{emoji}を絵文字として解釈できませんでした' +
                    '\n\nカスタム絵文字はBotがそのサーバーに入っていない場合，使用することはできません'
                )
            rp_payload.append(
                {'emoji': r_emoji, 'custom': False,
                    'role': role.id}
            )
            embed.description += f'\n{emoji} <@&{role.id}>\n'
            orig = emoji
        emojis = [d["emoji"] for d in rp_payload]
        if len(emojis) != len(set(emojis)):
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                '絵文字が重複しています！'
            )
        await asyncio.gather(
            q.RolePanel(self.bot, rp.message).set(
                payload=json.dumps(rp_payload)),
            message.edit(embed=embed),
            message.add_reaction(orig),
            ctx.message.add_reaction('✅'),
        )
        await asyncio.sleep(2)
        await ctx.message.remove_reaction('✅', ctx.bot.user)

    @add.error
    async def on_add_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が足りません！",
                "絵文字を追加するReaction Role PanelのIDと，絵文字とロールの対を" +
                "引数として与えてください"
            )

    @role_panel.command()
    async def remove(self, ctx: commands.Context, id: str, emoji: str):
        '''
        指定したIDのReaction Role Panelから指定した絵文字の選択肢を削除します
        '''
        rps = await q.RolePanel.search(self.bot, id=id)
        if not rps:
            return await ctx.send('指定したIDのReaction Role Panelはありません', delete_after=3.)
        rp = rps[0]
        rp_payload = json.loads(rp.payload)
        channel = ctx.guild.get_channel(int(rp.channel))
        try:
            message: discord.Message = await channel.fetch_message(int(rp.message))
        except discord.NotFound:
            return await self.bot.send_error(
                ctx, "メッセージは既に削除されています",
                "ロールを付与するメッセージが削除されてしまっているようです"
            )
        embed = message.embeds[0]
        desc = demojize(embed.description)
        try:
            r_emoji: discord.Emoji = await commands.EmojiConverter().convert(ctx, emoji)
            orig = r_emoji
            _orig = orig
            desc = demojize(embed.description)
            check = str(orig) in embed.description
            new_payload = []
            for d in rp_payload:
                if d["emoji"] != _orig.id:
                    new_payload.append(d)
        except commands.BadArgument:
            if emoji in UNICODE_EMOJI:  # types: ignore
                r_emoji = UNICODE_EMOJI[emoji]  # types: ignore
            else:
                return await self.bot.send_error(
                    ctx, '引数が不正です！',
                    f'{emoji}を絵文字として解釈できませんでした' +
                    '\n\nカスタム絵文字はBotがそのサーバーに入っていない場合，使用することはできません'
                )
            orig = emoji
            _orig = demojize(orig)

            for i, n in enumerate(['zero', 'one', 'two', 'three', 'four',
                                   'five', 'six', 'seven', 'eight', 'nine']):
                desc = desc.replace(f"digit_{n}", str(i))
                _orig = _orig.replace(f"digit_{n}", str(i))
            check = str(_orig) in desc
            new_payload = []
            for d in rp_payload:
                demoji = d["emoji"]
                for i, n in enumerate(['zero', 'one', 'two', 'three', 'four',
                                       'five', 'six', 'seven', 'eight', 'nine']):
                    if isinstance(demoji, str):
                        demoji = demoji.replace(f"digit_{n}", str(i))
                    else:
                        demoji = d["emoji"]
                if demoji != _orig:
                    new_payload.append(d)
        if not check:
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                f'{emoji}は指定したReaction Role Panelに登録されていない絵文字です'
            )
        ptn = str(_orig) + r'.*?\n'
        embed.description = emojize(re.sub(ptn, '', desc))
        await asyncio.gather(
            q.RolePanel(self.bot, rp.message).set(
                payload=json.dumps(new_payload)),
            message.edit(embed=embed),
            message.clear_reaction(orig),
            ctx.message.add_reaction('✅'),
        )
        await asyncio.sleep(2)
        await ctx.message.remove_reaction('✅', ctx.bot.user)

    @add.error
    async def on_remove_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が足りません！",
                "絵文字を削除するReaction Role PanelのIDと，対象の絵文字を" +
                "引数として与えてください"
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.member.bot:
            return
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        if not message.author.bot:
            return
        rp = await q.RolePanel(self.bot, payload.message_id).get()
        if not rp:
            return
        rp_payload = json.loads(rp.payload)
        member: discord.Member = guild.get_member(payload.user_id)
        emoji = payload.emoji
        role = None
        try:
            print(emoji)
            _emoji = UNICODE_EMOJI[emoji.name]
            print(_emoji)
            for d in rp_payload:
                if d["emoji"] == _emoji:
                    role = guild.get_role(d["role"])
        except:
            for d in rp_payload:
                if d["emoji"] == emoji.id:
                    role = guild.get_role(d["role"])
        if role is None:
            logger.error('ロールの付与時に不具合が発生しました')
            logger.error(rp.payload)
            return
        if role not in member.roles:
            await member.add_roles(role)
            await channel.send(f'{member.mention}に{role.mention}の役職を付与しました', delete_after=5., allowed_mentions=discord.AllowedMentions(roles=False))
        else:
            await member.remove_roles(role)
            await channel.send(f'{member.mention}から{role.mention}の役職を削除しました', delete_after=5., allowed_mentions=discord.AllowedMentions(roles=False))
        await message.remove_reaction(emoji, member)


def setup(bot):
    bot.add_cog(ReactionRole(bot))
