/* eslint-disable camelcase */
export interface Reminder {
  id: number
  user: string
  content: string
  start_at: string
  created_at: string
  guild: string
  channel: string
}

export interface CalendarDate {
  date: string
  time: string
  year: number
  month: number
  day: number
  hour: number
  minute: number
  weekday: number
  hasDay: boolean
  hasTime: boolean
  past: boolean
  present: boolean
  future: boolean
}
