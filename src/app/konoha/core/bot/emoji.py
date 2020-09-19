class CustomEmoji:
    ONLINE = 756590419566919830
    IDLE = 756590419281707110
    DND = 756590419575570453
    OFFLINE = 756590419671777340
    LOADING = 756590419600605254

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
