import discord
from discord.ext import commands, tasks

import asyncio
import re
import io
import os
import aiohttp
import random
import secrets
import random
from PIL import Image
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Pattern

import konoha.models.crud as q
from konoha.cogs.economy import Economy
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import ColorConverter, FontConverter
from konoha.core.utils import TextImageGenerator
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Gambling(commands.Cog):
    '''
    疑似通貨を使ってちょっとした賭けもどきを遊べるコマンドです
    '''
    order = 11

    def __init__(self, bot: Konoha):
        self.bot = bot

    def _subtask(self, ds):
        img = Image.new('RGBA', (len(ds) * 64, 64))
        for i, d in enumerate(ds):
            img2 = Image.open(f'./assets/dice-{d}.png')
            img2 = img2.resize((64, 64))
            img.paste(img2, (64 * i, 0))
        return img

    async def generate_dice_image(self, dices):
        f = io.BytesIO()
        img = await self.bot.loop.run_in_executor(None, self._subtask, dices)
        img.save(f, format="png")
        f.seek(0)
        return f

    @commands.command()
    async def dice(self, ctx: commands.Context, num: int):
        '''
        6面のサイコロを`num`回振ります
        '''
        num = min(10, max(1, num))
        dices = random.choices(range(1, 7), k=num)
        f = await self.generate_dice_image(dices)
        file = discord.File(f, 'dice.png')
        await ctx.send(f'合計は**{sum(dices)}**です！', file=file)

    @dice.error
    async def on_dice_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            return await self.bot.send_error(
                ctx, '引数が不足しています！',
                '`dice`コマンドは6面体サイコロを何回振るかを引数に与える必要があります'
            )
        if isinstance(error, commands.BadArgument):
            ctx.handled = True
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                '`dice`コマンドの`num`引数は1以上10以下の整数である必要があります'
            )

    @commands.command()
    @commands.guild_only()
    async def chinchiro(self, ctx: commands.Context):
        '''
        未来は僕等の手の中......!

        サーバー内疑似通貨を賭けてチンチロリンが遊べます．

        基本的に子が掛け金を入力するだけで自動進行していきます．

        最大10人まで参加可能です．

        ルールは親流れが「一の目,目無し,ヒフミ」を出した際のみで，親は3回連続まで行うことが可能です．(逆に言えばこれらの役が出るまで親を続けないといけません)

        また，ピンゾロは5倍，他のゾロ目は3倍です．

        掛け金は100~1000までとなっています．
        '''
        embed = discord.Embed(
            color=config.theme_color,
            title="チンチロ...!!!",
            description=f'圧倒的参加者募集...!!!\n\nはじめの親は{ctx.author.mention}だ...\n\n' +
                        f'参加希望のやつは5分以内に✋を押せ......!!\n\n' +
                        f'10人以上参加の場合は10人ランダムに抽選する...\n\n' +
                        f'{ctx.author.mention}は人数が集まったら`close`と入力しろ......!!!!'
        )
        economy: Economy = self.bot.get_cog('Economy')
        msg: discord.Message = await ctx.send(embed=embed)
        await msg.add_reaction('✋')
        try:
            closed = await self.bot.wait_for(
                'message',
                check=lambda m: all(
                    [m.content == 'close', m.author == ctx.author]),
                timeout=300
            )
        except asyncio.TimeoutError:
            await ctx.send('時間切れだ...!!!!!!')
        msg = await ctx.fetch_message(msg.id)
        reactions = [r for r in msg.reactions if r.emoji == '✋']
        try:
            users = await reactions[0].users().flatten()
            users = list(
                filter(lambda x: not x.bot and x.id != ctx.author.id, users))
            if len(users) > 9:
                users = random.sample(users, k=9)
        except Exception as e:
            await ctx.send('何やらエラーが起こったようだ...管理者に連絡してみてくれ...!!!')
            raise e
        if len(users) == 0:
            return await ctx.send('誰も参加してないじゃないか...!\n辞めだ......辞めだ...!!!')
        users.append(ctx.author)
        await ctx.send('参加者: '+','.join([f'{user.name}' for user in users]))
        await asyncio.sleep(1)
        await ctx.send('これよりゲームを始める...')
        await asyncio.sleep(1)
        await ctx.send('一巡したらゲーム終了だ...')
        await asyncio.sleep(1)
        await ctx.send('参加者は5秒以内に応答してくれ...')
        await asyncio.sleep(1)
        await ctx.send('応答がないヤツや数字じゃない返信をしたヤツは500ペリカを賭け金として払うものとする...!!!')
        await asyncio.sleep(1)
        n = 0
        for i, parent in enumerate(users[::-1]):
            for k in range(3):
                n += 1
                children = list(set(users) - {parent})
                embed = discord.Embed(
                    title=f'第{n}試合',
                    description=f'親: {parent.mention}\n\n子: {",".join([c.mention for c in children])}',
                    color=config.theme_color,
                )
                moneys = await asyncio.gather(*[economy.get_money(user) for user in users])
                for user, money in zip(users, moneys):
                    embed.description += f'\n\n{user.mention}: {money.amount}ペリカ'
                bit = {u.id: 0 for u in children}
                await ctx.send('子の奴らは賭け金を入力しろ......!!!\n\n最低100ペリカから最高1000ペリカだ...\n\n儲けたい奴は自己責任で借金してもいいぞ......!!', embed=embed)
                msg = await ctx.send('制限時間は5秒だ...\n賭けたい金額を数字だけのメッセージで送信してくれ...!')
                await asyncio.sleep(5)
                msgs = await ctx.channel.history(after=msg).flatten()
                await ctx.send('賭け金を確認する......')
                await asyncio.sleep(1)
                for msg in msgs:
                    u = msg.author.id
                    if u in bit.keys():
                        try:
                            b = int(msg.content)
                        except:
                            continue
                    else:
                        continue
                    bit[u] = min(1000, max(100, b))
                if all([b > 0 for b in bit.values()]):
                    await ctx.send('全員入力したようだな......!!!')
                    await asyncio.sleep(1)
                else:
                    ni = [k for k, v in bit.items() if v == 0]
                    nc = [f'<@{k}>' for k, v in bit.items() if v == 0]
                    await ctx.send(','.join(nc) + 'が賭けていないようだな')
                    await asyncio.sleep(1)
                    await ctx.send('約束通り500ペリカを賭け金として徴収する......!!!')
                    await asyncio.sleep(1)
                    bit.update({id: 500 for id in ni})
                await ctx.send(f'親: {parent.mention}の番だ......')
                await asyncio.sleep(1)
                for j in range(3):
                    dices = random.choices(range(1, 7), k=3)
                    p_r, r = chinchiro(dices)
                    f = await self.generate_dice_image(dices)
                    await ctx.send(file=discord.File(f, 'result.png'))
                    await asyncio.sleep(1)
                    await ctx.send(p_r)
                    await asyncio.sleep(1)
                    if p_r == '目なし' and j < 2:
                        await ctx.send('もう一度...!')
                        await asyncio.sleep(1)
                    else:
                        break
                embed = discord.Embed(
                    title=f"第{n}試合", color=config.theme_color)
                if p_r[-2:] == 'ゾロ':
                    await ctx.send('何たる幸運...!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}により子の賭け金の{r}倍の額をゲット！')
                    embed.description = f'親: {parent.mention} **+{sum(bit.values()) * r}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, sum(bit.values()) * r, True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **-{v*r}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, -v*r, True) for u, v in bit.items()])
                    await asyncio.sleep(1)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    continue
                if p_r == '出目: 6':
                    await ctx.send('出目が6...!!\n\n親の勝利が確定...!!!!!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}により子の賭け金の合計額をゲット！')
                    embed.description = f'親: {parent.mention} **+{sum(bit.values())}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, sum(bit.values()), True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **-{v}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, -v, True) for u, v in bit.items()])
                    await asyncio.sleep(1)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    continue
                if p_r == 'シゴロ':
                    await ctx.send('シゴロ!!!!!!\n\n圧倒的幸運!!\n親の勝利が確定...!!!!!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}により子の賭け金の倍額をゲット！')
                    embed.description = f'親: {parent.mention} **+{2*sum(bit.values())}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, 2*sum(bit.values()), True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **-{2*v}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, -2*v, True) for u, v in bit.items()])
                    await asyncio.sleep(1)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    continue
                if p_r == '出目: 1':
                    await ctx.send('出目が1...!!\n\n親の敗北が確定...!!!!!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}によりそれぞれの子に賭け金分の支払いが確定...!!!')
                    embed.description = f'親: {parent.mention} **-{sum(bit.values())}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, -sum(bit.values()), True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **+{v}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, v, True) for u, v in bit.items()])
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    break
                if p_r == 'ヒフミ':
                    await ctx.send('惨憺たる悲劇!!\n\n親の敗北が確定...!!!!!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}によりそれぞれの子に賭け金の倍額分の支払いが確定...!!!')
                    embed.description = f'親: {parent.mention} **-{2*sum(bit.values())}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, -2*sum(bit.values()), True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **+{2*v}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, 2*v, True) for u, v in bit.items()])
                    await asyncio.sleep(1)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    break
                if p_r == '目なし':
                    await ctx.send('圧倒的不運!!\n\n役に恵まれず親の敗北が確定...!!!!!!')
                    await asyncio.sleep(1)
                    await ctx.send(f'{parent.mention} {p_r}によりそれぞれの子に賭け金分の支払いが確定...!!!')
                    embed.description = f'親: {parent.mention} **-{sum(bit.values())}**ペリカ\n\n'
                    await economy.update_money_by_id(ctx.guild.id, parent.id, -sum(bit.values()), True)
                    for u, v in bit.items():
                        embed.description += f'<@{u}>: **+{v}**ペリカ\n'
                    await asyncio.gather(*[economy.update_money_by_id(ctx.guild.id, u, v, True) for u, v in bit.items()])
                    await asyncio.sleep(1)
                    await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                    break
                await ctx.send(f'親の{p_r}\nこれを超す出目を出せば子の勝利は確定...!!!')
                await asyncio.sleep(1)
                for child in children:
                    b = bit[child.id]
                    await ctx.send(f'子: {child.mention}の番だ......')
                    await asyncio.sleep(1)
                    for j in range(3):
                        dices = random.choices(range(1, 7), k=3)
                        c_r, r1 = chinchiro(dices)
                        f = await self.generate_dice_image(dices)
                        await ctx.send(file=discord.File(f, 'result.png'))
                        await asyncio.sleep(1)
                        await ctx.send(c_r)
                        await asyncio.sleep(1)
                        if c_r == '目なし' and j < 2:
                            await ctx.send('もう一度...!')
                            await asyncio.sleep(1)
                        else:
                            break
                    if c_r[-2:] == 'ゾロ':
                        await ctx.send('圧倒的幸運...!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカの{r}倍の額をゲット！')
                        embed.description = f'子: {child.mention} **+{b * r1}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, b * r, True)
                        embed.description += f'親: {parent.mention} **-{b*r1}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, -b * r, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    if c_r == '出目: 6':
                        await ctx.send('何たる幸運...!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカと同額をゲット！')
                        embed.description = f'子: {child.mention} **+{b}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, b, True)
                        embed.description += f'親: {parent.mention} **-{b}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, -b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    if c_r == 'シゴロ':
                        await ctx.send('シゴロ!!!!!!\n\n圧倒的幸運!!\n倍額勝利が確定...!!!!!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカの2倍の額をゲット！')
                        embed.description = f'子: {child.mention} **+{b * 2}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, b * 2, True)
                        embed.description += f'親: {parent.mention} **-{b*2}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, -b * 2, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    if c_r == '出目: 1':
                        await ctx.send('出目が1...!!\n\n敗北......!!!!!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカの没収...!!!')
                        embed.description = f'子: {child.mention} **-{b}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, -b, True)
                        embed.description += f'親: {parent.mention} **+{b}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    if c_r == 'ヒフミ':
                        await ctx.send('嗚呼...悲劇!!\n\n倍額没収が確定...!!!!!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカの倍額が没収...!!!')
                        embed.description = f'子: {child.mention} **-{b*2}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, -b*2, True)
                        embed.description += f'親: {parent.mention} **+{b*2}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, 2*b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    if c_r == '目なし':
                        await ctx.send('圧倒的不運!!\n\n役に恵まれず敗北が確定...!!!!!!')
                        await asyncio.sleep(1)
                        await ctx.send(f'{child.mention} {c_r}により賭け金{b}ペリカが没収...!!!')
                        embed.description = f'子: {child.mention} **-{b}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, -b, True)
                        embed.description += f'親: {parent.mention} **+{b}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                        continue
                    await ctx.send(f'{child.mention}の{c_r} (親の{p_r})')
                    await asyncio.sleep(1)
                    if r < r1:
                        await ctx.send(f'{child.mention}の勝利!!!賭け金{b}ペリカをゲット！')
                        await asyncio.sleep(1)
                        embed.description = f'子: {child.mention} **+{b}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, b, True)
                        embed.description += f'親: {parent.mention} **-{b}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, -b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                    elif r > r1:
                        await ctx.send(f'{child.mention}の敗北!!!賭け金{b}ペリカを没収！')
                        await asyncio.sleep(1)
                        embed.description = f'子: {child.mention} **-{b}**ペリカ\n\n'
                        await economy.update_money_by_id(ctx.guild.id, child.id, -b, True)
                        embed.description += f'親: {parent.mention} **+{b}**ペリカ\n'
                        await economy.update_money_by_id(ctx.guild.id, parent.id, b, True)
                        await asyncio.sleep(1)
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                    else:
                        await ctx.send('なんとこの勝負...引き分け...!!!')
                        await asyncio.sleep(1)
        embed = discord.Embed(
            title=f'全試合終了......!!!',
            description='',
            color=config.theme_color,
        )
        moneys = await asyncio.gather(*[economy.get_money(user) for user in users])
        for user, money in zip(users, moneys):
            embed.description += f'\n\n{user.mention}: {money.amount}ペリカ'
        await ctx.send(embed=embed)


def chinchiro(dices):
    dices = sorted(dices)
    n = set(dices)
    if len(n) == 1:
        if 1 in n:
            return 'ピンゾロ', 5
        if 2 in n:
            return 'ニゾロ', 3
        if 3 in n:
            return 'サンゾロ', 3
        if 4 in n:
            return 'ヨンゾロ', 3
        if 5 in n:
            return 'ゴゾロ', 3
        if 6 in n:
            return 'ロクゾロ', 3
    for i in range(1, 7):
        if dices.count(i) == 2:
            for j in range(1, 7):
                if dices.count(j) == 1:
                    return f'出目: {j}', j
    if dices == [1, 2, 3]:
        return 'ヒフミ', 2
    if dices == [4, 5, 6]:
        return 'シゴロ', 2
    return '目なし', 1


def setup(bot):
    bot.add_cog(Gambling(bot))
