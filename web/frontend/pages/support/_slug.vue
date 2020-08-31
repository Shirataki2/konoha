<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12" lg="10" xl="8" offset-lg="1" offset-xl="2">
          <h1 class="text-h4">{{ page.title }}</h1>
        </v-col>
      </v-row>
      <v-divider />
      <v-row>
        <v-col cols="12" lg="10" xl="8" offset-lg="1" offset-xl="2">
          <nuxt-content id="support" :document="page" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { Page } from '@/types/konoha'

@Component({
  name: 'Support',
  asyncData: async ({ $content, params, error }) => {
    const slug = params.slug
    if (!slug) error({ statusCode: 404, message: 'Page not Found' })
    const page = await $content('support', slug).fetch()
    return { page }
  },
})
class Support extends Vue {
  page!: Page
}
export default Support
</script>

<style>
#support h2 {
  margin-top: 20px !important;
  margin-bottom: 10px !important;
}

#support li {
  margin: 6px 1px;
}
</style>
