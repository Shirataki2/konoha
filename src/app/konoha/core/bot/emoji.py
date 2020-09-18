class CustomEmoji:
    ONLINE = 756591503673000016
    IDLE = 756591503673000016
    DND = 756591503673000016
    OFFLINE = 756591503673000016
    LOADING = 756591779612065914

    def __init__(self, bot):
        self.bot = bot

    @property
    def online(self):
        return self.bot.get_emoji(self.ONLINE)

    @property
    def idle(self):
        return self.bot.get_emoji(self.IDLE)

    @property
    def dnd(self):
        return self.bot.get_emoji(self.DND)

    @property
    def offline(self):
        return self.bot.get_emoji(self.OFFLINE)

    @property
    def loading(self):
        return self.bot.get_emoji(self.LOADING)
