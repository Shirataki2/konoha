<template>
  <v-snackbar
    v-model="snackbar"
    :color="content.color"
    :multi-line="content.multiline"
  >
    <strong>{{ content.content }}</strong>
    <template v-slot:action="{ attrs }">
      <v-btn text v-bind="attrs" @click="() => (snackbar = false)">
        Close
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import NotificationModule from '@/store/notification'

@Component({
  name: 'SnackBar',
})
class SnackBar extends Vue {
  get content() {
    const module = getModule(NotificationModule, this.$store)
    return module.snackbarContent
  }

  get snackbar() {
    const module = getModule(NotificationModule, this.$store)
    return module.snackbar || false
  }

  set snackbar(state: boolean) {
    const module = getModule(NotificationModule, this.$store)
    module.setSnackBar(state)
  }
}
export default SnackBar
</script>
