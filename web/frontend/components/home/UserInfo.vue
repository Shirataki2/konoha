<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-list-item class="mb-n6" two-line>
            <v-list-item-avatar
              tile
              max-width="160"
              max-height="160"
              width="20%"
              height="20%"
            >
              <v-avatar size="100%">
                <v-img :src="iconUrl" />
              </v-avatar>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title class="text-h4 mb-1">
                {{ name }}
                <span
                  v-if="nickname"
                  class="text-h5 grey--text text--darken-2"
                  v-text="nickname"
                />
              </v-list-item-title>
              <v-list-item-subtitle v-text="joinedAt" />
              <v-chip-group column>
                <div v-for="badge in badges" :key="badge.name">
                  <v-chip
                    v-if="badge.value()"
                    dark
                    disabled
                    style="opacity: 1;"
                    :color="badge.color"
                    v-text="badge.name"
                  />
                </div>
              </v-chip-group>
            </v-list-item-content>
          </v-list-item>
        </v-col>
        <v-col v-if="guild" cols="12">
          <v-expansion-panels popout flat>
            <v-expansion-panel
              v-for="panel in panels"
              :key="panel.name"
              style="border: solid 1px #333;"
            >
              <v-expansion-panel-header
                v-if="panel.permission()"
                expand-icon="$expand"
                :hide-actions="true"
                class="font-weight-bold subtitle-1"
                v-text="panel.name"
              />
              <v-expansion-panel-content v-if="panel.permission()">
                <component
                  :is="panel.component"
                  ref="panel"
                  :guild="guild"
                  :user="user"
                  @dirty="dirty"
                />
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { Member, GuildDetail } from '@/types/discord'
import RoleEdit from '@/components/home/RoleEdit.vue'
import Moderator from '@/components/home/Moderator.vue'
@Component({
  name: 'UserList',
  components: {
    RoleEdit,
    Moderator,
  },
})
class UserList extends Vue {
  @Prop({ type: Object, default: () => ({}) })
  user!: Member

  @Prop({ type: Object, default: () => ({}) })
  guild!: GuildDetail

  panels = [
    {
      name: 'ロール管理',
      component: RoleEdit,
      permission: () => {
        if (this.user.user.bot) return false
        const p = this.guild.user.permissions
        return p && (p.owner || p.administrator || p.manage_roles)
      },
    },
    {
      name: 'モデレーション',
      component: Moderator,
      permission: () => {
        if (this.user.user.bot) return false
        const p = this.guild.user.permissions
        return (
          p &&
          ((p.kick_members &&
            p.ban_members &&
            p.mute_members &&
            p.deafen_members &&
            p.move_members &&
            p.manage_messages) ||
            p.owner ||
            p.administrator)
        )
      },
    },
  ]

  badges = [
    {
      name: 'サーバーオーナー',
      value: () => {
        const p = this.user.permissions
        return p && p.owner
      },
      color: 'indigo',
    },
    {
      name: '管理者',
      value: () => {
        const p = this.user.permissions
        return p && p.administrator
      },
      color: 'primary',
    },
    {
      name: 'サーバー管理者',
      value: () => {
        const p = this.user.permissions
        return p && p.manage_guild
      },
      color: 'purple',
    },
    {
      name: 'ロール管理者',
      value: () => {
        const p = this.user.permissions
        return p && p.manage_roles
      },
      color: 'green',
    },
    {
      name: 'モデレーター',
      value: () => {
        const p = this.user.permissions
        return (
          p &&
          p.kick_members &&
          p.ban_members &&
          p.mute_members &&
          p.deafen_members &&
          p.move_members &&
          p.manage_messages
        )
      },
      color: 'orange',
    },
    {
      name: 'Bot',
      value: () => {
        return this.user.user.bot
      },
      color: 'red',
    },
  ]

  get iconUrl() {
    if (this.user.user.avatar) {
      return `http://cdn.discordapp.com/avatars/${this.user.user.id}/${this.user.user.avatar}`
    } else {
      return '/noimage.png'
    }
  }

  get name() {
    if (this.user.nick) {
      return this.user.nick
    } else {
      return this.user.user.username
    }
  }

  get nickname() {
    if (this.user.nick) {
      return `/ ${this.user.user.username}`
    } else {
      return null
    }
  }

  get joinedAt() {
    const d = new Date(this.user.joined_at)
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日に参加`
  }

  get isOwner() {
    return this.user.permissions?.owner
  }

  dirty(state: boolean) {
    this.$emit('dirty', state)
  }

  async save() {
    const refs: any = this.$refs.panel
    if (Array.isArray(refs)) {
      await refs.forEach(async (ref: any) => {
        await ref.save()
      })
    } else {
      await refs.save()
    }
  }

  validate() {
    let valid = true
    const refs: any = this.$refs.panel
    if (Array.isArray(refs)) {
      refs.forEach((ref: any) => {
        valid = valid && ref.validate()
      })
    } else {
      valid = valid && refs.validate()
    }
    return valid
  }

  reset() {
    const refs: any = this.$refs.panel
    if (Array.isArray(refs)) {
      refs.forEach((ref: any) => {
        ref.reset()
      })
    } else {
      refs.reset()
    }
  }
}
export default UserList
</script>
