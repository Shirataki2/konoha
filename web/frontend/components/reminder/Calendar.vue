<template>
  <v-card>
    <v-toolbar height="64">
      <v-btn outlined color="secondary" @click="prevMonth">
        <v-icon>mdi-chevron-left</v-icon>
        前月
      </v-btn>
      <v-spacer />
      <v-btn text class="align-end" x-large @click="setToday">
        <span class="text-h3" v-text="year" />
        <span class="text-h3" v-text="month" />
      </v-btn>
      <v-spacer />
      <v-btn outlined color="secondary" @click="nextMonth">
        翌月
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </v-toolbar>
    <v-progress-linear :indeterminate="loading" value="100" color="white" />
    <v-sheet height="700">
      <v-calendar
        ref="calendar"
        v-model="date"
        :events="reminders"
        event-color="red darken-1"
        :event-overlap-threshold="30"
        :day-format="dayFormat"
        :month-format="monthFormat"
        :now="today"
        color="primary"
        @click:date="onDateClicked"
        @click:event="onEventClicked"
        @change="onDateChanged"
      ></v-calendar>
    </v-sheet>
  </v-card>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { Reminder, CalendarDate } from '@/types/konoha'
import dayjs from '@/plugins/dayjs'
import { Random } from 'random-js'
import 'cookie-universal-nuxt'
import '@nuxtjs/axios'

@Component({
  name: 'Calendar',
})
class Calendar extends Vue {
  today = '1970-01-01'
  date = '1970-01-01'
  dayFormat = (date: any) => dayjs(date.date).format('D')
  monthFormat = (date: any) => `${dayjs(date.date).format('M')} / `

  reminders: Array<any> = []

  loading = true

  first = false

  moreDialog = false

  async updateCalendar() {
    this.loading = true
    this.reminders = []
    const [year, month, day] = this.date.split('-')
    try {
      const { data } = await this.$axios.get<Array<Reminder>>(
        '/local_api/month_reminders',
        {
          params: {
            guild_id: this.$route.params.guild,
            year,
            month,
            day,
          },
        }
      )
      this.reminders = data.map((reminder) => ({
        name: reminder.content,
        start: reminder.start_at,
        end: reminder.start_at,
        color: this.randomColor(),
        reminder,
      }))
      this.loading = false
    } catch {}
  }

  async onDateChanged(dates: { start: CalendarDate; end: CalendarDate }) {
    if (dates.start.year === 1970 && !this.first) {
      this.first = true
      return
    }
    if (this.first) {
      this.first = false
      return
    }
    this.loading = true
    this.reminders = []
    try {
      const { data } = await this.$axios.get<Array<Reminder>>(
        '/local_api/month_reminders',
        {
          params: {
            guild_id: this.$route.params.guild,
            year: dates.start.year,
            month: dates.start.month,
          },
        }
      )
      this.reminders = data.map((reminder) => ({
        name: reminder.content,
        start: reminder.start_at,
        end: reminder.start_at,
        color: 'red darken-2',
        reminder,
      }))
    } catch {}
    this.loading = false
  }

  randomColor() {
    const r = new Random()
    const colors = ['red darken-2']
    return colors[r.integer(0, colors.length - 1)]
  }

  onDateClicked(date: CalendarDate) {
    this.$emit('date', date.year, date.month, date.day)
  }

  onEventClicked({ event }: any) {
    this.$emit('event', event.reminder)
  }

  get events() {
    return 1
  }

  get year() {
    return dayjs(this.date).format('YYYY / ')
  }

  get month() {
    return dayjs(this.date).format('M')
  }

  prevMonth() {
    const ref: any = this.$refs.calendar
    ref.prev()
  }

  setToday() {
    this.date = dayjs().format('YYYY-MM-DD')
  }

  nextMonth() {
    const ref: any = this.$refs.calendar
    ref.next()
  }

  mounted() {
    this.today = dayjs().format('YYYY-MM-DD')
    this.date = dayjs().format('YYYY-MM-DD')
  }
}
export default Calendar
</script>
