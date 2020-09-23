<template>
  <div>
    <p class="text-center mt-8">
      作成中です
    </p>
  </div>
</template>

<script>
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'Login',
})
class Login extends Vue {
  mounted() {
    // location.href = process.env.login_url
  }
}
export default Login
</script>
