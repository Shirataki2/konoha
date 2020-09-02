<template>
  <div>
    <v-app-bar color="grey darken-4" dark app flat clipped-left>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title style="cursor: pointer;" @click="$router.push('/')">
        <strong>Konoha Bot</strong>
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        to="/commands"
        text
        nuxt
        active-class="no-active"
        class="hidden-xs-only"
      >
        Commands
      </v-btn>
      <div v-if="isLogin">
        <v-btn
          to="/console"
          text
          nuxt
          active-class="no-active"
          class="hidden-xs-only"
        >
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
            <v-list-item
              to="/console"
              class="hidden-sm-and-up"
              text
              nuxt
              active-class="no-active"
            >
              <v-list-item-icon>
                <v-icon>mdi-console-line</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                Console
              </v-list-item-title>
            </v-list-item>
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
        <v-btn to="/login" text nuxt active-class="no-active">
          <v-icon>mdi-login</v-icon>
          Login
        </v-btn>
      </div>
    </v-app-bar>
    <AppNavBar v-model="drawer" :is-login="isLogin" />
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AppNavBar from '@/components/general/NavBar.vue'

@Component({
  components: {
    AppNavBar,
  },
})
class AppHeader extends Vue {
  drawer = false
  show = false

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
    localStorage.setItem('isDark', this.$vuetify.theme.dark.toString())
  }
}
export default AppHeader
</script>
