# This example requires the 'message_content' intent.

import discord
import time
import os
import json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
home_channel_guilds={}
first_use=True
long_reference_link="https://cdn.discordapp.com/attachments/972481920103489604/1334509425272160266/IS_THAT_A_LONG_REFERENCE.png?ex=679f6d40&is=679e1bc0&hm=736083076f1b99b16a492a0bb729067a4f09437a0b361e9679b5fec6e7db0f0c&"
command_start='#'
try:
    with open('.\TOKEN.txt') as f:
        bot_token = f.readline()

except FileNotFoundError:
    print('TOKEN.txt not found')
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global home_channel_guilds
    global first_use
    command=message.content[1:].split(' ')[0]
    if message.author == client.user:
        return
    if command=='start':
        if not message.content.startswith(command_start):
            return
        home_channel_guilds[message.guild]=message.channel
        await message.add_reaction('👋')
        await home_channel_guilds[message.guild].send(f'{home_channel_guilds[message.guild].mention} will be the default channel for this session')
    if message.guild not in home_channel_guilds:
        await message.channel.send(
            f'the bot is not active yet, please use {command_start}start in the channel you want to use the bot in first')
        return
    if "long" in message.content.lower() and message.guild in home_channel_guilds:
        await message.reply(long_reference_link)
    if not message.content.startswith(command_start):
        return
    if message.channel != home_channel_guilds[message.guild] and message.guild in home_channel_guilds:
        await message.channel.send(f'The bot is active in {home_channel_guilds[message.guild].mention}')
        return
    if command=='help':
        await message.channel.send(f'Command starting is: {command_start}'
                                   f'\nhelp: View this command'
                                   f'\nhello: reply hello with the user\'s name'
                                   f'\necho: Repeat what is said after')
    if command=='hello':
        await home_channel_guilds[message.guild].send(f'Hello {message.author.display_name}!')
    if command=='echo':
        await home_channel_guilds[message.guild].send(message.content[6:])

@client.event
async def on_reaction_add(react, user):
    global home_channel_guilds
    if user == client.user:
        return
    if react.message.author != client.user:
        return
    if react.message.guild not in home_channel_guilds:
        return
    await home_channel_guilds[react.message.guild].send(f'{user.name}: {react.emoji}')

try:
    client.run(bot_token)
except RuntimeError:
    print('Token expired')