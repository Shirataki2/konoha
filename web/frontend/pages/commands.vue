<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4">コマンド一覧</h1>
        </v-col>
      </v-row>
      <v-divider />
      <v-row>
        <v-col class="hidden-xs-only" sm="3" md="3" lg="3" offset-lg="1">
          <div style="position: sticky; top: 0;">
            <v-list>
              <v-list-item-group v-model="currentPage" color="blue" mandatory>
                <v-list-item v-for="page in pages" :key="page.slug">
                  <v-list-item-title v-text="page.title" />
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </div>
        </v-col>
        <v-col class="hidden-sm-and-up" cols="12">
          <div>
            <v-select
              :items="pages"
              item-text="title"
              item-value="title"
              @change="onCogSelected(selected)"
            />
          </div>
        </v-col>
        <v-col cols="12" sm="9" md="9" lg="7">
          <div v-if="pages">
            <nuxt-content :document="currentDocument" />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

interface Page {
  body: Object
  createdAt: String
  description: String
  dir: String
  extention: String
  path: String
  slug: String
  title: String
  updatedAt: String
}

@Component({
  name: 'Commands',
  asyncData: async ({ $content, store, app, $axios }) => {
    const pages = await $content('commands').sortBy('description').fetch()
    if (store.getters['auth/accessToken'] && store.getters['auth/user']) {
      return { userdata: store.getters['auth/user'] }
    } else if (app.$cookies.get('access_token')) {
      store.dispatch('auth/setAccessToken', app.$cookies.get('access_token'))
      store.dispatch('auth/setRefreshToken', app.$cookies.get('refresh_token'))
      try {
        const { data } = await $axios.get('/api/users/@me')
        store.dispatch('auth/setUser', data)
        return { userdata: data, pages }
      } catch {
        return { pages }
      }
    } else {
      return { pages }
    }
  },
})
class Commands extends Vue {
  currentPage = 0
  pages: Array<Page> = []

  get currentDocument() {
    return this.pages[this.currentPage]
  }

  onCogSelected(selected) {
    console.log(selected)
  }
}
export default Commands
</script>
