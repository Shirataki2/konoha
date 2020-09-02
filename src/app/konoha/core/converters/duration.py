import discord
import re
from discord.ext import commands

d = '[0-9０１２３４５６７８９\.．]'
yers = re.compile(f'({d}+)?(?:年|year|yr|y).*')
mths = re.compile(f'({d}+)?(?:.月|month).*')
weks = re.compile(f'({d}+)?(?:週|week|w).*')
days = re.compile(f'({d}+)?(?:日|day|d).*')
hurs = re.compile(f'({d}+)?(?:時間|hr|hour|h).*')
mins = re.compile(f'({d}+)?(?:分|minute|min|m).*')
secs = re.compile(f'({d}+)?(?:秒|second|sec|s).*')


def extract(argument: str):
    argument = argument.replace(',', '')
    argument = argument.replace(' ', '')
    n = [0.0]
    try:
        y = float(n[0]) if (n := yers.findall(argument)) else 0
    except:
        y = 0
    try:
        m = float(n[0]) if (n := mths.findall(argument)) else 0
    except:
        m = 0
    try:
        w = float(n[0]) if (n := weks.findall(argument)) else 0
    except:
        w = 0
    try:
        d = float(n[0]) if (n := days.findall(argument)) else 0
    except:
        d = 0
    try:
        H = float(n[0]) if (n := hurs.findall(argument)) else 0
    except:
        H = 0
    try:
        M = float(n[0]) if (n := mins.findall(argument)) else 0
    except:
        M = 0
    try:
        S = float(n[0]) if (n := secs.findall(argument)) else 0
    except:
        S = 0
    return y, m, w, d, H, M, S


class DurationToSecondsConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        if isinstance(argument, list):
            argument = "".join(argument)
        y, mo, w, d, h, m, s = extract(argument)
        t = 0.0
        u = 1.0
        for j, mul in zip([s, m, h, d, w, mo, y, 0], [1, 60, 60, 24, 7, 30.4165, 52.142]):
            u *= mul
            t += j * u
        return t
