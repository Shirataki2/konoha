import discord
from discord.ext import commands, tasks

import asyncio
import aiohttp
import random
from functools import partial
from pybooru import Danbooru

import konoha.models.crud2 as q
from konoha.core import config
from konoha.core.bot.konoha import Konoha
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class Images(commands.Cog):
    order = 999999

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
    @commands.is_owner()
    async def autobooru(self, ctx: commands.Context, *, tags):
        channel_id = ctx.channel.id
        if hook := await q.Hook(self.bot, ctx.guild.id, channel_id).get():
            async with aiohttp.ClientSession() as session:
                await q.Hook(self.bot, ctx.guild.id, channel_id).set(hookurl=hook.hookurl, tags=tags)
                await ctx.send(f"Tagを{hook.tags}から{tags}に変更しました")
                try:
                    webhook = discord.Webhook.from_url(
                        hook.hookurl, adapter=discord.AsyncWebhookAdapter(session))
                    return await webhook.send(f"Webhookの変更が完了しました")
                except:
                    webhook2: discord.Webhook = await ctx.channel.create_webhook(name="Autobooru")
                    await q.Hook(self.bot, ctx.guild.id, channel_id).set(hookurl=webhook2.url, tags=tags)
                    await ctx.send(f"Danbooru Webhookを登録しました\nTag: {tags}")
                    return await webhook2.send(f"Webhookの登録が完了しました")
        else:
            webhook_: discord.Webhook = await ctx.channel.create_webhook(name="Autobooru")
            await q.Hook.create(self.bot, ctx.guild.id, channel_id, webhook_.url, tags)
            await ctx.send(f"新規Danbooru Webhookを登録しました\nTag: {tags}")
            return await webhook_.send(f"Webhookの登録が完了しました")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def stopbooru(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            if hook := await q.Hook(self.bot, ctx.guild.id, ctx.channel.id).get():
                await q.Hook(self.bot, ctx.guild.id, ctx.channel.id).delete()
                webhook = discord.Webhook.from_url(
                    hook.hookurl, adapter=discord.AsyncWebhookAdapter(session))
                await webhook.send(f"Webhookの登録を解除しました")
                await webhook.delete()
            else:
                await ctx.send(f"まだWebHookを利用していません")

    @tasks.loop(seconds=180)
    async def postloop(self):
        try:
            hooks = await q.Hook.get_all(self.bot, verbose=2)
            await asyncio.gather(*[
                self.hook_subtask(hook) for hook in hooks
            ])
        except Exception as e:
            pass
    
    async def hook_subtask(self, hook):
        posts = []
        reconnect = 0
        while len(posts) == 0 and reconnect < 10:
            reconnect += 1
            p = random.randint(1, 2000)
            fn = partial(self.client.post_list,
                            tags=hook.tags, page=p, limit=2)
            posts = await self.bot.loop.run_in_executor(None, fn)
            await asyncio.sleep(0.1)
        post = random.choice(posts)
        try:
            fileurl = post['file_url']
        except:
            fileurl = 'https://danbooru.donmai.us' + post['source']
        embed = discord.Embed(title='щ（゜ロ゜щ）')
        try:
            p = lambda c: "/".join(f"[{e.replace('_', ' ').title()}](https://danbooru.donmai.us/posts?tags={e})" for e in post[c].split())
            embed.add_field(name="Detail", value=f"[view](https://danbooru.donmai.us/posts/{post['id']})")
            if post['tag_string_artist']:
                embed.add_field(name="Artist", value=p('tag_string_artist'))
            if post['tag_string_copyright']:
                embed.add_field(name="Copyright", value=p('tag_string_copyright'))
            if post['tag_string_character']:
                embed.add_field(name="Character", value=p('tag_string_character'))
        except Exception as e:
            pass
        embed.set_image(url=fileurl)
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                hook.hookurl,
                adapter=discord.AsyncWebhookAdapter(session)
            )
            await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.channel.category_id in [703650843924103230, 775364727521017866]:
            await message.add_reaction('⭐')


def setup(bot):
    bot.add_cog(Images(bot))
