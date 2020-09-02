import discord
import re
import aiofiles
from discord.ext import commands
from konoha.core.exceptions import InvalidColorException

color = re.compile("(?:#|0x)?([0-9a-fA-F]{3,8})")


class ColorConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        async with aiofiles.open("./palette.txt") as f:
            lines = await f.readlines()
        colors = {col.replace(" ", "-").replace("\n", "").strip("-"): code.replace("\n", "") for col,
                  code in zip(lines[::2], lines[1::2])}
        if argument in colors.keys():
            argument = colors[argument]
        if color.match(argument):
            c = color.findall(argument)[0]
            a = 255
            if len(c) in [3, 4]:
                r = int(c[0] * 2, 16)
                g = int(c[1] * 2, 16)
                b = int(c[2] * 2, 16)
                if len(c) == 4:
                    a = int(c[3] * 2, 16)
            elif len(c) in [6, 8]:
                r = int(c[0:2], 16)
                g = int(c[2:4], 16)
                b = int(c[4:6], 16)
                if len(c) == 8:
                    a = int(c[6:8], 16)
            else:
                raise InvalidColorException(
                    f"Invalid Color code: {argument}")
            return (r, g, b, a)
        else:
            raise InvalidColorException(
                f"Invalid Color code: {argument}")


class FontConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        argument = argument.lower()
        if argument in ["maru", "rounded", "丸ゴシック", "m+1p-rounded"]:
            return "./fonts/rounded-mplus-1p-black.ttf", 28
        if argument in ["sans", "gothic", "ゴシック", "notosans"]:
            return "./fonts/NotoSansCJKjp-Bold.otf", 36
        if argument in ["sans-black", "black", "gothic-black", "太ゴシック", "notosans-black"]:
            return "./fonts/NotoSansCJKjp-Black.otf", 36
        if argument in ["serif", "mincho", "明朝", "notoserif"]:
            return "./fonts/NotoSerifCJKjp-Bold.otf", 36
        if argument in ["serif-black", "mincho-black", "太明朝", "notoserif-black"]:
            return "./fonts/NotoSerifCJKjp-Black.otf", 36
        if argument in ["yagoi", "851", "impact"]:
            return "./fonts/851CHIKARA-DZUYOKU_kanaA_004.ttf", 0
        if argument in ["linlibertine", "libertine", "lib"]:
            return "./fonts/LinLibertine_RB.ttf", 22
        return "./fonts/NotoSansCJKjp-Bold.otf", 36
