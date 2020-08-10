<template>
  <div>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import 'cookie-universal-nuxt'
import '@nuxtjs/axios'

@Component({
  name: 'Home',
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
      } catch (e) {
        redirect(301, '/logout')
      }
    }
  },
})
class Index extends Vue {}
export default Index
</script>
