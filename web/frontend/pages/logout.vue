<template>
  <div>
    <p class="text-center mt-8">
      ログアウト中です
    </p>
  </div>
</template>

<script>
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'Logout',
})
class Logout extends Vue {
  async mounted() {
    const sleep = (msec) => new Promise((resolve) => setTimeout(resolve, msec))
    this.$cookies.remove('access_token')
    this.$cookies.remove('refresh_token')
    this.$cookies.remove('session')
    this.$store.dispatch('auth/setAccessToken', '')
    this.$store.dispatch('auth/setRefreshToken', '')
    this.$store.dispatch('auth/setUser', null)
    await sleep(500)
    this.$router.push('/')
  }
}
export default Logout
</script>
