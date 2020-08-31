<template>
  <v-app dark>
    <AppHeader />
    <v-main class="mb-8">
      <nuxt />
      <FloatButton />
    </v-main>
    <SnackBar />
    <AppFooter />
  </v-app>
</template>

<script lang="ts">
import AppHeader from '@/components/general/AppHeader.vue'
import AppFooter from '@/components/general/AppFooter.vue'
import SnackBar from '@/components/general/SnackBar.vue'
import FloatButton from '@/components/general/FloatButton.vue'
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'app',
  components: {
    AppFooter,
    AppHeader,
    SnackBar,
    FloatButton,
  },
})
class App extends Vue {
  mounted() {
    const isDark = localStorage.getItem('isDark')
    if (isDark) {
      this.$vuetify.theme.dark = isDark.toLowerCase() === 'true'
    } else {
      localStorage.setItem('isDark', 'true')
    }
  }
}
export default App
</script>
