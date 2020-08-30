<template>
  <v-dialog v-model="dialog" max-width="700px" persistent>
    <v-card>
      <v-card-title v-text="title" />
      <v-card-text>
        <v-form ref="form">
          <v-text-field v-model="name" counter="100" label="要件 *" required />
        </v-form>
        <v-menu
          v-model="dateMenu"
          :close-on-content-click="false"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="startDate"
              label="開催日"
              prepend-icon="mdi-calendar-month"
              readonly
              v-bind="attrs"
              v-on="on"
            />
          </template>
          <v-date-picker
            v-model="startDate"
            color="green lighten-1"
            header-color="primary"
            :day-format="(date) => new Date(date).getDate()"
          >
            <v-btn text color="primary" block @click="dateMenu = false">
              OK
            </v-btn>
          </v-date-picker>
        </v-menu>
        <v-menu
          ref="menu"
          v-model="timeMenu"
          :close-on-content-click="false"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="startTime"
              label="開催時刻"
              prepend-icon="mdi-clock-outline"
              readonly
              v-bind="attrs"
              v-on="on"
            />
          </template>
          <v-time-picker
            v-model="startTime"
            color="green lighten-1"
            header-color="primary"
            format="24hr"
            full-width
          >
            <v-btn text color="primary" block @click="saveTime">OK</v-btn>
          </v-time-picker>
        </v-menu>
        <v-btn
          block
          outlined
          color="primary"
          :loading="loading"
          :disabled="deleteLoading"
          @click="submit"
        >
          <strong>保存</strong>
        </v-btn>
        <v-btn
          v-if="index >= 0"
          block
          outlined
          color="error"
          class="mt-4"
          :loading="deleteLoading"
          :disabled="loading"
          @click="remove"
        >
          <strong>削除</strong>
        </v-btn>
        <v-btn
          block
          outlined
          color="error"
          class="mt-4"
          :disabled="loading || deleteLoading"
          @click="cancel"
        >
          <strong>キャンセル</strong>
        </v-btn>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from 'vue-property-decorator'
import dayjs from '@/plugins/dayjs'
import { getModule } from 'vuex-module-decorators'
import NotificationModule from '@/store/notification'
import { Reminder } from '~/types/konoha'
import { GuildDetail } from '~/types/discord'

@Component({
  name: 'Dialog',
})
class Dialog extends Vue {
  @Prop({ type: Boolean, default: false })
  value!: boolean

  @Prop({ type: String, default: '' })
  title!: string

  @Prop({ type: Array, required: true })
  reminders!: Array<Reminder>

  @Prop({ type: Object, default: () => ({}) })
  guild!: GuildDetail

  @Prop({ type: Number, default: -1 })
  index!: number

  @Prop()
  reminder!: Reminder | null

  @Prop({ type: String, default: '' })
  date!: string

  name: string = ''

  loading = false
  deleteLoading = false

  dateMenu = false
  timeMenu = false
  startDate = ''
  startTime = '17:00'

  @Watch('value')
  watchDialog() {
    if (this.value) {
      if (this.reminder) {
        this.name = this.reminder.content
        const d = dayjs(this.reminder.start_at)
        this.startDate = d.format('YYYY-MM-DD')
        this.startTime = d.format('HH:mm')
      } else if (this.index >= 0) {
        this.name = this.reminders[this.index].content
        const d = dayjs(this.reminders[this.index].start_at)
        this.startDate = d.format('YYYY-MM-DD')
        this.startTime = d.format('HH:mm')
      } else {
        if (this.date === '') {
          this.startDate = dayjs().format('YYYY-MM-DD')
        } else {
          this.startDate = dayjs(this.date).format('YYYY-MM-DD')
        }
        this.startTime = '17:00'
        this.name = ''
      }
    }
  }

  saveTime() {
    const menu: any = this.$refs.menu
    menu.save(this.startTime)
  }

  get dialog() {
    return this.value
  }

  set dialog(state: boolean) {
    this.$emit('input', state)
  }

  async submit() {
    this.loading = true
    const module = getModule(NotificationModule, this.$store)
    try {
      if (this.index < 0) {
        await this.$axios.post(
          '/local_api/reminders',
          {
            content: this.name,
            start_at: `${this.startDate} ${this.startTime}`,
          },
          {
            params: {
              guild_id: this.guild.id,
            },
          }
        )
      } else {
        const id = this.reminder
          ? this.reminder.id
          : this.reminders[this.index].id
        await this.$axios.patch(
          '/local_api/reminders',
          {
            content: this.name,
            start_at: `${this.startDate} ${this.startTime}`,
          },
          {
            params: {
              guild_id: this.guild.id,
              reminder_id: id,
            },
          }
        )
      }
      module.setSnackBarContent({
        content: '投稿が完了しました',
        color: 'success',
      })
      module.fireSnackBar()
      this.dialog = false
      this.$emit('update')
    } catch {
      module.setSnackBarContent({
        content: '申し訳ありませんが投稿に失敗しました',
        color: 'error',
      })
      module.fireSnackBar()
    }
    this.loading = false
  }

  cancel() {
    this.dialog = false
  }

  async remove() {
    const id = this.reminder ? this.reminder.id : this.reminders[this.index].id
    const module = getModule(NotificationModule, this.$store)
    this.deleteLoading = true
    if (confirm('このリマインダーを削除しますか？')) {
      try {
        await this.$axios.delete('/local_api/reminders', {
          params: {
            guild_id: this.guild?.id,
            reminder_id: id,
          },
        })
        module.setSnackBarContent({
          content: '正常に削除しました',
          color: 'success',
        })
        this.dialog = false
        await this.$emit('update')
      } catch {
        module.setSnackBarContent({
          content: '申し訳ありませんが削除に失敗しました',
          color: 'error',
        })
      }
      module.fireSnackBar()
    }
    this.deleteLoading = false
  }
}
export default Dialog
</script>
