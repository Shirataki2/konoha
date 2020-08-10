<template>
  <div>
    <v-app-bar color="grey darken-4" dark>
      <v-app-bar-nav-icon
        class="hidden-sm-and-up mr-n3"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>
      <v-toolbar-title style="cursor: pointer;" @click="$router.push('/')">
        <strong>Konoha Bot</strong>
      </v-toolbar-title>
      <v-spacer />
      <div v-if="isLogin">
        <v-btn x-large text active-class="no-active">
          <v-avatar size="40">
            <v-img :src="imgPath" />
          </v-avatar>
          <span class="ml-4">
            {{ username }}
          </span>
        </v-btn>
        <v-btn to="/console" large text nuxt active-class="no-active">
          <v-icon>mdi-console-line</v-icon>
          Console
        </v-btn>
        <v-btn to="/logout" large text nuxt active-class="no-active">
          <v-icon>mdi-logout</v-icon>
          Logout
        </v-btn>
      </div>
      <div v-else>
        <v-btn large :href="oauth2Url" text nuxt active-class="no-active">
          <v-icon>mdi-login</v-icon>
          Login
        </v-btn>
      </div>
    </v-app-bar>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

@Component({})
class AppHeader extends Vue {
  drawer = false

  oauth2Url =
    'https://discord.com/api/oauth2/authorize?client_id=740158924476645396&redirect_uri=http%3A%2F%2F192.168.10.19%3A3000%2Fcallback&response_type=code&scope=identify%20guilds%20email'

  get isLogin() {
    return this.$store.getters['auth/user'] !== null
  }

  get imgPath() {
    const user = this.$store.getters['auth/user']
    return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}`
  }

  get username() {
    const user = this.$store.getters['auth/user']
    return user.username
  }
}
export default AppHeader
</script>
