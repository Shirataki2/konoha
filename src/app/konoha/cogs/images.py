import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
from pybooru import Danbooru

import konoha.models.crud as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)

class Images(commands.Cog):
    def __init__(self, bot: Konoha):
        self.bot: Konoha = bot
        self.client = Danbooru(
            "danbooru",
            username=config.danbooru_name,
            api_key=config.danbooru_key
        )
        # pylint: disable=no-member
        self.postloop.start()

    def cog_unload(self):
        # pylint: disable=no-member
        self.postloop.cancel()


    @commands.command(hidden=True)
    async def autobooru(self, ctx: commands.Context, hookurl, *, tags):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(hookurl, adapter=discord.AsyncWebhookAdapter(session))
            channel_id = webhook.id
            if hook := await q.Hook(ctx.guild.id, channel_id).get():
                await q.Hook(ctx.guild.id, channel_id).set(hookurl=hookurl, tags=tags)
                await ctx.send(f"Tagを{hook.tags}から{tags}に変更しました")
                return await webhook.send(f"Webhookの登録が完了しました")
            else:
                await q.Hook.create(ctx.guild.id, channel_id, hookurl, tags)
                await ctx.send(f"新規Danbooru Webhookを登録しました\nTag: {tags}")
                return await webhook.send(f"Webhookの登録が完了しました")

    @commands.command(hidden=True)
    async def stopbooru(self, ctx: commands.Context, hookurl):
        async with aiohttp.ClientSession() as session:
            if hooks := await q.Hook.search(hookurl=hookurl):
                hook: q.Hook = hooks[0]
                hook = await q.Hook(hook.guild, hook.channel).delete()
                webhook = discord.Webhook.from_url(hookurl, adapter=discord.AsyncWebhookAdapter(session))
                return await webhook.send(f"Webhookの登録を解除しました")
            else:
                await ctx.send(f"与えられたURLではまだWebHookを利用していません")

    @tasks.loop(seconds=60)
    async def postloop(self):
        for hook in await q.Hook.get_all(verbose=0):
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    hook.hookurl,
                    adapter=discord.AsyncWebhookAdapter(session)
                )
                posts = []
                while len(posts) == 0:
                    p = random.randint(1, 2000)
                    posts = self.client.post_list(tags=hook.tags, page=p, limit=20)
                    await asyncio.sleep(0.2)
                post = random.choice(posts)
                try:
                    fileurl = post['file_url']
                except:
                    fileurl = 'https://danbooru.donmai.us' + post['source']
                embed = discord.Embed(title='щ（゜ロ゜щ）')
                embed.set_image(url=fileurl)
                await webhook.send(embed=embed)


def setup(bot):
    bot.add_cog(Images(bot))