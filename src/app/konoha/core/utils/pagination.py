import discord
from discord.ext import commands

import asyncio
from copy import deepcopy

from konoha.core import config
from konoha.core.log.logger import get_module_logger

logger = get_module_logger(__name__)


class EmbedPaginator(commands.Paginator):
    def __init__(self, title="", description="", color=None, image="", thumb="", author="", author_link="", icon="", footer=""):
        super().__init__()
        self._set_template(title, description, color, image,
                           thumb, author, author_link, icon, footer)
        self.content = {}

    def _set_template(self, title="", description="", color=None, image="", thumb="", author="", author_link="", icon="", footer=""):
        self.page_template = {
            "title": title,
            "description": description,
            "color": color,
            "dict": [],
            "image": image,
            "thumb": thumb,
            "author": {
                "name": author,
                "url": author_link,
                "icon": icon
            },
            "footer": footer
        }

    def new_page(self):
        self.content[len(self.content)] = deepcopy(self.page_template)

    def add_row_manually(self, k, v, inline=False, page=None):
        if page is None:
            page = len(self.content) - 1
        self.content[page]["dict"].append({"k": k, "v": v, "inline": inline})

    def add_row(self, k, v, inline=False, line_per_page=5):
        p = 0
        while len(self.content[p]["dict"]) == line_per_page and p < 5:
            p += 1
            try:
                self.content[p]["dict"]
            except KeyError:
                self.content[p] = deepcopy(self.page_template)
        self.add_row_manually(k, v, inline, p)

    def render(self, page):
        c = self.content[page]
        for k in c.keys():
            if isinstance(c[k], str):
                c[k] = c[k].replace(
                    "$p", str(page+1)).replace("$P", str(len(self.content)))
            elif isinstance(c[k], dict):
                for l in c[k].keys():
                    c[k][l] = c[k][l].replace(
                        "$p", str(page+1)).replace("$P", str(len(self.content)))
        embed = discord.Embed(title=c["title"], description=c["description"])
        embed.color = c["color"] if c["color"] is not None else config.theme_color
        for r in c["dict"]:
            embed.add_field(name=r["k"], value=r["v"], inline=r["inline"])
        if c["image"] != "":
            embed.set_image(url=c["image"])
        if (name := c["author"]["name"]) != "":
            aurl = c["author"]["url"] if c["author"]["url"] != "" else discord.embeds.EmptyEmbed
            icon = c["author"]["icon"] if c["author"]["icon"] != "" else discord.embeds.EmptyEmbed
            embed.set_author(name=name, url=aurl, icon_url=icon)
        if (footer := c["footer"]) != "":
            embed.set_footer(text=footer)
        return embed

    async def paginate(self, ctx: commands.Context):
        curr = 0
        if len(self.content) == 1:
            return await ctx.send(embed=self.render(curr))
        message: discord.Message = await ctx.send(embed=self.render(curr))
        emojis = ("\u23EE", "\u2B05", "🇽", "\u27A1", "\u23ED")
        for emoji in emojis:
            await message.add_reaction(emoji)

        def check_reaction(r: discord.Reaction, u: discord.Member):
            return all([
                r.message.id == message.id,
                str(r.emoji) in emojis,
                u.id != ctx.bot.user.id,
                ctx.author == u
            ])
        is_dm = False
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=180, check=check_reaction)
            except asyncio.TimeoutError:
                try:
                    for emoji in emojis:
                        await message.clear_reaction(emoji)
                    break
                except:
                    pass
            try:
                await message.remove_reaction(reaction.emoji, user)
            except:
                if not is_dm:
                    is_dm = True
                    await ctx.send("ページ変更するにはリアクションを解除してもう一度押してください")
                pass
            if reaction.emoji == emojis[0]:  # 最初のページへ
                curr = 0
                await message.edit(embed=self.render(curr))
            if reaction.emoji == emojis[1]:  # 前のページへ
                curr = max(0, curr - 1)
                await message.edit(embed=self.render(curr))
            if reaction.emoji == emojis[2]:  # 削除
                return await message.delete()
            if reaction.emoji == emojis[3]:  # 次のページへ
                curr = min(len(self.content) - 1, curr + 1)
                await message.edit(embed=self.render(curr))
            if reaction.emoji == emojis[4]:  # 最後のページへ
                curr = len(self.content) - 1
                await message.edit(embed=self.render(curr))
