import discord
from discord.ext import commands, tasks

import asyncio
from pytz import timezone
from datetime import datetime
from pybooru import Danbooru

import konoha.models.crud as q
from konoha.core.utils.pagination import EmbedPaginator
from konoha.core.commands import checks
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Reminder(commands.Cog):
    '''
    指定時間にイベントを通知する機能です
    '''

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        self.notifications = [
            {"color": 0x3a47e4, "before": 24*60, "message": "あと1日で以下のイベントが開始します"},
            {"color": 0x379717, "before": 6*60, "message": "あと6時間で以下のイベントが開始します"},
            {"color": 0xf7c417, "before": 60, "message": "あと1時間で以下のイベントが開始します"},
            {"color": 0xff1717, "before": 0, "message": "以下のイベントが開催されます"},
        ]
        # pylint: disable=no-member
        self.notification_task.start()

    def cog_unload(self):
        # pylint: disable=no-member
        self.notification_task.cancel()

    @commands.group(aliases=["rem"])
    @commands.guild_only()
    async def reminder(self, ctx: commands.Context):
        '''
        以下のサブコマンドとともに`{prefix}reminder create`のように実行して下さい
        '''
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=config.theme_color)
            p = await self.bot.get_prefix(ctx.message)
            embed.set_author(name="Reminder コマンド",
                             icon_url=self.bot.user.avatar_url)
            embed.add_field(
                name=f"{p}reminder init", value="メッセージを投稿したチャンネルをリマインダー投稿先に設定", inline=False)
            embed.add_field(name=f"{p}reminder create",
                            value="新規リマインダーの作成", inline=False)
            embed.add_field(name=f"{p}reminder list",
                            value="リマインダーの確認", inline=False)
            embed.add_field(name=f"{p}reminder delete <ID>",
                            value="リマインダーの削除", inline=False)
            return await ctx.send(embed=embed)

    @reminder.command(aliases=["i"])
    @checks.can_manage_guild()
    @commands.guild_only()
    async def init(self, ctx: commands.Context):
        '''
        リマインダーの投稿先を設定します
        このコマンドの投げられたチャンネルがリマインダーの投稿先になります
        '''
        guild: discord.Guild = ctx.guild
        channel: discord.TextChannel = ctx.channel
        if (await q.Reminder(guild.id).update_config(channel.id)) == "create":
            logger.debug(f"[{ctx.guild.id}] リマインダーリスト登録")
            await ctx.send(f"リマインダーの投稿先を{channel.mention}に設定しました")
        else:
            logger.debug(f"[{ctx.guild.id}] リマインダーリスト変更")
            await ctx.send(f"リマインダーの投稿先を{channel.mention}に変更しました")

    @reminder.command(aliases=["c"])
    @commands.guild_only()
    async def create(self, ctx: commands.Context):
        '''
        リマインダーを作成します
        このコマンドの実行後に幾つかの質問を行い，双方向的に作成します．
        '''
        def text_checker(message: discord.Message):
            if len(message.content) > 100:
                logger.debug(f"[{ctx.guild.id}] 100文字以上の送信が行われました")
                return False
            return message.author == ctx.author

        def date_checker(message: discord.Message):
            txt = message.content
            try:
                [_, _, _, _, _] = [int(e) for e in txt.split('-')]
            except:
                return False
            return message.author == ctx.author
        p = await self.bot.get_prefix(ctx.message)
        if (c := await q.Reminder(ctx.guild.id).get_config()) is None:
            return await ctx.send((f"リマインダーを作成する前にリマインダーの初期化を行ってください\n"
                                   f"リマインダーを投稿したいチャンネルで`{p}reminder init`を実行してください．"))
        messages = [ctx.message]
        logger.debug(f"[{ctx.guild.id}] リマインダー作成開始")
        messages.append(await ctx.send("リマインダーを作成します"))
        try:
            messages.append(await ctx.send(("イベントの題名を100文字以内で入力してください\n"
                                            "キャンセルの場合は`cancel`と入力してください")))
            message1 = await self.bot.wait_for("message", check=text_checker, timeout=120)
            t = message1.content
            logger.debug(f"[{ctx.guild.id}] 要件: {t}")
            if t == "cancel":
                messages.append(await ctx.send("リマインダー作成をキャンセルしました"))
                await asyncio.sleep(2)
                messages.append(message1)
                for message in messages:
                    await message.delete()
                return
            else:
                messages.append(message1)
        except Exception as e:
            messages.append(await ctx.send(f"リマインダーの作成に失敗もしくはタイムアウトしました"))
            await asyncio.sleep(2)
            for message in messages:
                await message.delete()
            raise e
        try:
            messages.append(await ctx.send(("開催日時を入力してください\n"
                                            "`2020-08-01-15-00`のように年月日時分を`-`区切りで入力してください"
                                            "キャンセルの場合は`9999-99-99-99-99`と送信してください"
                                            )))
            message2 = await self.bot.wait_for('message', check=date_checker, timeout=300)
            text = message2.content
            logger.debug(f"[{ctx.guild.id}] 日時: {text}")
            if text == '9999-99-99-99-99':
                messages.append(await ctx.send("リマインダー作成をキャンセルしました"))
                await asyncio.sleep(2)
                messages.append(message2)
                for message in messages:
                    await message.delete()
                return
            [y, m, d, H, M] = [int(e) for e in message2.content.split('-')]
            try:
                await q.Reminder(ctx.guild.id).create(
                    user=ctx.author.id,
                    content=message1.content,
                    start_at=datetime(year=y, month=m, day=d, hour=H, minute=M)
                )
            except Exception as e:
                messages.append(await ctx.send(f"日時指定が不正のため作成に失敗しました"))
                messages.append(message2)
                raise e
            embed = discord.Embed(
                title=message1.content,
                color=config.theme_color,
                inline=False
            )
            embed.add_field(name='日時', value=datetime(
                y, m, d, H, M, 0, 0).strftime('%Y/%m/%d %H:%M'))
            embed.add_field(name='作成者', value=ctx.author)
            messages.append(message2)
            channel = ctx.guild.get_channel(int(c.channel))
            logger.debug(f"[{ctx.guild.id}] リマインダー登録完了")
            await channel.send('新しいリマインダーが作成されました', embed=embed)
        except Exception as e:
            raise e
        finally:
            await asyncio.sleep(2)
            for message in messages:
                await message.delete()

    @reminder.command(aliases=["l"])
    @commands.guild_only()
    async def list(self, ctx: commands.Context):
        '''
        開催予定のリマインダーの一覧を表示します
        '''
        p = await self.bot.get_prefix(ctx.message)
        if await q.Reminder(ctx.guild.id).get_config() is None:
            return await ctx.send((f"リマインダーを表示する前にリマインダーの初期化を行ってください\n"
                                   f"リマインダーを投稿したいチャンネルで`{p}reminder init`を実行してください．"))
        reminders, _ = await q.Reminder(ctx.guild.id).list()
        paginator = EmbedPaginator(title="開催予定のイベント", footer="Page $p / $P")
        if len(reminders) == 0:
            return await ctx.send("開催予定のリマインダーはありません")
        paginator.new_page()
        for reminder in reminders:
            paginator.add_row(
                f"{reminder.content}",
                (
                    f"` 開催日時 `: {reminder.start_at.strftime('%Y/%m/%d %H:%M')}\n"
                    f"`  記入者  `: {ctx.guild.get_member(int(reminder.user)).mention}\n"
                    f"`イベントID`: {reminder.id:05d}\n"
                    f"` 登録日時 `: {reminder.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M')}"
                )
            )
        await paginator.paginate(ctx)

    @reminder.command(aliases=["d"])
    @commands.guild_only()
    async def delete(self, ctx: commands.Context, id: int):
        '''
        指定したIDのイベントを削除します
        '''
        p = await self.bot.get_prefix(ctx.message)
        if await q.Reminder(ctx.guild.id).get_config() is None:
            return await ctx.send((f"リマインダーを削除する前にリマインダーの初期化を行ってください\n"
                                   f"リマインダーを投稿したいチャンネルで`{p}reminder init`を実行してください．"))
        reminder = await q.Reminder(ctx.guild.id).get(id)
        if reminder:
            await q.Reminder(ctx.guild.id).delete(id)
            embed = discord.Embed(
                title=reminder.content,
                description=(
                    f"` 開催日時 `: {reminder.start_at.strftime('%Y/%m/%d %H:%M')}\n"
                    f"`  記入者  `: {ctx.guild.get_member(int(reminder.user)).mention}\n"
                    f"`イベントID`: {reminder.id:05d}\n"
                    f"` 登録日時 `: {reminder.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M')}"
                ),
                color=0xff0000
            )
            await ctx.send(
                "以下の予定を削除しました",
                embed=embed
            )
        else:
            await ctx.send("指定したIDのリマインダーが見つかりません")

    @tasks.loop(minutes=1)
    async def notification_task(self):
        for notification in self.notifications:
            reminders = await q.Reminder.search_between_minutes(notification["before"], verbose=0)
            for reminder in reminders:
                c = await q.Reminder.get_config_from_id(reminder.config, verbose=2)
                guild: discord.Guild = await self.bot.fetch_guild(c.guild)
                channel: discord.TextChannel = await self.bot.fetch_channel(c.channel)
                embed = discord.Embed(
                    title=reminder.content,
                    description=(
                        f"` 開催日時 `: {reminder.start_at.strftime('%Y/%m/%d %H:%M')}\n"
                        f"`  記入者  `: {(await guild.fetch_member(int(reminder.user))).mention}\n"
                        f"`イベントID`: {reminder.id:05d}\n"
                        f"` 登録日時 `: {reminder.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M')}"
                    ),
                    color=notification["color"]
                )
                embed.set_author(name=notification["message"])
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Reminder(bot))
