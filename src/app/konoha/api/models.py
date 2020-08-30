class Permission:
    def __init__(self, bit):
        self.bit = bit
        self.create_instant_invite = False
        self.kick_members = False
        self.ban_members = False
        self.administrator = False
        self.manage_channels = False
        self.manage_guild = False
        self.add_reactions = False
        self.view_audit_log = False
        self.priority_speaker = False
        self.stream = False
        self.view_channel = False
        self.send_messages = False
        self.send_tts_messages = False
        self.manage_messages = False
        self.embed_links = False
        self.attach_files = False
        self.read_message_history = False
        self.mention_everyone = False
        self.use_external_emojis = False
        self.view_guild_insights = False
        self.connect = False
        self.speak = False
        self.mute_members = False
        self.deafen_members = False
        self.move_members = False
        self.use_vad = False
        self.change_nickname = False
        self.manage_nicknames = False
        self.manage_roles = False
        self.manage_webhooks = False
        self.manage_emojis = False
        self.owner = False
        self.flags = [
            "create_instant_invite",
            "kick_members",
            "ban_members",
            "administrator",
            "manage_channels",
            "manage_guild",
            "add_reactions",
            "view_audit_log",
            "priority_speaker",
            "stream",
            "view_channel",
            "send_messages",
            "send_tts_messages",
            "manage_messages",
            "embed_links",
            "attach_files",
            "read_message_history",
            "mention_everyone",
            "use_external_emojis",
            "view_guild_insights",
            "connect",
            "speak",
            "mute_members",
            "deafen_members",
            "move_members",
            "use_vad",
            "change_nickname",
            "manage_nicknames",
            "manage_roles",
            "manage_webhooks",
            "manage_emojis",
            "owner",
        ]
        for i, flag in enumerate(self.flags):
            setattr(self, flag, ((self.bit >> (i)) & 1) == 1)

    def to_json(self):
        return {flag: getattr(self, flag) for flag in self.flags}

    @classmethod
    def from_json(cls, payload):
        obj = cls(0)
        for attr, flag in payload.items():
            if hasattr(obj, attr):
                setattr(obj, attr, flag)
        return obj

    @property
    def is_admin(self):
        return self.owner or self.administrator

    @property
    def can_manage_guild(self):
        return self.is_admin() or self.manage_guild

    @property
    def can_manage_roles(self):
        return self.is_admin() or self.manage_roles

    @property
    def can_manage_messages(self):
        return self.is_admin() or self.manage_messages
