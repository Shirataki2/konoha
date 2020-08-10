<template>
  <v-app dark>
    <AppHeader />
    <v-main class="mb-8">
      <nuxt />
    </v-main>
    <SnackBar />
    <AppFooter />
  </v-app>
</template>

<script lang="ts">
import AppHeader from '@/components/general/AppHeader.vue'
import AppFooter from '@/components/general/AppFooter.vue'
import SnackBar from '@/components/general/SnackBar.vue'
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'app',
  components: {
    AppFooter,
    AppHeader,
    SnackBar,
  },
})
class App extends Vue {}
export default App
</script>
