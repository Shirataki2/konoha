import discord
from discord.ext import commands, tasks

import asyncio
import re
import io
import os
import aiohttp
import random
import secrets
from unicodedata import east_asian_width
from itertools import cycle
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Pattern

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.commands import checks
from konoha.core.converters import ColorConverter, FontConverter
from konoha.core.utils import TextImageGenerator
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
    order = 1

    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot

    def _get_unicode_length(self, message: str):
        length = 0
        for code in map(east_asian_width, message):
            if code in ['W', 'A', 'F']:
                length += 2
            else:
                length += 1
        return length

    def _to_suddendeath(self, message: str):
        lines = message.split('\n')
        lengths = list(map(self._get_unicode_length, lines))
        max_length = max(lengths)
        header_length = (max_length // 2 + 2)
        footer_length = int(((max_length + 2) // 2 / 5) * 9 + 2)
        header = '＿' + '人' * header_length + '＿'
        footer = '￣' + \
            ''.join(c for i, c in zip(range(footer_length), cycle('Y^'))) + '￣'
        new_lines = []
        new_lines.append(header)
        for line, length in zip(lines, lengths):
            spaces = '　' * ((max_length - length) // 2) + \
                     ' ' * ((max_length - length) % 2)
            new_lines.append('＞　' + line + spaces + '　＜')
        new_lines.append(footer)
        return '\n'.join(new_lines)

    @commands.command(aliases=['sd'])
    async def suddendeath(self, ctx: commands.Context, *, body: str = None):
        '''
        \> 突然の死 < のような文章を生成します．
        '''
        if body is None:
            body = '突然の死'
        if max(map(self._get_unicode_length, body.split('\n'))) > 25:
            body = '一行が長すぎです！'
        await ctx.send(self._to_suddendeath(body))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(5, 60, commands.BucketType.guild)
    async def run(self, ctx: commands.Context, lang, *, code: str):
        '''
        C++,Python,Ruby,Rust,Haskell,Javascript,Shellのソースコードを走らせます．

        Twitterのシェル芸Botと同様，ファイルを送信したら/mediaにファイルが置かれ，

        画像を/imagesに保存すると帰ってきます
        '''
        if lang in ['py', 'python']:
            l = 'python'
        elif lang in ['c', 'c++', 'cpp']:
            l = 'cpp'
        elif lang in ['js', 'javascript']:
            l = 'javascript'
        elif lang in ['hs', 'haskell']:
            l = 'haskell'
        elif lang in ['rb', 'ruby']:
            l = 'ruby'
        elif lang in ['rs', 'rust']:
            l = 'rust'
        elif lang in ['sh', 'bash', 'zsh', 'shell']:
            l = 'shell'
        else:
            return await self.bot.send_error(
                ctx, '引数が不正です！',
                '第一引数には言語名を入れてください!\n\n' +
                '対応言語: ' +
                ','.join(['python', 'c++', 'javascript',
                          'ruby', 'haskell', 'shell'])
            )
        ptn: Pattern[str] = re.compile(r'```(.*)?\n((.|\s)*)?```')
        codes = ptn.findall(code)
        if len(codes) == 1:
            _code = codes[0]
            if len(_code) == 3:
                code = _code[1]
        if code[0] == '`' and code[-1] == '`':
            code = code[1:-1]
        form = aiohttp.FormData()
        form.add_field('source', code)
        form.add_field('language', l)
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

    @run.error
    async def on_shellgei_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 20, 10)
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "このコマンドを動かすには引数として言語とソースコードを入力してください\n\n" +
                "例: `run python print('Hello')`"
            )

    @commands.command()
    @commands.cooldown(60, 120, commands.BucketType.guild)
    async def translate(self, ctx: commands.Context, target: str, *, text: str):
        '''
        [DeepL API](https://www.deepl.com/home)を利用して文章の翻訳を行います

        言語は以下のようにして指定してください

        "DE", "EN-GB", "EN-US", "EN", "FR", "IT", "JA", "ES", "NL", "PL", "PT-PT", "PT-BR", "PT", "RU", "ZH"
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
        loading = self.bot.custom_emojis.loading
        embed = discord.Embed(title=f"翻訳中 {loading}", color=config.theme_color)
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
            await self.bot.send_cooldown_error(ctx, error, 10, 2)
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "`translate JA Hello!`のように翻訳先の言語を第一引数にして" +
                "翻訳対象の文字列をそれに続いて入力してください\n\n" +
                "対応している言語は以下の通りです:\n" +
                ", ".join([f"`{l}`" for l in supported_langs])
            )

    @commands.command(aliases=["create_emoji"])
    @commands.cooldown(5, 60, commands.BucketType.guild)
    async def emocre(self, ctx: commands.Context, text,
                     color: Optional[ColorConverter],
                     font: Optional[FontConverter],
                     background: Optional[ColorConverter],
                     ):
        """
        引数に与えられた文字を絵文字化します．改行したい場合は`;`を入力してください
        """
        text = text.replace(" ", "")
        if len(text.replace(";", "")) > 60:
            return await self.bot.send_error(
                ctx, "最大文字数を超過しています",
                "最大60文字まで絵文字に変換することが可能です"
            )
        if color is None:
            color = (244, 67, 54)  # type: ignore
        if background is None:
            background = (0, 0, 0, 0)  # type: ignore
        if font is None:
            font = "./fonts/NotoSansCJKjp-Bold.otf", 34  # type: ignore
        gen = TextImageGenerator(
            font[0], text, fg_color=color, bg_color=background, offset=font[1])  # type: ignore
        img = await self.bot.loop.run_in_executor(None, gen.render)
        fp = io.BytesIO()
        img.save(fp, "PNG")
        fp.seek(0)
        file = discord.File(fp, filename="emoji.png")
        await ctx.send(file=file)

    @emocre.error
    async def on_emocre_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            ctx.handled = True
            await self.bot.send_cooldown_error(ctx, error, 5, 1)
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.handled = True
            await self.bot.send_error(
                ctx, "引数が不足しています！",
                "このコマンドを動かすには最低限引数として絵文字化したい文字列を入力してください"
            )


def setup(bot):
    bot.add_cog(Fun(bot))
