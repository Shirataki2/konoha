<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12" sm="6" lg="4">
          <v-dialog
            v-for="action in actions"
            :key="action.name"
            v-model="action.dialog"
            :disabled="!action.permission()"
            max-width="600"
            persistent
          >
            <template v-slot:activator="{ on: dialog }">
              <v-tooltip top :disabled="action.permission()">
                <template v-slot:activator="{ on: tooltip, attrs }">
                  <div v-on="{ ...tooltip, ...dialog }">
                    <v-card
                      v-bind="attrs"
                      outlined
                      :disabled="!action.permission()"
                    >
                      <v-card-title v-text="action.name" />
                      <v-card-subtitle v-text="action.description" />
                    </v-card>
                  </div>
                </template>
                <span v-text="action.alert()" />
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

  actions = [
    {
      name: 'Ban',
      description: 'このユーザをサーバからBANします',
      alert: () => {
        if (this.guild.user.user.id === this.user.user.id) {
          return '自身をBANすることはできません'
        } else {
          return 'ユーザをBANする権限がありません'
        }
      },
      permission: () => {
        const isNotMyself = this.guild.user.user.id !== this.user.user.id
        const perms = this.guild.user.permissions
        if (perms) {
          const canBan = this.withAdmin(perms, perms.ban_members)
          return isNotMyself && canBan
        } else {
          return false
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
