class Server:
    def __init__(self, home_channel_guilds=None, bot_channel_lock=True, logs_channel_guilds=None, long_ref=False,
                 command_guilds="#", voice_client=None, ):
        self.bot_channel_lock = bot_channel_lock
        self.home_channel_guilds = home_channel_guilds
        self.logs_channel_guilds = logs_channel_guilds
        self.long_ref = long_ref
        self.command_guilds = command_guilds
        self.voice_client = voice_client
