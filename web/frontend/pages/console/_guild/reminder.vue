<template>
  <div>
    <v-container>
      <ControllBar title="リマインダー" />
      <v-row v-if="!err">
        <v-col cols="12" lg="10" xl="8" offset-lg="1" offset-xl="2">
          <div class="text-right mt-1 mb-6">
            <v-btn color="primary" large @click="newReminder">新規作成</v-btn>
          </div>
          <Calendar ref="calendar" @date="onDateClick" @event="onEventClick" />
          <v-data-table
            :headers="headers"
            :items="customReminders"
            :options.sync="options"
            :server-items-length="total"
            :loading="loading"
            :footer-props="{
              'items-per-page-options': [5, 10, 25, 50, 100],
            }"
          >
            <template #top>
              <v-card flat>
                <v-card-title>
                  <v-checkbox
                    v-model="options.filter"
                    label="過去のイベントを表示する"
                  />
                </v-card-title>
              </v-card>
            </template>
            <template #item.actions="{ item }">
              <v-icon color="primary" class="mr-2" @click="editReminder(item)">
                mdi-pencil
              </v-icon>
              <v-icon color="error" class="mr-2" @click="deleteReminder(item)">
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
          <Dialog
            v-model="dialog"
            :reminder="reminder"
            :date="date"
            :guild="guild"
            :reminders="reminders"
            :title="index < 0 ? '新規作成' : '編集'"
            :index="index"
            @update="onOptionUpdate"
          />
        </v-col>
      </v-row>
      <div v-else>
        <p>リマインダーの初期設定が完了していないようです．</p>
        <p>
          通知を届けたいチャンネルで
          <code>
            >reminder init
          </code>
          のように初期化処理を行ってください
        </p>
        <p>
          初期化はサーバーのオーナーか管理者またはサーバー管理者のロールを持っているユーザが実行できます
        </p>
      </div>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Watch } from 'vue-property-decorator'
import { GuildDetail } from '@/types/discord'
import ControllBar from '@/components/general/ControllBar.vue'
import Dialog from '@/components/reminder/Dialog.vue'
import Calendar from '@/components/reminder/Calendar.vue'
import dayjs from '@/plugins/dayjs'
import { getModule } from 'vuex-module-decorators'
import NotificationModule from '@/store/notification'
import 'cookie-universal-nuxt'
import '@nuxtjs/axios'
import { Reminder } from '~/types/konoha'

@Component({
  name: 'Reminder',
  components: {
    ControllBar,
    Dialog,
    Calendar,
  },
  asyncData: async ({ redirect, store, app, $axios }) => {
    if (store.getters['auth/accessToken'] && store.getters['auth/user']) {
      return { userdata: store.getters['auth/user'] }
    } else if (app.$cookies.get('access_token')) {
      store.dispatch('auth/setAccessToken', app.$cookies.get('access_token'))
      store.dispatch('auth/setRefreshToken', app.$cookies.get('refresh_token'))
      try {
        const { data } = await $axios.get('/api/users/@me')
        store.dispatch('auth/setUser', data)
        return { userdata: data }
      } catch {
        redirect(301, '/')
      }
    } else {
      redirect(301, '/')
    }
  },
})
class Index extends Vue {
  guild: GuildDetail | null = null
  reminders: Array<Reminder> = []
  dateFormat = 'YYYY/MM/DD HH:mm'
  date = ''

  dialog = false
  index = -1
  reminder: Reminder | null = null

  options = {
    page: 1,
    itemsPerPage: 3,
    sortBy: ['start'],
    sortDesc: [false],
    filter: false,
  }

  loading = true
  total = 0

  err = false

  @Watch('options', { deep: true })
  async onOptionUpdate() {
    this.loading = true
    if (this.err) return
    try {
      const { data } = await this.$axios.get('/local_api/reminders', {
        params: {
          guild_id: this.$route.params.guild,
          type: this.options.filter ? 'all' : 'future',
          offset: this.options.itemsPerPage * (this.options.page - 1),
          limit: this.options.itemsPerPage,
          sort_by: this.options.sortBy[0],
          descending: this.options.sortDesc[0],
        },
      })
      const ref: any = this.$refs.calendar
      ref.updateCalendar()
      this.reminders = data.reminders
      this.total = data.count
      this.loading = false
    } catch {
      this.err = true
    }
  }

  headers = [
    {
      text: '要件',
      value: 'content',
      width: '50%',
      align: 'left',
      sortable: false,
    },
    {
      text: '開始日時',
      value: 'start',
      align: 'center',
    },
    {
      text: '作成日時',
      value: 'created',
      align: 'center',
    },
    {
      text: '編集',
      value: 'actions',
      align: 'center',
      sortable: false,
    },
  ]

  onDateClick(year: number, month: number, day: number) {
    this.reminder = null
    this.date = `${year}-${month}-${day}`
    this.index = -1
    this.$nextTick(() => {
      this.dialog = true
    })
  }

  onEventClick(reminder: Reminder) {
    this.reminder = reminder
    this.index = 9999
    this.date = ''
    this.$nextTick(() => {
      this.dialog = true
    })
  }

  get customReminders() {
    return this.reminders.map((reminder) => {
      const start = dayjs(reminder.start_at).format(this.dateFormat)
      const created = dayjs(reminder.created_at).format(this.dateFormat)
      return { ...reminder, start, created }
    })
  }

  async mounted() {
    if (this.$route.params.guild) {
      const { data } = await this.$axios.get('/local_api/guild', {
        params: {
          guild_id: this.$route.params.guild,
        },
      })
      this.guild = data
    }
  }

  newReminder() {
    this.reminder = null
    this.index = -1
    this.date = ''
    this.$nextTick(() => {
      this.dialog = true
    })
  }

  editReminder(reminder: Reminder) {
    this.reminder = null
    this.index = this.reminders.findIndex((r) => r.id === reminder.id)
    this.date = ''
    this.$nextTick(() => {
      this.dialog = true
    })
  }

  async deleteReminder(reminder: Reminder) {
    const module = getModule(NotificationModule, this.$store)
    if (confirm('このリマインダーを削除しますか？')) {
      try {
        await this.$axios.delete('/local_api/reminder', {
          params: {
            guild_id: this.guild?.id,
            reminder_id: reminder.id,
          },
        })
        module.setSnackBarContent({
          content: '正常に削除しました',
          color: 'success',
        })
        await this.onOptionUpdate()
      } catch {
        module.setSnackBarContent({
          content: '申し訳ありませんが削除に失敗しました',
          color: 'error',
        })
      }
      module.fireSnackBar()
    }
  }
}
export default Index
</script>
