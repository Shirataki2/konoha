import discord
from discord.ext import commands

import re
import os
import io
import asyncio
import subprocess
import tabulate
import aiomysql
import random
import glob
import json
import wavelink
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from pathlib import Path
from time import perf_counter

import konoha
import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.utils import TextImageGenerator
from konoha.core.utils.circularizer import Circularizer
from konoha.core.bot.konoha import Konoha, Word
from konoha.core.commands import checks
from konoha.core.converters import DurationToSecondsConverter, ColorConverter
from konoha.core.log.logger import get_module_logger
import aiohttp
logger = get_module_logger(__name__)


async def get_duration(coro, *args, **kwargs):
    start = perf_counter()
    ret = await coro(*args, **kwargs)
    end = perf_counter()
    return (end - start) * 1000, ret


class Test(commands.Cog):
    '''
    実験中の機能
    '''
    order = 100

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command(hidden=True)
    async def tmp(self, ctx: commands.Context):
        msg = await self.bot.wait_for(
            'message',
            check=lambda m: \
                m.channel.id == 756602618918469645 and
                m.author.id == 756592679160119386 and 
                m.embeds and
                m.embeds[0].fields
        )
        print(msg)


    @commands.group(hidden=True)
    async def dev(self, ctx: commands.Context):
        pass


    @dev.command(hidden=True)
    async def markov(self, ctx: commands.Context, user: discord.Member = None, channel: discord.TextChannel = None, N: int = 100):
        if channel is None:
            channel = ctx.channel
        words = {}
        start = []
        msg = await ctx.send("収集中...")
        N = max(1, min(1000, N))
        i = 1
        async for message in channel.history(limit=N):
            if user is not None and message.author != user:
                continue
            if message.author.bot:
                continue
            tokens = await self.bot.morph(message.content)
            tokens.append(Word.eos())
            start.append(tokens[0])
            if random.random() > 0.992:
                await msg.edit(content=f"収集中...({i/N:.1f} %)")
            for w, nx in zip(tokens[:-1], tokens[1:]):
                if w.name in words:
                    words[w.name].append(nx)
                else:
                    words[w.name] = [nx]
            i += 1
        await msg.edit(content="自動生成されたメッセージ:")
        word = random.choice(start)
        sentence = word.name
        while len(sentence) < 300 and word.yomi != "#EOS#":
            word = random.choice(words[word.name])
            if word.name != "#EOS#":
                sentence += word.name
        await ctx.send(sentence)

    @dev.group()
    async def stat(self, ctx: commands.Context):
        pass

    @stat.group(aliases=["freq"])
    async def frequency(self, ctx: commands.Context):
        pass

    @frequency.command(aliases=["m"])
    async def message(self, ctx: commands.Context, channel: discord.TextChannel = None, N: int = 2000):
        if channel is None:
            channel = ctx.channel
        emb_message = await ctx.send(f'{self.bot.custom_emojis.loading} 集計中...')
        messages = []
        N = max(1, min(10000, N))
        i = 0
        async for msg in channel.history(limit=N):
            i += 1
            messages.append(msg)
            if random.random() > 0.997:
                await emb_message.edit(content=f'{self.bot.custom_emojis.loading} 集計中... ({100*i/N:.1f} %)')
        await emb_message.edit(content=f'{self.bot.custom_emojis.loading} 集計中... (100.0 %)')
        heatmap = np.zeros((7, 24)).astype(np.int64)
        for message in messages:
            t = message.created_at + timedelta(hours=9)
            wd = t.weekday()
            h = t.hour
            heatmap[wd, h] += 1
        heatmap = heatmap[::-1]
        fig, ax = plt.subplots(figsize=(14, 6))
        fig.suptitle(f"#{channel.name} の活発な時間帯 (直近{N}件)", fontsize=26)
        hm = ax.pcolor(heatmap, cmap="BuGn")
        ax.set_xticks(np.arange(24) + 0.5, minor=False)
        ax.set_yticks(np.arange(7) + 0.5, minor=False)
        ax.set_yticklabels(list("月火水木金土日")[::-1], minor=False, size="14")
        ax.set_xticklabels([f"{i:02d}:00" for i in range(24)], minor=False, size="12")
        for i in range(7):
            for j in range(24):
                c = "w" if heatmap[i, j] / heatmap.max() > 0.7 else "k"
                text = ax.text(j+.5, i+.5, heatmap[i, j],
                               ha="center", va="center", size="14", color=c)
        tempfile = io.BytesIO()
        plt.tight_layout()
        plt.savefig(tempfile, format='png')
        tempfile.seek(0)
        plt.close(fig)
        await emb_message.delete()
        await ctx.send(file=discord.File(tempfile, filename='chart.png'))
        
    @frequency.command(aliases=["u"])
    async def user(self, ctx: commands.Context, channel: discord.TextChannel = None, N: int = 2000):
        if channel is None:
            channel = ctx.channel
        emb_message = await ctx.send(f'{self.bot.custom_emojis.loading} 集計中...')
        messages = []
        N = max(1, min(10000, N))
        i = 0
        async for msg in channel.history(limit=N):
            i += 1
            if msg.author.bot:
                continue
            messages.append(msg)
            if random.random() > 0.997:
                await emb_message.edit(content=f'{self.bot.custom_emojis.loading} 集計中... ({100*i/N:.1f} %)')
        if len(messages) == 0:
            await emb_message.delete()
            return await self.bot.send_error(ctx, "どうやらBOT以外のユーザーの発言は無いようです")
        await emb_message.edit(content=f'{self.bot.custom_emojis.loading} 集計中... (100.0 %)')
        users = {}
        for message in messages:
            atr = message.author
            if atr.id in users.keys():
                users[atr.id]["ctr"] += 1
            else:
                users[atr.id] = {
                    "name": atr.name,
                    "icon": atr.avatar_url,
                    "ctr": 1
                }
        users = sorted(list(users.values()), key=lambda x: -x["ctr"])[:10]
        r = []
        images = []
        await emb_message.edit(content=f'{self.bot.custom_emojis.loading} レンダリング中...')
        for user in users:
            icon = await user["icon"].read()
            if icon:
                images.append(Image.open(io.BytesIO(icon)).convert('RGB'))
            else:
                gen = TextImageGenerator(
                    "./fonts/NotoSansCJKjp-Bold.otf",
                    fg_color=(255,255,255),
                    bg_color=(0, 0, 255),
                    offset=34
                )  # type: ignore
                img = await self.bot.loop.run_in_executor(None, gen.render)
                images.append(img)
            r.append(user["ctr"])
        r = np.array(r)
        r = r / r.max()
        r = r ** 1.2
        c = Circularizer(r, images)
        await self.bot.loop.run_in_executor(None, c.minimize)
        img = await self.bot.loop.run_in_executor(None, c.plot, 1024)
        tempfile = io.BytesIO()
        img.save(tempfile, format='png')
        tempfile.seek(0)
        await emb_message.delete()
        embed = discord.Embed(description="", title=f"#{channel.name}での発言ランキングBEST10", color=config.theme_color)
        embed.set_footer(text=f"直近{N}件のメッセージから記録を取っています")
        for i, user in enumerate(users[:10]):
            icon = "🥇🥈🥉４５６７８９*"[i].replace("*", "10")
            embed.description += f"`{icon}　 {user['name']}`\n `　　　　　　　　　　　　　　　　　　　　　... {user['ctr']}回`\n"
        await ctx.send(embed=embed, file=discord.File(tempfile, filename='chart.png'))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id == 756602618918469645 and message.attachments and len(message.attachments) >= 2:
            api_key = "ea4e09a2-733b-40d0-9af1-a3a3679c780f"
            async with self.bot.session.post(
                "https://api.deepai.org/api/fast-style-transfer", 
                data={
                    'content': message.attachments[0].url,
                    'style': message.attachments[1].url
                }, 
                headers={
                    "Api-Key": api_key,
                }
            ) as resp:
                data = await resp.json()
                await message.channel.send(data["output_url"])
            try:
                print(data)
            except KeyError:
                pass

def setup(bot):
    bot.add_cog(Test(bot))
