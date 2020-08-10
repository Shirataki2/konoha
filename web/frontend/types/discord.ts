/* eslint-disable camelcase */
export interface Guild {
  id: string
  name: string
  icon: string | null
  owner: boolean
  permissions: number
  icon_url?: string | null
  joined?: number
  user: Member
}

export interface Emoji {
  name: string
  id: string
  animated: boolean
}

export interface Role {
  id: string
  name: string
  permissions: number
  position: number
  color: number
  hoist: boolean
  managed: boolean
  mentionable: boolean
  tags: any
}

export interface GuildDetail {
  id: string
  name: string
  icon: string | null
  emojis: Array<Emoji>
  roles: Array<Role>
  owner_id: string
  region: string
  icon_url?: string | null
  approximate_member_count: number
  approximate_presence_count: number
  user: Member
}

export interface User {
  id: string
  username: string
  avatar: string
  discriminator: string
  public_flags: number
  bot: true | undefined
}

export interface Permission {
  create_instant_invite: boolean
  kick_members: boolean
  ban_members: boolean
  administrator: boolean
  manage_channels: boolean
  manage_guild: boolean
  add_reactions: boolean
  view_audit_log: boolean
  priority_speaker: boolean
  stream: boolean
  view_channel: boolean
  send_messages: boolean
  send_tts_messages: boolean
  manage_messages: boolean
  embed_links: boolean
  attach_files: boolean
  read_message_history: boolean
  mention_everyone: boolean
  use_external_emojis: boolean
  view_guild_insights: boolean
  connect: boolean
  speak: boolean
  mute_members: boolean
  deafen_members: boolean
  move_members: boolean
  use_vad: boolean
  change_nickname: boolean
  manage_nicknames: boolean
  manage_roles: boolean
  manage_webhooks: boolean
  manage_emojis: boolean
  owner: boolean
}

export interface Member {
  user: User
  roles: Array<string>
  nick: string | null
  premium_since: string
  joined_at: string
  mute: boolean
  deaf: boolean
  permissions?: Permission
}
