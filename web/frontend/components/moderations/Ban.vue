<template>
  <v-card>
    <v-card-title>ユーザのBAN</v-card-title>
    <v-card-text>
      <v-form ref="form">
        <v-textarea
          v-model="reason"
          :counter="512"
          label="理由"
          :rules="[(v) => v.length <= 512 || '512文字を超過しています']"
        />
        <v-select
          v-model="selected"
          :items="deleteMessageSelection"
          label="メッセージの削除"
        />
        <div class="mt-7 mb-7" />
        <v-btn color="error" outlined block large @click="submit">
          BANする
        </v-btn>
        <div class="mt-7 mb-7" />
        <v-btn color="primary" outlined block large @click="cancel">
          キャンセル
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

@Component({
  name: 'Ban',
})
class Ban extends Vue {
  reason = ''
  selected = '24時間分'

  deleteMessageSelection: ['削除しない', '24時間分', '7日間分'] = [
    '削除しない',
    '24時間分',
    '7日間分',
  ]

  async submit() {}

  cancel() {
    this.$emit('cancel')
  }
}
export default Ban
</script>
