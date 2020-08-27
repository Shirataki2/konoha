<template>
  <div>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
    <h1>Hi</h1>
  </div>
</template>

<script>
import queryString from 'querystring'
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'Callback',
  asyncData: async ({ query, $axios, redirect, app }) => {
    const code = query.code
    console.log(process.env.bot_id)
    console.log(process.env.bot_secret)
    console.log(process.env.bot_redirect_uri)
    const payload = {
      client_id: process.env.bot_id,
      client_secret: process.env.bot_secret,
      grant_type: 'authorization_code',
      redirect_uri: process.env.bot_redirect_uri,
      scope: 'identify email guilds',
      code,
    }
    const { data } = await $axios.post(
      '/api/oauth2/token',
      queryString.stringify(payload),
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      }
    )
    app.$cookies.set('access_token', data.access_token)
    app.$cookies.set('refresh_token', data.refresh_token)
    redirect(301, '/')
    // return { token: data }
  },
})
class Callback extends Vue {}
export default Callback
</script>
