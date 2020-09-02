<template>
  <v-fab-transition>
    <v-btn
      v-show="show"
      v-scroll="onScroll"
      fixed
      dark
      fab
      large
      bottom
      right
      color="indigo"
      @click="goToTop"
    >
      <v-icon>mdi-chevron-up</v-icon>
    </v-btn>
  </v-fab-transition>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'FloatButton',
})
class FloatButton extends Vue {
  show = false

  onScroll() {
    this.show = window.pageYOffset > 500
  }

  goToTop() {
    this.$vuetify.goTo(60)
  }
}
export default FloatButton
</script>
