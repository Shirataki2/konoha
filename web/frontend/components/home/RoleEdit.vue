<template>
  <div>
    <p>編集不可ロール</p>
    <v-chip
      v-for="role in unchangeableRole"
      :key="role.id"
      :color="getColor(role.color)"
    >
      {{ role.name }}
    </v-chip>
    <v-divider class="mt-4 mb-5" />
    <p>現在のロール</p>
    <draggable
      v-model="userrole"
      :group="`roleGroup_${user.user.id}`"
      :animation="200"
      @start="drag = true"
      @end="drag = false"
      @change="onChipChanged"
    >
      <v-chip
        v-for="role in userrole"
        :key="role.id"
        dark
        draggable
        :color="getColor(role.color)"
      >
        {{ role.name }}
      </v-chip>
    </draggable>
    <v-divider class="mt-4 mb-5" />
    <p>付けられるロール</p>
    <draggable
      v-model="unselectRoles"
      :group="`roleGroup_${user.user.id}`"
      :animation="200"
      @start="drag = true"
      @end="drag = false"
      @change="onChipChanged"
    >
      <v-chip
        v-for="role in unselectRoles"
        :key="role.id"
        dark
        draggable
        :color="getColor(role.color)"
      >
        {{ role.name }}
      </v-chip>
    </draggable>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { GuildDetail, Member, Role } from '@/types/discord'
import draggable from 'vuedraggable'

@Component({
  name: 'RoleEdit',
  components: {
    draggable,
  },
})
class RoleEdit extends Vue {
  @Prop({ type: Object, default: () => {} })
  guild!: GuildDetail

  @Prop({ type: Object, default: () => {} })
  user!: Member

  unchangeableRole: Array<Role> = []
  userrole: Array<Role> = []
  unselectRoles: Array<Role> = []
  roles: Array<Role> = []

  userrolePrev: Array<Role> = []
  unselectRolesPrev: Array<Role> = []

  drag = false

  options = {
    group: 'roleGroup',
    animation: 200,
  }

  getColor(color: number) {
    if (color === 0) {
      return '#666'
    } else {
      const r = (color >> 16) % 256
      const g = (color >> 8) % 256
      const b = color % 256
      return `rgb(${r}, ${g}, ${b})`
    }
  }

  getHighestRole() {
    if (this.guild.user.permissions?.owner) {
      return 100000
    }
    let highest = 0
    this.roles.forEach((role) => {
      this.guild.user.roles.forEach((userRole) => {
        if (userRole === role.id) {
          highest = Math.max(highest, role.position)
        }
      })
    })
    return highest
  }

  mounted() {
    this.roles = this.guild.roles
    const highest = this.getHighestRole()
    const botId = process.env.bot_id
    const botRole = this.roles.find(
      (role) => role.tags && role.tags.bot_id === botId
    )
    this.roles.forEach((role) => {
      const isBot = 'tags' in role
      const isEveryone = role.position === 0
      const isSuperior = role.position >= highest
      const isBotSuperior = botRole && role.position > botRole.position
      if (isBotSuperior || (isSuperior && !(isBot || isEveryone))) {
        if (this.user.roles.includes(role.id.toString()))
          this.unchangeableRole.push(role)
      } else if (isBot || isEveryone) {
      } else if (this.user.roles.includes(role.id.toString())) {
        this.userrole.push(role)
        this.userrolePrev.push(role)
      } else {
        this.unselectRoles.push(role)
        this.unselectRolesPrev.push(role)
      }
    })
  }

  get isChanged() {
    return (
      JSON.stringify(
        this.userrole.slice().sort((a, b) => Number(a.id < b.id))
      ) !==
      JSON.stringify(
        this.userrolePrev.slice().sort((a, b) => Number(a.id < b.id))
      )
    )
  }

  onChipChanged() {
    if (this.isChanged) {
      this.$emit('dirty', true)
    } else {
      this.$emit('dirty', false)
    }
  }

  validate() {
    return true
  }

  async save() {
    if (this.isChanged) {
      await this.$axios.patch(
        '/local_api/userrole',
        this.userrole.map((role) => role.id),
        {
          params: {
            guild_id: this.guild.id,
            user_id: this.user.user.id,
          },
        }
      )
    }
    this.userrolePrev = JSON.parse(JSON.stringify(this.userrole))
    this.unselectRolesPrev = JSON.parse(JSON.stringify(this.unselectRoles))
  }

  reset() {
    this.userrole = JSON.parse(JSON.stringify(this.userrolePrev))
    this.unselectRoles = JSON.parse(JSON.stringify(this.unselectRolesPrev))
  }
}
export default RoleEdit
</script>
