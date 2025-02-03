# This example requires the 'message_content' intent.

import discord
import time
import os
import json

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot client with the specified intents
client = discord.Client(intents=intents)

# Global variables for managing bot settings
long_reference_link="https://cdn.discordapp.com/attachments/972481920103489604/1334509425272160266/IS_THAT_A_LONG_REFERENCE.png?ex=679f6d40&is=679e1bc0&hm=736083076f1b99b16a492a0bb729067a4f09437a0b361e9679b5fec6e7db0f0c&"
bot_channel_lock = {}  # Tracks whether the bot is locked to a specific channel
home_channel_guilds = {}  # Stores the default channel for each server
logs_channel_guilds = {}  # Stores the logging channel for each server
long_ref = {}  # Tracks whether long reference feature is enabled for each server
command_guilds = {}  # Stores custom command prefixes for each server
# Load bot token from a file
try:
    with open('.\TOKEN.txt') as f:
        bot_token = f.readline()
        f.close()
except FileNotFoundError:
    print('TOKEN.txt not found')

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print('we are in bois') # Bot startup confirmation

# Event triggered when a message is sent in a server
@client.event
async def on_message(message):
    global bot_channel_lock, home_channel_guilds, logs_channel_guilds, command_guilds
    command=''.join(message.content.lower().split(' ')) #format the command text

    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    # Handle bot start/restart command
    if message.content.startswith('#start') or message.content.startswith('#restart'):
        command_guilds[message.guild] = '#'
        home_channel_guilds[message.guild]=message.channel
        bot_channel_lock[message.guild] = True
        long_ref[message.guild] = False
        await message.add_reaction('👋')
        await home_channel_guilds[message.guild].send(
            f'{home_channel_guilds[message.guild].mention} will be the default channel for this server.')
        return

    # Ensure bot is active before processing commands
    if message.guild not in home_channel_guilds:
        if not message.content.startswith(command_guilds[message.guild]):
            return
        await message.channel.send(
            f'the bot is not active yet, please use '
            f'{command_guilds[message.guild]}start in the channel you want to use the bot in first')
        return
    # Respond with long reference image if feature is enabled
    if ("long" in message.content.lower()
            and message.guild in home_channel_guilds
            and long_ref[message.guild]):
        await message.reply(long_reference_link)

    # Ignore messages that do not start with the command prefix
    if not message.content.startswith(command_guilds[message.guild]):
        return

    # Enforce channel lock if enabled
    if (message.guild in home_channel_guilds
        and message.channel != home_channel_guilds[message.guild]
        and bot_channel_lock[message.guild]):
        await message.channel.send(f'The bot is active in {home_channel_guilds[message.guild].mention}')
        return

    # Display help command
    if command.startswith(command_guilds[message.guild]+'help'):
        await message.channel.send(f'Command start is: {command_guilds[message.guild]}'
                                   f'\n-#start/#restart: Start/restart the bot'
                                   f'\n-help: View this command'
                                   f'\n-change_start: Change the bot start character, '
                                   f'spaces also count(this will be case sensitive)'
                                   f'\n-hello: reply hello with the user\'s name'
                                   f'\n-echo: Repeat what is said after'
                                   f'\n-logs: set the logs channel to be sent the logs'
                                   f'\n-lock: lock the bot to be only used in the default channel'
                                   f'\n-unlock: unlock the bot to be used server-wide'
                                   f'\n-long_reference: enable long reference, reply any message with the word \"long\"'
                                   f'with long reference image')

    # Change command prefix
    if command.startswith(command_guilds[message.guild]+'change_start'):
        if message.content[len(command_guilds[message.guild])+13:] != "":
            command_guilds[message.guild]=message.content[len(command_guilds[message.guild])+13:]
            await message.channel.send(f'The command calling is now set to:{command_guilds[message.guild]}')
        else:
            await message.channel.send(f'Please provide a valid command')

    # Handle 'hello' command
    if command.startswith(command_guilds[message.guild]+'hello'):
        await message.channel.send(f'Hello {message.author.display_name}!')

    # Echo user input
    if command.startswith(command_guilds[message.guild]+'echo'):
        await message.channel.send(message.content[len(command_guilds[message.guild])+5:])

    # Set log channel
    if command.startswith(command_guilds[message.guild]+'logs'):
        logs_channel_guilds[message.guild] = message.channel
        await logs_channel_guilds[message.guild].send(
            f'{logs_channel_guilds[message.guild].mention} will now be the log channel')

    # Lock bot to a single channel
    if command.startswith(command_guilds[message.guild]+'lock'):
        bot_channel_lock[message.guild]=True
        await message.channel.send(
            f'The bot is locked to only be used in {home_channel_guilds[message.guild].mention}'
            ,delete_after=5)

    # Unlock bot for all channels
    if command.startswith(command_guilds[message.guild]+'unlock'):
        bot_channel_lock[message.guild]=False
        await message.channel.send(
            f'The bot is unlocked and can be used everywhere'
            ,delete_after=5)

    # Toggle long reference replies
    if command.startswith(command_guilds[message.guild]+'long_reference'):
        long_ref[message.guild]= not long_ref[message.guild]
        await message.channel.send(
            f'long reference is now set to {long_ref[message.guild]}'
            ,delete_after=5)


# Event triggered when a reaction is added
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


# Event triggered when a message is deleted
@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return
    if message.guild not in home_channel_guilds:
        return
    await home_channel_guilds[message.guild].send(f'{message.author.name} deleted: {message.content}')


# Event triggered when a message is edited
@client.event
async def on_message_edit(before, after):
    if before.author == client.user:
        return
    if before.guild not in home_channel_guilds:
        return
    await home_channel_guilds[before.guild].send(f'{after.author.name} edited: {before.content} -> {after.content}')


# Start the bot
try:
    client.run(bot_token)
except RuntimeError:
    print('Token expired')