<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12" sm="6" lg="4">
          <v-dialog
            v-for="action in actions"
            :key="action.name"
            v-model="action.dialog"
            :disabled="!action.permission()[0]"
            max-width="600"
            persistent
          >
            <template v-slot:activator="{ on: dialog }">
              <v-tooltip top :disabled="action.permission()[0]">
                <template v-slot:activator="{ on: tooltip, attrs }">
                  <div v-on="{ ...tooltip, ...dialog }">
                    <v-card
                      v-bind="attrs"
                      outlined
                      :disabled="!action.permission()[0]"
                    >
                      <v-card-title v-text="action.name" />
                      <v-card-subtitle v-text="action.description" />
                    </v-card>
                  </div>
                </template>
                <span v-text="action.permission()[1]" />
              </v-tooltip>
            </template>
            <component :is="action.component" @cancel="action.dialog = false" />
          </v-dialog>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { GuildDetail, Permission, Member } from '@/types/discord'
import Ban from '@/components/moderations/Ban.vue'
@Component({
  name: 'Moderator',
  components: {
    Ban,
  },
})
class Moderator extends Vue {
  @Prop({ type: Object, default: () => {} })
  guild!: GuildDetail

  @Prop({ type: Object, default: () => {} })
  user!: Member

  withAdmin(permission: Permission, p: boolean) {
    return permission.owner || permission.administrator || p
  }

  getHighestRole(user: Member) {
    if (user.permissions?.owner) {
      return 100000
    }
    let highest = 0
    this.guild.roles.forEach((role) => {
      user.roles.forEach((userRole) => {
        if (userRole === role.id) {
          highest = Math.max(highest, role.position)
        }
      })
    })
    return highest
  }

  actions = [
    {
      name: 'Ban',
      description: 'このユーザをサーバからBANします',
      permission: () => {
        const isNotMyself = this.guild.user.user.id !== this.user.user.id
        const botPosition = this.guild.roles.find(
          (role) => role.tags && role.tags.bot_id === process.env.bot_id
        )?.position
        if (!botPosition) return [false, 'ユーザをBANする権限がありません']
        const canBotBan = this.getHighestRole(this.user) < botPosition
        const canUserBan =
          this.getHighestRole(this.user) < this.getHighestRole(this.guild.user)
        const perms = this.guild.user.permissions
        if (perms) {
          const canBan = this.withAdmin(perms, perms.ban_members)
          if (!isNotMyself) return [false, '自身をBANすることはできません']
          if (!canBan) return [false, 'ユーザをBANする権限がありません']
          if (!canUserBan)
            return [
              false,
              'BAN対象がより高いロールのメンバーなのでBANできません',
            ]
          if (!canBotBan)
            return [false, 'このBotより高いロールのメンバーはBANできません']
          return [true, '']
        } else {
          return [false, 'ユーザをBANする権限がありません']
        }
      },
      component: Ban,
      dialog: false,
    },
  ]

  get isChanged() {
    return false
  }

  validate() {
    return true
  }

  async save() {}

  reset() {}
}
export default Moderator
</script>
