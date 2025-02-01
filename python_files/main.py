# This example requires the 'message_content' intent.

import discord
import time
import os
import json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
home_channel=None
first_use=True
long_reference_link="https://cdn.discordapp.com/attachments/972481920103489604/1334509425272160266/IS_THAT_A_LONG_REFERENCE.png?ex=679f6d40&is=679e1bc0&hm=736083076f1b99b16a492a0bb729067a4f09437a0b361e9679b5fec6e7db0f0c&"

with open('TOKEN.txt') as f:
    bot_token = f.readline()
    f.close()

@client.event
async def on_ready():
    global home_channel
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global home_channel
    global first_use
    if message.author == client.user:
        return
    if message.content.startswith('#'):
        if message.channel != home_channel and home_channel is not None:
            await message.channel.send(f'The bot is active in {home_channel.mention}')
            return
        if message.content.startswith('#start'):
            with open("home.txt",'w') as f:
                f.write(str(message.channel))
            if first_use:
                home_channel=message.channel
                await message.add_reaction('👋')
                await home_channel.send(f'{home_channel.mention} will be the default channel for this session')
                first_use=False
            else:
                await message.channel.send(f'The bot is already active in {home_channel.mention}')
    if message.content.startswith('#hello'):
        await home_channel.send(f'Hello {message.author.name}!')
    if message.content.startswith('#echo'):
        await home_channel.send(message.content[6:])
    if "long" in message.content.lower() and home_channel is not None:
        await message.reply(long_reference_link)
    if home_channel is None:
        await message.channel.send(
            f'the bot is not active yet, please use #start in the channel you want to use the bot in first')

@client.event
async def on_reaction_add(react, user):
    global home_channel
    if user == client.user:
        return
    if react.message.author != client.user:
        return
    if home_channel is None:
        return
    await home_channel.send(f'{user.name}: {react.emoji}')

try:
    client.run(bot_token)
except RuntimeError:
    print('Token expired')
