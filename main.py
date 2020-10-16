import asyncio

import discord
from discord import Message
from discord.utils import get

from vault import vault_init, vault

vault_init('Unglaublich geheimer Schlüssel')

client = discord.Client()


async def organic_send(channel, *args, organic_time=None, **kwargs):
    async with channel.typing():
        if organic_time is None:
            organic_time = 1
        await asyncio.sleep(organic_time)
        await channel.send(*args, **kwargs)


@client.event
async def on_message(message: Message):
    if get(message.mentions, id=client.user.id) is not None:
        await organic_send(message.channel, 'Hello')


if __name__ == '__main__':
    client.run(vault.bot_token(None))
