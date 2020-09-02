<template>
  <v-card class="mb-2">
    <v-card-title>{{ name }}</v-card-title>
    <v-divider />
    <v-card-subtitle v-if="aliases">
      (エイリアス:
      <code
        v-for="alias in aliases"
        :key="alias"
        style="background: #444; color: #fff;"
        class="pa-1"
        >{{ alias }}</code
      >)
    </v-card-subtitle>
    <v-card-text>
      <v-container class="ma-n4">
        <div class="mt-1 ml-3 mb-4">
          <slot />
        </div>
        <v-row class="mt-n5">
          <v-col cols="12" sm="6">
            <p class="mt-2 text-h6">使用例</p>
            <div v-for="usage in usages" :key="usage" class="ma-3">
              <div
                style="white-space: pre-line; background: #444; padding: 5px;"
              >
                <code
                  style="
                    background: transparent;
                    color: #fff;
                    word-wrap: break-word;
                    padding: 0;
                  "
                  v-text="usage"
                />
              </div>
            </div>
          </v-col>
          <v-col v-if="roles" cols="12" sm="6">
            <p class="mt-2 text-h6">使用可能ユーザ</p>
            <v-chip
              v-for="role in roles"
              :key="role.name"
              :color="role.color"
              dark
              v-text="role.name"
            />
            <p class="mt-3 text-h6">使用回数制限</p>
            <span>{{ rate }}</span>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

@Component({
  name: 'command',
})
class Command extends Vue {
  @Prop({ type: String })
  name!: string

  @Prop({ type: Array })
  roles!: Array<any>

  @Prop({ type: Array })
  aliases!: Array<String>

  @Prop({ type: Array })
  usages!: Array<String>

  @Prop({ type: String, default: '-' })
  rate!: string
}
export default Command
</script>

<style>
pre::before {
  content: '';
}

code {
  background: #222 !important;
  color: #fff !important;
  padding: 4px 0 !important;
  margin: 0 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
}

table th,
table td {
  padding: 10px 0;
  text-align: center;
}

table tr:nth-child(even) {
  background-color: #333;
}
</style>
