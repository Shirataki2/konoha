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
      <v-btn to="/commands" text nuxt active-class="no-active">
        Commands
      </v-btn>
      <div v-if="isLogin">
        <v-btn to="/console" text nuxt active-class="no-active">
          <v-icon>mdi-console-line</v-icon>
          Console
        </v-btn>
        <v-menu v-model="show" offset-y>
          <template #activator="{ on, attrs }">
            <v-btn text active-class="no-active" v-bind="attrs" v-on="on">
              <v-avatar size="36">
                <v-img :src="imgPath" />
              </v-avatar>
              <span class="ml-4 text-h6">
                {{ username }}
              </span>
            </v-btn>
          </template>
          <v-list>
            <v-list-item to="/logout" text nuxt active-class="no-active">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                Logout
              </v-list-item-title>
            </v-list-item>
            <v-list-item text active-class="no-active" @click="themeToggle">
              <v-list-item-icon>
                <v-icon v-text="themeIcon" />
              </v-list-item-icon>
              <v-list-item-title>
                Theme
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
      <div v-else>
        <v-btn text active-class="no-active" @click="themeToggle">
          <v-icon v-text="themeIcon" />
        </v-btn>
        <v-btn :href="oauth2Url" text nuxt active-class="no-active">
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
  show = false

  oauth2Url = process.env.login_url || '/'
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

  get themeIcon() {
    return this.$vuetify.theme.dark ? 'mdi-brightness-4' : 'mdi-brightness-7'
  }

  themeToggle() {
    this.$vuetify.theme.dark = !this.$vuetify.theme.dark
  }
}
export default AppHeader
</script>
