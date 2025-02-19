import json
from io import BytesIO

import discord
from petpet import petpet

from files import encryption, server, user

#require pynacl

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True

# Dictionary to store user data
user_dict = {}

# Define the debugging server
MY_GUILD = discord.Object(id=1087776751205232761)  # replace with own server id

# Load bot token from a file
try:
    with open('random/TOKEN.txt') as f:
        bot_token = f.readline()
        f.close()
except FileNotFoundError:
    print('TOKEN.txt not found')

class MyClient(discord.Client):
    #initate variables for the bot
    def __init__(self, servers_list=None):
        super().__init__(intents=intents)
        if servers_list is None:
            servers_list = {}
        self.servers_list = servers_list
        self.tree = discord.app_commands.CommandTree(self)

    # Event triggered when the bot is ready
    async def on_ready(self):
        #Triggered when the bot successfully connects to Discord.
        print('we are in bois') # Bot startup confirmation

    async def setup_hook(self):
        # Syncs command tree to the guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    # Event triggered when a message is sent in a server
    async def on_message(self,message):

        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        # Handle bot start/restart command
        if message.content.startswith('#start') or message.content.startswith('#restart'):
            print(self.guilds)
            self.servers_list[message.guild] = server.Server(home_channel_guilds=message.channel)
            await message.add_reaction('👋')
            await self.servers_list[message.guild].home_channel_guilds.send(
                f'{self.servers_list[message.guild].home_channel_guilds.mention} will be the default channel for this server.')
            self.tree.copy_global_to(guild=message.guild)
            return

        # Ensure bot is active before processing commands
        if message.guild not in self.servers_list:
            if not message.content.startswith('#'):
                return
            await message.channel.send(
                f'the bot is not active yet, please use '
                f'#start in the channel you want to use the bot in first')
            return

        # Extract command from message
        command=message.content.replace(self.servers_list[message.guild].command_guilds,'').lstrip() #format the command text

        if command.startswith('restart'):
            self.servers_list[message.guild] = server.Server(home_channel_guilds=message.channel)
            await message.add_reaction('👋')
            await self.servers_list[message.guild].home_channel_guilds.send(
                f'{self.servers_list[message.guild].home_channel_guilds.mention} will be the default channel for this server.')
            return

        # Respond with long reference image if feature is enabled
        if ("long" in message.content.lower()
                and message.guild in self.servers_list
                and self.servers_list[message.guild].long_ref):
            long_reference = discord.File(fp="random/is_that_a_long_reference.png",
                                          filename="is_that_a_long_reference.png")
            await message.reply(file=long_reference, mention_author=False)

        # Ignore messages that do not start with the command prefix
        if not message.content.startswith(self.servers_list[message.guild].command_guilds):
            return

        # Enforce channel lock if enabled
        if (message.guild in self.servers_list
            and message.channel != self.servers_list[message.guild].home_channel_guilds
            and self.servers_list[message.guild].bot_channel_lock):
            await message.channel.send(f'The bot is active in {self.servers_list[message.guild].home_channel_guilds.mention}')
            return

        # Display help command
        if command.startswith('help'):
            output= ''
            with open('random/help_command.json') as f:
                helps = json.load(f)
            if len(command.split(' '))==1:
                for help_command in helps:
                    output += f'\n- {help_command}'
                await message.channel.send(f'Default start command: #start'
                                           f'\nCommand prefix is: {self.servers_list[message.guild].command_guilds}'
                                           f'{output}')
            else:
                help_for=command.split(' ')[1].strip()
                if help_for in helps:
                    await message.channel.send(f'{help_for}: {helps[help_for]}')
                else:
                    await message.channel.send(f'That is not a command, try again')

        # Change command prefix
        if command.startswith('change_start'):
            if message.content.split('change_start')[1] != "":
                self.servers_list[message.guild].command_guilds=message.content.split('change_start')[1].strip()
                await message.channel.send(f'The command calling is now set to:{self.servers_list[message.guild].command_guilds}')
            else:
                await message.channel.send(f'Please provide a valid command')

        # Handle 'hello' command
        if command.startswith('hello'):
            await message.channel.send(f'Hello {message.author.display_name}!')

        # Echo user input
        if command.startswith('echo'):
            echo_content=message.content.split('echo')[1]
            await message.channel.send(echo_content)

        # Set log channel
        if command.startswith('logs'):
            self.servers_list[message.guild].logs_channel_guilds = message.channel
            await self.servers_list[message.guild].logs_channel_guilds.send(
                f'{self.servers_list[message.guild].logs_channel_guilds.mention} will now be the log channel')

        # Lock bot to a single channel
        if command.startswith('lock'):
            self.servers_list[message.guild].bot_channel_lock=not self.servers_list[message.guild].bot_channel_lock
            await message.channel.send(
                f'The bot is locked to only be used in {self.servers_list[message.guild].home_channel_guilds.mention}'
                ,delete_after=5)

        # Toggle long reference replies
        if command.startswith('long_reference'):
            self.servers_list[message.guild].long_ref= not self.servers_list[message.guild].long_ref
            await message.channel.send(
                f'long reference is now set to {self.servers_list[message.guild].long_ref}'
                ,delete_after=5)

        # Encrypt and decrypt commands using custom module
        if command.startswith('encrypt'):
            content = message.content.split('encrypt')[1].strip()
            await message.channel.send(f'{encryption.encrypt(content)}', delete_after=5)
            await message.delete(delay=5)

        if command.startswith('decrypt'):
            content = message.content.split('decrypt')[1].strip()
            await message.channel.send(f'{encryption.decrypt(content)}', delete_after=5)
            await message.delete(delay=5)

        #pet command that return a gif of the user pfp being petted
        if command.startswith('pet' or 'pat'):
            for person in message.mentions:
                image = await person.display_avatar.read()
                source = BytesIO(image)  # file-like container to hold the emoji in memory
                dest = BytesIO()  # container to store the petpet gif in memory
                petpet.make(source, dest)
                dest.seek(0)  # set the file pointer back to the beginning so it doesn't upload a blank file.
                await message.channel.send(file=discord.File(dest, filename=f"{image[0]}-petpet.gif"))

        # join a voice channel
        #currently have no use
        if command.startswith('join'):
            if message.author.voice is None:
                await message.channel.send(f'You are not in a voice channel')
            else:
                voice_channel=message.author.voice.channel
                self.servers_list[message.guild].voice_client=await voice_channel.connect()

        #leave the voice channel the bot is in
        if command.startswith('leave'):
            if message.author.voice is None:
                await message.channel.send(f'You are not in a voice channel')
            elif self.servers_list[message.guild].voice_client is None:
                await message.channel.send(f'The bot is not connected to a voice channel')
            else:
                await self.servers_list[message.guild].voice_client.disconnect()

    # Event triggered when a reaction is added
    async def on_reaction_add(self,react, user):
        if user == self.user:
            return
        if react.message.author != self.user:
            return
        if react.message.guild not in self.servers_list:
            return  #ensure all the required channels exist before logging
        await self.servers_list[react.message.guild].home_channel_guilds.send(f'{user.name}: {react.emoji}')


    # Event triggered when a message is deleted
    async def on_message_delete(self,message):
        if message.author == self.user:
            return
        if (message.guild not in self.servers_list
                or self.servers_list[message.guild].logs_channel_guilds is None):
            return  #ensure all the required channels exist before logging
        await self.servers_list[message.guild].logs_channel_guilds.send(f'{message.author.name} deleted: {message.content}')


    # Event triggered when a message is edited
    async def on_message_edit(self,before, after):
        if before.author == self.user:
            return
        if (before.guild not in self.servers_list
                or self.servers_list[before.guild].logs_channel_guilds is None):
            return  #ensure all the required channels exist before logging
        await self.servers_list[before.guild].logs_channel_guilds.send(
            f'{after.author.name} edited: {before.content} -> {after.content}')


client = MyClient()


# greet the user
@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


# pet the user being mentioned
@client.tree.command()
@discord.app_commands.describe(user='The member you want to pet; defaults to the user who uses the command')
async def pet(interaction: discord.Interaction, user: discord.Member = None):
    """Pet a member."""
    # If no member is explicitly provided then we use the command user here
    user = user or interaction.user
    image = await user.display_avatar.read()
    source = BytesIO(image)  # file-like container to hold the emoji in memory
    dest = BytesIO()  # container to store the petpet gif in memory
    petpet.make(source, dest)
    dest.seek(0)  # set the file pointer back to the beginning so it doesn't upload a blank file.
    await interaction.response.send_message(file=discord.File(dest, filename=f"{image[0]}-petpet.gif"))


# send a message using the bot
@client.tree.command()
@discord.app_commands.rename(text_to_send='text')
@discord.app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


# gamba time
@client.tree.command()
@discord.app_commands.describe(amount='The amount you want to bid')
async def gamble(interaction: discord.Interaction, amount: int):
    """Gamble your money away"""
    if interaction.user.id not in user_dict:
        user_dict[interaction.user.id] = user.User(interaction.user.id)
    gamba = user_dict[interaction.user.id].coin_flip(amount)
    if gamba:
        await interaction.response.send_message(f'You won {amount} coins! '
                                                f'<a:yippee:1341676448104189993>'
                                                f'\nYou now have {user_dict[interaction.user.id].balance} coins')
    else:
        await interaction.response.send_message(f'You lost :c'
                                                f'\nYou now have {user_dict[interaction.user.id].balance} coins')


@client.tree.command()
async def claim(interaction: discord.Interaction):
    """Get a free 1000 coins"""
    if interaction.user.id not in user_dict:
        user_dict[interaction.user.id] = user.User(interaction.user.id)
    user_dict[interaction.user.id].add_coin(1000)
    await interaction.response.send_message('Added 1000 coins to your balance', ephemeral=True)


@client.tree.command()
async def bal(interaction: discord.Interaction):
    """Check your balance"""
    if interaction.user.id not in user_dict:
        user_dict[interaction.user.id] = user.User(interaction.user.id)
    await interaction.response.send_message(f'You have {user_dict[interaction.user.id].balance} coins', ephemeral=True)

# Start the bot
try:
    client.run(bot_token)
except RuntimeError:
    print('Token expired')