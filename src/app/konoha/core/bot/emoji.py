class CustomEmoji:
    ONLINE = 706276692465025156
    IDLE = 706276692678934608
    DND = 706276692674609192
    OFFLINE = 706276692662157333
    LOADING = 750643745795342367

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
