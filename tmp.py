import discord
import MeCab
import jaconv
import asyncio

client = discord.Client()
tagger = MeCab.Tagger("-Oyomi -d/usr/local/lib/mecab/dic/mecab-ipadic-neologd")


@client.event
async def on_message(message):
    if message.content.startswith(":TRAIN:"):
        n = int(message.content.split()[1])
        ch = await client.fetch_channel(703633853302177916)
        for i in range(n):
            await ch.send(f"{i+1} / {n}")
            await ch.send('::t')
            await asyncio.sleep(4)
            msg = await ch.history().get(author__name='TAO')
            ideom = msg.embeds[0].description.split("」")[0][1:]
            yomi =  jaconv.kata2hira(tagger.parse(ideom))
            await ch.send(yomi)
            await asyncio.sleep(3)
        await ch.send(f"{client.user.mention} FINISHED!")
    if message.content.startswith(":ATK:"):
        n = int(message.content.split()[1])
        ch = await client.fetch_channel(703633853302177916)
        for i in range(n):
            await ch.send(f"{i+1} / {n}")
            await ch.send('::atk')
            await asyncio.sleep(5)
        await ch.send(f"{client.user.mention} FINISHED!")
    if message.content.startswith(":TEST:"):
        ch = await client.fetch_channel(703633853302177916)
        msg = await ch.send("ping")
        await ch.send(f"{msg.author.name} {msg.author.bot}")
client.run("MzM0MDE3ODA5MDkwNzQwMjI0.X46G5A.m38HosxB0N0IOS_q_bxQbbkqk1s", bot=False)
