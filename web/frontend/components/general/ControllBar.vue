<template>
  <v-row class="mt-n3 mb-n2">
    <v-col cols="12" lg="10" xl="8" offset-lg="1" offset-xl="2">
      <v-btn icon large class="mt-n1" to="." nuxt active-class="no-active">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
      <span class="font-weight-black text-h6">{{ title }}</span>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

@Component({
  name: 'ControllBar',
})
class ControllBar extends Vue {
  @Prop({ type: String, default: '' })
  title!: string
}
export default ControllBar
</script>
