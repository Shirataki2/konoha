<template>
  <v-navigation-drawer
    :value="drawer"
    clipped
    app
    @input="toggleDrawer($event)"
  >
    <v-list>
      <div v-for="item in items" :key="item.title">
        <v-list-item
          v-if="isShow(item.needLogin, item.needLogout, isLogin)"
          link
          nuxt
          color="blue"
          :to="item.to"
        >
          <v-list-item-icon>
            <v-icon v-text="item.icon" />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title v-text="item.title" />
          </v-list-item-content>
        </v-list-item>
      </div>
    </v-list>
    <template #append>
      <div v-for="item in bottomItems" :key="item.title">
        <v-list-item
          v-if="isShow(item.needLogin, item.needLogout, isLogin)"
          color="blue"
          @click="item.func()"
        >
          <v-list-item-icon>
            <v-icon v-text="item.icon()" />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title v-text="item.title" />
          </v-list-item-content>
        </v-list-item>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { Vue, Component, Prop, Model } from 'vue-property-decorator'

@Component({})
class AppNavBar extends Vue {
  @Model('input', { default: null })
  drawer!: boolean | null

  @Prop({ type: Boolean, default: false })
  isLogin!: boolean

  items = [
    {
      title: 'コマンド一覧',
      icon: 'mdi-robot',
      to: '/commands',
      needLogin: false,
      needLogout: false,
      section: false,
    },
    {
      title: '管理コンソール',
      icon: 'mdi-console-line',
      to: '/console',
      needLogin: true,
      needLogout: false,
      section: false,
    },
    {
      title: '利用規約',
      icon: 'mdi-book-open',
      to: '/support/tos',
      needLogin: false,
      needLogout: false,
      section: false,
    },
    {
      title: 'ログアウト',
      icon: 'mdi-logout',
      to: '/logout',
      needLogin: true,
      needLogout: false,
      section: false,
    },
    {
      title: 'ログイン',
      icon: 'mdi-login',
      to: '/login',
      needLogin: false,
      needLogout: true,
      section: false,
    },
  ]

  themeIcon() {
    if (this.isDark) {
      return 'mdi-brightness-4'
    } else {
      return 'mdi-brightness-7'
    }
  }

  get isDark() {
    return this.$vuetify.theme.dark
  }

  bottomItems = [
    {
      title: 'テーマ変更',
      icon: () => this.themeIcon(),
      func: () => {
        this.$vuetify.theme.dark = !this.$vuetify.theme.dark
        localStorage.setItem('isDark', this.$vuetify.theme.dark.toString())
      },
      needLogin: false,
      needLogout: false,
    },
  ]

  isShow(A: boolean, B: boolean, C: boolean) {
    if (A && B) return false
    if (!A && !B) return true
    if (A && !B && !C) return false
    if (!A && B && C) return false
    if (A && !B && C) return true
    if (!A && B && !C) return true
  }

  toggleDrawer($event) {
    this.$emit('input', $event)
  }
}
export default AppNavBar
</script>
