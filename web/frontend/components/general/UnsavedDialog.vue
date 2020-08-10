<template>
  <v-alert
    v-model="visible"
    class="alert"
    border="right"
    transition="slide"
    color="gray darken-3"
    type="warning"
    prominent
    style="
      border: solid 1px #333;
      position: fixed;
      right: 30px;
      bottom: 30px;
      z-index: 99999;
    "
  >
    <p class="ml-7 mr-7">
      <strong>未保存の変更があります</strong>
    </p>
    <div class="text-center">
      <v-btn color="error" text large @click="reset">
        <strong>破棄</strong>
      </v-btn>
      <v-btn color="success" text large @click="submit">
        <strong>保存</strong>
      </v-btn>
    </div>
  </v-alert>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

@Component({
  name: 'UnsavedDialog',
})
class UnsavedDialog extends Vue {
  @Prop({ type: Boolean, default: false })
  value!: boolean

  get visible() {
    return this.value
  }

  set visible(value: boolean) {
    this.$emit('input', value)
  }

  reset() {
    this.$emit('reset')
  }

  submit() {
    this.$emit('submit')
  }
}
export default UnsavedDialog
</script>

<style scoped>
.slide-leave-active,
.slide-enter-active {
  transition: 0.4s;
}
.slide-enter {
  transform: translate(100%, 0);
}
.slide-leave-to {
  transform: translate(100%, 0);
}
</style>
