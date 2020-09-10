from discord.ext.commands import CheckFailure


class KonohaException(Exception):
    def __init__(self, message=None, *args):
        if message is not None:
            # clean-up @everyone and @here mentions
            m = message.replace(
                '@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
            super().__init__(m, *args)
        else:
            super().__init__(*args)


class KonohaCheckFailure(CheckFailure):
    pass


class InvalidColorException(KonohaException):
    pass


to_japanese = {
    'create_instant_invite': '招待を作成',
    'kick_members': 'メンバーをキック',
    'ban_members': 'メンバーをBAN',
    'administrator': '管理者',
    'manage_channel': 'チャンネルの管理',
    'manage_guild': 'サーバーの管理',
    'add_reaction': 'リアクションの追加',
    'view_audit_log': '監査ログの閲覧',
    'priority_speaker': '優先スピーカーの使用',
    'stream': '配信',
    'view_channel': 'メッセージの閲覧',
    'send_messages': 'メッセージの送信',
    'send_tts_messages': '読み上げメッセージの送信',
    'manage_messages': 'メッセージの管理',
    'embed_link': '埋め込みリンク',
    'attach_files': 'ファイルを添付',
    'read_message_history': 'メッセージ履歴の閲覧',
    'mention_everyone': '@everyone，@here，全てのロールにメンション',
    'external_emojis': '外部絵文字の使用',
    'use_external_emojis': '外部絵文字の使用',
    'view_guild_insight': 'サーバーインサイトの閲覧',
    'connect': 'ボイスチャンネルへの接続',
    'speak': 'ボイスチャンネルでの発言',
    'mute_members': 'メンバーをミュート',
    'deafen_members': 'メンバーのスピーカーをミュート',
    'move_members': 'メンバーを移動',
    'use_voice_activation': '音声検出の利用',
    'change_nickname': 'ニックネームの変更',
    'manage_nicknames': 'ニックネームの管理',
    'manage_roles': 'ロールの管理',
    'manage_permissions': 'ロールの管理',
    'manage_webhooks': 'Webhookの管理',
    'manage_emojis': '絵文字の管理',
}


class MissingPermissions(KonohaCheckFailure):
    def __init__(self, missing_perms, *args):
        self.missing_perms = missing_perms
        missing = '，'.join(
            [f'`{to_japanese.get(perm)}`' for perm in missing_perms]
        )
        msg = f'このコマンドを実行するには{missing}の権限が必要です'
        super().__init__(msg, *args)


class BotMissingPermissions(KonohaCheckFailure):
    def __init__(self, missing_perms, *args):
        self.missing_perms = missing_perms
        missing = '，'.join(
            [f'`{to_japanese.get(perm)}`' for perm in missing_perms]
        )
        msg = f'このコマンドを実行するにはBotに{missing}の権限が与えられている必要があります'
        super().__init__(msg, *args)
