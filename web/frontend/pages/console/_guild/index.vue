<template>
  <div>
    <v-container>
      <ControllBar title="ホーム" />
      <div v-if="!is404 && guild">
        <v-row>
          <v-col cols="2" lg="1" offset-lg="1" offset-xl="2">
            <v-avatar size="100%">
              <v-img v-if="guild.icon" :src="guild.icon_url" />
              <v-img v-else src="/noimage.png" />
            </v-avatar>
          </v-col>
          <v-col cols="10" lg="9" xl="7">
            <h1 class="text-h4 mt-5">
              {{ guild.name }}
            </h1>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" lg="10" xl="8" offset-lg="1" offset-xl="2">
            <v-card>
              <v-tabs v-model="tab" grow icons-and-text>
                <v-tabs-slider />
                <v-tab href="#tab-1">
                  機能一覧
                  <v-icon>mdi-robot</v-icon>
                </v-tab>
                <v-tab href="#tab-2">
                  ユーザー
                  <v-icon>mdi-account</v-icon>
                </v-tab>
                <v-tab href="#tab-3">
                  設定
                  <v-icon>mdi-cog</v-icon>
                </v-tab>
                <v-tab href="#tab-4">
                  支援
                  <v-icon>mdi-gift-outline</v-icon>
                </v-tab>
              </v-tabs>
              <v-tabs-items v-model="tab">
                <v-tab-item value="tab-1">
                  <v-card flat>
                    <v-container>
                      <v-row>
                        <v-col
                          v-for="command in commands"
                          :key="command.title"
                          cols="12"
                          sm="6"
                          md="4"
                        >
                          <v-card outlined :to="command.to" append nuxt>
                            <v-list-item class="mb-n6" two-line>
                              <v-list-item-avatar tile size="80">
                                <v-icon size="80" v-text="command.icon" />
                              </v-list-item-avatar>
                              <v-list-item-content>
                                <v-list-item-title class="headline mb-1">
                                  {{ command.title }}
                                </v-list-item-title>
                                <v-list-item-subtitle
                                  v-text="command.subtitle"
                                />
                              </v-list-item-content>
                            </v-list-item>
                            <v-card-text v-text="command.description" />
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-card>
                </v-tab-item>
                <v-tab-item value="tab-2">
                  <v-card flat>
                    <v-card-title class="justify-center mb-n10 mt-3 text-h5">
                      自分の情報
                    </v-card-title>
                    <v-card-text>
                      <UserInfo
                        ref="form"
                        :user="user"
                        :guild="guild"
                        @dirty="dirty"
                      />
                    </v-card-text>
                    <v-divider />
                    <v-card-title class="justify-center mt-3 text-h5">
                      サーバーメンバー
                    </v-card-title>
                    <v-card-text>
                      <v-data-table
                        :headers="memberHeaders"
                        :items="memberItems"
                        :items-per-page="2"
                        :server-items-length="guild.approximate_member_count"
                        :loading="loading"
                        locale="ja-jp"
                        loading-text="Loading ..."
                        :footer-props="{
                          'items-per-page-options': [10, 25, 50, 100],
                        }"
                        style="cursor: pointer;"
                        :options.sync="options"
                      >
                        <template #item="{ item }">
                          <tr @click="onClickRow(item)">
                            <td>
                              <v-avatar size="40" class="mr-2">
                                <v-img :src="getIcon(item)" />
                              </v-avatar>
                              {{ item.user.username }}
                            </td>
                            <td>
                              {{ item.nick }}
                            </td>
                            <td>
                              <v-icon v-if="item.isOwner" color="indigo">
                                mdi-check
                              </v-icon>
                            </td>
                            <td>
                              <v-icon v-if="item.isAdmin" color="primary">
                                mdi-check
                              </v-icon>
                            </td>
                            <td>
                              <v-icon v-if="item.isGuildManager" color="purple">
                                mdi-check
                              </v-icon>
                            </td>
                            <td>
                              <v-icon v-if="item.isRoleManager" color="green">
                                mdi-check
                              </v-icon>
                            </td>
                            <td>
                              <v-icon v-if="item.isModerator" color="orange">
                                mdi-check
                              </v-icon>
                            </td>
                            <td>
                              <v-icon v-if="item.isBot" color="red">
                                mdi-check
                              </v-icon>
                            </td>
                          </tr>
                        </template>
                      </v-data-table>
                      <v-dialog
                        v-for="member in members"
                        :key="member.user.id"
                        v-model="member.dialog"
                      >
                        <v-card>
                          <v-card-text>
                            <UserInfo
                              ref="form"
                              :user="member"
                              :guild="guild"
                              @dirty="dirty"
                            />
                          </v-card-text>
                        </v-card>
                      </v-dialog>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                <v-tab-item value="tab-3">
                  <Settings
                    ref="form"
                    :user="guild.user"
                    :guild="guild"
                    @dirty="dirty"
                  />
                </v-tab-item>
                <v-tab-item value="tab-4">
                  <v-card flat>
                    <v-card-text>
                      Lorem ipsum dolor sit amet consectetur adipisicing elit.
                      Sequi quaerat eius, sint repudiandae omnis cumque
                      reiciendis. Soluta, dolor neque recusandae, beatae,
                      voluptates quibusdam veritatis veniam quos id sequi
                      debitis deleniti?
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </v-card>
          </v-col>
        </v-row>
      </div>
      <p v-else-if="is404" class="mt-6 text-center">
        サーバーを発見できませんでした
      </p>
      <p v-else class="mt-6 text-center">
        Loading...
      </p>
    </v-container>
    <UnsavedDialog v-model="isDirty" @reset="reset" @submit="submit" />
  </div>
</template>

<script lang="ts">
import { Vue, Component, Watch } from 'vue-property-decorator'
import { GuildDetail, Member } from '@/types/discord'
import ControllBar from '@/components/general/ControllBar.vue'
import UserInfo from '@/components/home/UserInfo.vue'
import Settings from '@/components/home/Settings.vue'
import UnsavedDialog from '@/components/general/UnsavedDialog.vue'
import { Route, NavigationGuardNext } from 'vue-router'
import { getModule } from 'vuex-module-decorators'
import NotificationModule from '@/store/notification'

import 'cookie-universal-nuxt'
import '@nuxtjs/axios'

Component.registerHooks(['beforeRouteLeave'])

@Component({
  name: 'GuildHome',
  components: {
    ControllBar,
    UserInfo,
    UnsavedDialog,
    Settings,
  },
  asyncData: async ({ redirect, store, app, $axios }) => {
    if (store.getters['auth/accessToken'] && store.getters['auth/user']) {
      return { userdata: store.getters['auth/user'] }
    } else if (app.$cookies.get('access_token')) {
      store.dispatch('auth/setAccessToken', app.$cookies.get('access_token'))
      store.dispatch('auth/setRefreshToken', app.$cookies.get('refresh_token'))
      try {
        const { data } = await $axios.get('/api/users/@me')
        store.dispatch('auth/setUser', data)
        return { userdata: data }
      } catch {
        redirect(301, '/')
      }
    } else {
      redirect(301, '/')
    }
  },
})
class Index extends Vue {
  guild: GuildDetail | null = null
  members: Array<Member & { dialog: boolean }> = []
  prevMembers: { [x: string]: Array<Member & { dialog: boolean }> } = {}
  is404 = false
  loading = false
  tab = 1

  options = {
    page: 1,
    itemsPerPage: 10,
  }

  prevPage = 1
  currId = ''

  @Watch('options', { deep: true })
  async onOptionChanged() {
    if (this.options.page > this.prevPage) {
      this.currId =
        this.members.length > 0
          ? this.members[this.members.length - 1].user.id
          : '0'
      this.prevMembers[this.prevPage.toString()] = JSON.parse(
        JSON.stringify(this.members)
      )
      this.prevPage = this.options.page
    } else {
      if (this.options.page < 2) {
        this.currId = '0'
      } else {
        this.currId = this.prevMembers[this.options.page - 1][
          this.prevMembers[this.options.page - 1].length - 1
        ].user.id
      }
      this.prevPage = this.options.page
    }
    this.loading = true
    const { data } = await this.$axios.get('/local_api/members', {
      params: {
        guild_id: this.$route.params.guild,
        offset: this.currId,
        limit: this.options.itemsPerPage,
      },
    })
    this.members = data.map((member: Member) => ({ ...member, dialog: false }))
    this.loading = false
  }

  isDirty = false

  memberHeaders = [
    { text: 'Name', value: 'name', sortable: false },
    { text: 'Nick', value: 'nick', sortable: false },
    { text: 'オーナー', value: 'isOwner', sortable: false },
    { text: '管理者', value: 'isAdmin', sortable: false },
    { text: 'サーバー管理者', value: 'isGuildManager', sortable: false },
    { text: 'ロール管理者', value: 'isRoleManager', sortable: false },
    { text: 'モデレーター', value: 'isModerator', sortable: false },
    { text: 'Bot', value: 'isBot', sortable: false },
  ]

  getIcon(member: Member) {
    const id = member.user.id
    const av = member.user.avatar
    if (av) {
      return `https://cdn.discordapp.com/avatars/${id}/${av}`
    }
  }

  onClickRow(member: Member) {
    const idx = this.members.findIndex((m) => m.user.id === member.user.id)
    this.members[idx].dialog = true
  }

  get user() {
    return this.guild ? this.guild.user : {}
  }

  get memberItems() {
    return this.members.map((member) => {
      const p = member.permissions
      return {
        isOwner: p && p.owner,
        isAdmin: p && p.administrator,
        // eslint-disable-next-line camelcase
        isGuildManager: p && p.manage_guild,
        // eslint-disable-next-line camelcase
        isRoleManager: p && p.manage_roles,
        // eslint-disable-next-line camelcase
        isModerator:
          p &&
          p.kick_members &&
          p.ban_members &&
          p.mute_members &&
          p.deafen_members &&
          p.move_members &&
          p.manage_messages,
        isBot: member.user.bot,
        ...member,
      }
    })
  }

  beforeRouteLeave(_to: Route, _from: Route, next: NavigationGuardNext<Vue>) {
    if (this.isDirty) {
      const elements = document.getElementsByClassName('container')
      Array.prototype.slice.call(elements).forEach((element) => {
        element.classList.add('vibration')
        setTimeout(() => {
          element.classList.remove('vibration')
        }, 500)
      })
      const alerts = document.getElementsByClassName('alert')
      Array.prototype.slice.call(alerts).forEach((alert) => {
        alert.classList.add('alerting')
        setTimeout(() => {
          alert.classList.remove('alerting')
        }, 1000)
      })
    } else {
      next()
    }
  }

  commands = [
    {
      icon: 'mdi-calendar',
      title: 'リマインダー',
      subtitle: '!>reminder',
      description: 'リマインダーの新規作成や変更，削除を行います',
      to: 'reminder',
    },
  ]

  async mounted() {
    if (this.$route.params.guild) {
      const { data } = await this.$axios.get('/local_api/guild', {
        params: {
          guild_id: this.$route.params.guild,
        },
      })
      if (data.status_code === 404) {
        this.is404 = true
        return
      }
      this.guild = data
    } else {
      this.is404 = true
    }
  }

  reset() {
    const refs: any = this.$refs.form
    if (Array.isArray(refs)) {
      refs.forEach((ref: any) => {
        ref.reset()
      })
    } else {
      refs.reset()
    }
    this.isDirty = false
  }

  async submit() {
    const refs: any = this.$refs.form
    const module = getModule(NotificationModule, this.$store)
    let valid = true
    try {
      if (Array.isArray(refs)) {
        await refs.forEach(async (ref: any) => {
          valid = valid && ref.validate()
          await ref.save()
        })
      } else {
        await refs.save()
        valid = valid && refs.validate()
        module.setSnackBarContent({
          content: '正常に保存されました．再読み込みします',
          color: 'success',
        })
      }
    } catch {
      module.setSnackBarContent({
        content: '申し訳ありませんがセーブに失敗しました',
        color: 'error',
      })
    }

    if (!valid) {
      module.setSnackBarContent({
        content: '不正な値が入力されているため保存できません',
        color: 'error',
      })
      module.fireSnackBar()
      return
    }

    module.fireSnackBar()
    this.isDirty = false
    setTimeout(() => {
      location.reload(true)
    }, 2000)
  }

  dirty(state: boolean) {
    this.isDirty = state
  }
}
export default Index
</script>

<style>
.vibration {
  animation: vibrate 0.2s infinite;
}
@keyframes vibrate {
  0% {
    transform: translate(0, 0) rotateZ(0deg);
  }
  25% {
    transform: translate(2px, 4px) rotateZ(1deg);
  }
  50% {
    transform: translate(-1px, 4px) rotateZ(0deg);
  }
  75% {
    transform: translate(2px, 0) rotateZ(1deg);
  }
  100% {
    transform: translate(0, 0) rotateZ(0deg);
  }
}

.alerting {
  animation: alert 0.8s ease-in-out;
}
@keyframes alert {
  0%,
  100% {
    background: inherit;
  }

  50% {
    background: #e13;
  }
}
</style>
