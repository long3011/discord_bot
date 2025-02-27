import discord

MY_GUILD = discord.Object(id=1087776751205232761)


class CustomClient(discord.Client):
    # initiate variables for the bot
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        # Syncs command tree to the guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync()
