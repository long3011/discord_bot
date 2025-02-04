import discord
import json
from extra_stuff import encryption

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True


# Global variables for managing bot settings
long_reference_link="https://cdn.discordapp.com/attachments/972481920103489604/1334509425272160266/IS_THAT_A_LONG_REFERENCE.png?ex=679f6d40&is=679e1bc0&hm=736083076f1b99b16a492a0bb729067a4f09437a0b361e9679b5fec6e7db0f0c&"
# Load bot token from a file
try:
    with open('.\TOKEN.txt') as f:
        bot_token = f.readline()
        f.close()
except FileNotFoundError:
    print('TOKEN.txt not found')

class MyClient(discord.Client):
    #initate variables for the bot
    def __init__(self, bot_channel_lock=None, home_channel_guilds=None, logs_channel_guilds=None, long_ref=None,
                 command_guilds=None):
        super().__init__(intents=intents)
        if command_guilds is None:
            command_guilds = {}
        if long_ref is None:
            long_ref = {}
        if logs_channel_guilds is None:
            logs_channel_guilds = {}
        if home_channel_guilds is None:
            home_channel_guilds = {}
        if bot_channel_lock is None:
            bot_channel_lock = {}
        self.bot_channel_lock = bot_channel_lock
        self.home_channel_guilds = home_channel_guilds
        self.logs_channel_guilds = logs_channel_guilds
        self.long_ref = long_ref
        self.command_guilds = command_guilds

    # Event triggered when the bot is ready
    async def on_ready(self):
        print('we are in bois') # Bot startup confirmation

    # Event triggered when a message is sent in a server
    async def on_message(self,message):

        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        # Handle bot start/restart command
        if message.content.startswith('#start') or message.content.startswith('#restart'):
            self.command_guilds[message.guild] = '#'
            self.home_channel_guilds[message.guild]=message.channel
            self.bot_channel_lock[message.guild] = True
            self.long_ref[message.guild] = False
            await message.add_reaction('👋')
            await self.home_channel_guilds[message.guild].send(
                f'{self.home_channel_guilds[message.guild].mention} will be the default channel for this server.')
            return

        # Ensure bot is active before processing commands
        if message.guild not in self.home_channel_guilds:
            if not message.content.startswith('#'):
                return
            await message.channel.send(
                f'the bot is not active yet, please use '
                f'{self.command_guilds[message.guild]}start in the channel you want to use the bot in first')
            return

        command=message.content.replace(self.command_guilds[message.guild],'').lstrip() #format the command text

        # Respond with long reference image if feature is enabled
        if ("long" in message.content.lower()
                and message.guild in self.home_channel_guilds
                and self.long_ref[message.guild]):
            await message.reply(long_reference_link)

        # Ignore messages that do not start with the command prefix
        if not message.content.startswith(self.command_guilds[message.guild]):
            return

        # Enforce channel lock if enabled
        if (message.guild in self.home_channel_guilds
            and message.channel != self.home_channel_guilds[message.guild]
            and self.bot_channel_lock[message.guild]):
            await message.channel.send(f'The bot is active in {self.home_channel_guilds[message.guild].mention}')
            return

        # Display help command
        if command.startswith('help'):
            output=''
            with open('.\help_command.json') as helps:
                data = json.load(helps)
            for help_command in data:
                output+=f'\n{help_command}: {data[help_command]}'
            await message.channel.send(f'Command start is: {self.command_guilds[message.guild]}'
                                       f'{output}')

        # Change command prefix
        if command.startswith('change_start'):
            if message.content.split('change_start')[1] != "":
                self.command_guilds[message.guild]=message.content.split('change_start')[1].strip()
                await message.channel.send(f'The command calling is now set to:{self.command_guilds[message.guild]}')
            else:
                await message.channel.send(f'Please provide a valid command')

        # Handle 'hello' command
        if command.startswith('hello'):
            await message.channel.send(f'Hello {message.author.display_name}!')

        # Echo user input
        if command.startswith('echo'):
            content=message.content.split('echo')[1]
            await message.channel.send(content)

        # Set log channel
        if command.startswith('logs'):
            self.logs_channel_guilds[message.guild] = message.channel
            await self.logs_channel_guilds[message.guild].send(
                f'{self.logs_channel_guilds[message.guild].mention} will now be the log channel')

        # Lock bot to a single channel
        if command.startswith('lock'):
            self.bot_channel_lock[message.guild]=not self.bot_channel_lock[message.guild]
            await message.channel.send(
                f'The bot is locked to only be used in {self.home_channel_guilds[message.guild].mention}'
                ,delete_after=5)

        # Toggle long reference replies
        if command.startswith('long_reference'):
            self.long_ref[message.guild]= not self.long_ref[message.guild]
            await message.channel.send(
                f'long reference is now set to {self.long_ref[message.guild]}'
                ,delete_after=5)

        if command.startswith('encrypt'):
            content = message.content.split('encrypt')[1].strip()
            await message.channel.send(f'{encryption.encrypt(content)}',delete_after=5)
            await message.delete(delay=5)

        if command.startswith('decrypt'):
            content = message.content.split('decrypt')[1].strip()
            await message.channel.send(f'{encryption.decrypt(content)}',delete_after=5)
            await message.delete(delay=5)

    # Event triggered when a reaction is added
    async def on_reaction_add(self,react, user):
        if user == self.user:
            return
        if react.message.author != self.user:
            return
        if react.message.guild not in self.home_channel_guilds:
            return
        await self.home_channel_guilds[react.message.guild].send(f'{user.name}: {react.emoji}')


    # Event triggered when a message is deleted
    async def on_message_delete(self,message):
        if message.author == self.user:
            return
        if message.guild not in self.logs_channel_guilds:
            return
        await self.logs_channel_guilds[message.guild].send(f'{message.author.name} deleted: {message.content}')


    # Event triggered when a message is edited
    async def on_message_edit(self,before, after):
        if before.author == self.user:
            return
        if before.guild not in self.logs_channel_guilds:
            return
        await self.logs_channel_guilds[before.guild].send(f'{after.author.name} edited: {before.content} -> {after.content}')

my_client=MyClient()
# Start the bot
try:
    my_client.run(bot_token)
except RuntimeError:
    print('Token expired')