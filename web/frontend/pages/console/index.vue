<template>
  <div>
    <h1 class="text-center text-h4 mt-10 mb-6">
      Konoha Bot 管理コンソール
    </h1>
    <v-container>
      <v-row>
        <v-col cols="12" md="10" offset-md="1">
          <p class="text-center mb-6">管理権限を持っているサーバーの一覧</p>
          <v-card v-if="!loading" class="mx-auto mt-3 mb-3">
            <v-list>
              <v-list-item
                v-for="guild in guilds"
                :key="guild.id"
                @click="onGuildClicked(guild)"
              >
                <v-list-item-avatar>
                  <div v-if="guild.icon">
                    <v-avatar>
                      <v-img :src="guild.icon_url" />
                    </v-avatar>
                  </div>
                  <div v-else>
                    <v-icon v-text="'mdi-account'" />
                  </div>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ guild.name }}
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn v-if="guild.joined" color="primary">
                    管理画面へ
                  </v-btn>
                  <v-btn v-else color="secondary">
                    Botを招待する
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card>
          <div v-else>
            <p class="text-center">
              参加中のサーバーを読み込んでいます
            </p>
          </div>
        </v-col>
        <v-col cols="12" md="10" offset-md="1">
          <p class="text-center mb-6">閲覧可能なサーバーの一覧</p>
          <v-card v-if="!loading" class="mx-auto mt-3 mb-3">
            <v-list>
              <v-list-item
                v-for="guild in guilds2"
                :key="guild.id"
                @click="onGuildClicked(guild)"
              >
                <v-list-item-avatar>
                  <div v-if="guild.icon">
                    <v-avatar>
                      <v-img :src="guild.icon_url" />
                    </v-avatar>
                  </div>
                  <div v-else>
                    <v-icon v-text="'mdi-account'" />
                  </div>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ guild.name }}
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn v-if="guild.joined" color="primary">
                    管理画面へ
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card>
          <div v-else>
            <p class="text-center">
              参加中のサーバーを読み込んでいます
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { Guild } from '@/types/discord'
import 'cookie-universal-nuxt'
import '@nuxtjs/axios'

@Component({
  name: 'GuildList',
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
  guilds: Array<Guild> = []
  guilds2: Array<Guild> = []
  loading = true

  async mounted() {
    try {
      const { data } = await this.$axios.get('/local_api/guilds', {
        params: {
          token: this.$store.getters['auth/accessToken'],
        },
      })
      this.guilds = data[0]
      this.guilds2 = data[1]
      this.loading = false
    } catch {
      this.$router.push('/')
    }
  }

  onGuildClicked(guild: Guild) {
    if (!guild.joined) {
      window.open(
        `${process.env.bot_url}&guild_id=${guild.id}`,
        'Discord',
        'menubar=no,location=no,resizable=no,scrollbar=no,width=500,height=700'
      )
    } else {
      this.$router.push(`/console/${guild.id}`)
    }
  }
}
export default Index
</script>
