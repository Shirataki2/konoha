<template>
  <v-card>
    <v-card-text>
      <v-form ref="settings">
        <div v-for="field in fields" :key="field.name">
          <span
            v-if="!field.permission()"
            class="caption"
            v-text="field.alert"
          />
          <v-text-field
            v-model="field.value"
            :counter="field.limit"
            :label="field.name"
            :hint="field.description"
            :rules="field.rules"
            :required="field.required"
            :disabled="!field.permission()"
            @input="onFieldChanged"
          />
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { GuildDetail, Member } from '@/types/discord'
import 'cookie-universal-nuxt'
import '@nuxtjs/axios'

@Component({
  name: 'Settings',
})
class Settings extends Vue {
  @Prop({ type: Object, default: () => {} })
  guild!: GuildDetail

  @Prop({ type: Object, default: () => {} })
  user!: Member

  fields = [
    {
      name: '接頭文字 *',
      description:
        'Botを呼び出す際に使用する文字です．例えば">"と設定した場合">help"のように呼び出します',
      alert:
        '※ 変更するにはサーバーのオーナーであるか，管理者，サーバ管理権限のいずれかの権限を持っている必要があります',
      value: '',
      valuePrev: '',
      permission: () => {
        const p = this.guild.user.permissions
        return p && (p.owner || p.administrator || p.manage_roles)
      },
      limit: 8,
      required: true,
      rules: [
        (v: string) => !!v || '必須項目です',
        (v: string) => v.length <= 8 || '8文字以下である必要があります',
      ],
      apiEndpoint: '/local_api/prefix',
      method: 'PATCH',
      param: 'prefix',
    },
  ]

  fieldPrev = ''

  async mounted() {
    const prefix = await this.$axios.get('/local_api/prefix', {
      params: {
        guild_id: this.guild.id,
      },
    })
    this.fields = this.fields.map((field) => {
      if (field.name === '接頭文字 *') {
        return { ...field, value: prefix.data, valuePrev: prefix.data }
      } else {
        return field
      }
    })
    this.fieldPrev = JSON.stringify(this.fields)
  }

  onFieldChanged() {
    this.$emit('dirty', this.fieldPrev !== JSON.stringify(this.fields))
  }

  validate() {
    const form: any = this.$refs.settings
    return form.validate()
  }

  async save() {
    await this.fields.forEach(async (field) => {
      if (field.value !== field.valuePrev) {
        if (field.method === 'PATCH') {
          const param = field.param
          await this.$axios.patch(
            field.apiEndpoint,
            {},
            {
              params: {
                guild_id: this.guild.id,
                [param]: field.value,
              },
            }
          )
        }
      }
    })
  }

  reset() {
    const fields = JSON.parse(this.fieldPrev)
    fields.forEach((field: any) => {
      this.fields[
        this.fields.findIndex((_field) => _field.name === field.name)
      ].value = field.value
    })
  }
}
export default Settings
</script>
