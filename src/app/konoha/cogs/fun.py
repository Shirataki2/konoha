import discord
from discord.ext import commands, tasks

import asyncio
import re
import io
import aiohttp
import random
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Pattern

import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


supported_langs = [
    "DE", "EN-GB", "EN-US", "EN", "FR", "IT",
    "JA", "ES", "NL", "PL", "PT-PT", "PT-BR",
    "PT", "RU", "ZH"
]


class Fun(commands.Cog):
    '''
    娯楽的なコマンドたちです
    '''

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(20, 600, commands.BucketType.guild)
    async def shellgei(self, ctx: commands.Context, *, code: str):
        '''
        シェル芸を走らせます

        Twitterのシェル芸Botと同様，ファイルを送信したら/mediaにファイルが置かれ，

        画像を/imagesに保存すると帰ってきます
        '''
        ptn: Pattern[str] = re.compile('```(.*)?\n((.|\s)*)?```')
        codes = ptn.findall(code)
        if len(codes) == 1:
            _code = codes[0]
            if len(_code) == 3:
                code = _code[1]
        form = aiohttp.FormData()
        form.add_field('source', code)
        if ctx.message.attachments:
            fs = ctx.message.attachments[:4]
            for i, f in enumerate(fs):
                data = await f.read()
                form.add_field(f"f{i}", data)
        async with aiohttp.ClientSession() as session:
            async with session.post('https://bash.chomama.jp/api/run', data=form) as resp:
                data = await resp.json()
        if len(data["stdout"]) > 0:
            if len(data["stdout"].split('\n')) > 20:
                data["stdout"] = "\n".join(
                    data["stdout"].split('\n')[:20]) + "\n..."
            if len(data["stdout"]) > 500:
                data["stdout"] = data["stdout"][:500] + "..."
            await ctx.message.add_reaction('✅')
            await ctx.send(f'**標準出力**\n```\n{data["stdout"]}\n```')
        if len(data["stderr"]) > 0:
            if len(data["stderr"].split('\n')) > 20:
                data["stderr"] = "\n".join(
                    data["stderr"].split('\n')[:20]) + "\n..."
            if len(data["stderr"]) > 500:
                data["stderr"] = data["stderr"][:500] + "..."
            await ctx.message.add_reaction('⚠')
            await ctx.send(f'**標準エラー出力**\n```\n{data["stderr"]}\n```')
        if len(data["images"]) > 0:
            await ctx.message.add_reaction('🖼')
            files = []
            for url in data["images"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://bash.chomama.jp{url}") as resp:
                        if resp.status != 200:
                            continue
                        fn = url.split("/")[-1]
                        g = io.BytesIO(await resp.read())
                        files.append(discord.File(g, fn))
            await ctx.send(files=files)
        await ctx.send(f"`終了コード: {data['exit_code']}`\n`実行時間: {data['exec_sec']}`")

    @shellgei.error
    async def on_shellgei_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 20, 10)
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "`shellgei`を動かすには引数としてシェルスクリプトのソースコードを入力してください"
            )

    @commands.command()
    @commands.cooldown(2, 120, commands.BucketType.guild)
    async def translate(self, ctx: commands.Context, target: str, *, text: str):
        '''
        [DeepL API](https://www.deepl.com/home)を利用して文章の翻訳を行います
        '''
        if len(text) > 1000:
            return await self.bot.send_error(
                ctx, "翻訳対象の文章が長すぎます",
                "一度に翻訳できる文字数は最大`1000`文字です"
            )
        if not target.upper() in supported_langs:
            return await self.bot.send_error(
                ctx, "サポートされていない言語です",
                ", ".join([f"`{l}`" for l in supported_langs]) +
                " のいずれかをtargetの引数として与えてください"
            )
        embed = discord.Embed(title="翻訳中...", color=config.theme_color)
        embed.set_author(name="DeepL APIを利用しています",
                         url="https://www.deepl.com/home",
                         icon_url="https://www.clker.com/cliparts/E/W/z/w/n/B/deepl.svg.med.png")
        embed.set_footer(text="翻訳", icon_url=self.bot.user.avatar_url)
        msg: discord.Message = await ctx.send(embed=embed)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    'https://api.deepl.com/v2/usage', params={
                        'auth_key': config.deepl_apikey,
                    }) as resp:
                data = await resp.json()
        if data["character_count"] > 100000:
            embed.title = "エラー！"
            await msg.edit(embed=embed)
            return await self.bot.send_error(
                ctx, "DeepL API利用上限に到達しました",
                "本月の翻訳API利用が多いため28日まで翻訳機能は利用できません"
            )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    'https://api.deepl.com/v2/translate', params={
                        'auth_key': config.deepl_apikey,
                        'text': text,
                        'target_lang': target.upper()
                    }) as resp:
                data = await resp.json()
        src = data["translations"][0]["detected_source_language"]
        result = data["translations"][0]["text"]
        embed.title = "翻訳完了！"
        embed.add_field(name=f"元の文章: ({src})", value=text, inline=False)
        embed.add_field(
            name=f"翻訳結果: ({target.upper()})", value=result, inline=False)
        await msg.edit(embed=embed)

    @translate.error
    async def on_translate_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 3, 2)
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "`translate JA Hello!`のように翻訳先の言語を第一引数にして" +
                "翻訳対象の文字列をそれに続いて入力してください\n\n" +
                "対応している言語は以下の通りです:\n" +
                ", ".join([f"`{l}`" for l in supported_langs])
            )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def tapi(self, ctx: commands.Context):
        '''
        [DeepL API](https://www.deepl.com/home)の利用状況を得ます
        '''
        with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        'https://api.deepl.com/v2/usage', params={
                            'auth_key': config.deepl_apikey,
                        }) as resp:
                    data = await resp.json()
            return await self.bot.send_notification(
                ctx, "DeepL API利用状況",
                f"{data['character_count']} / 100000\n\n" +
                f"大体 {data['character_count'] / 1000000 * 2500}円くらい"
            )


def setup(bot):
    bot.add_cog(Fun(bot))
