<template>
  <div>
    <p class="text-center mt-8">
      リダイレクト中...
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
    location.href = process.env.login_url
  }
}
export default Login
</script>
