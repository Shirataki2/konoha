import { AxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

export const getTokenFromCookie = (req?: any): string | undefined => {
  // SSR
  if (req && req.headers.cookie) {
    const cookie: string = req.headers.cookie
      .split(';')
      .find((c: string): boolean => c.trim().startsWith('access_token='))

    if (!cookie) {
      return undefined
    }

    const token = cookie.split('=')[1]
    return decodeURIComponent(token)
  }

  return Cookies.get('access_token')
}

export default ({ $axios, req }: any): void => {
  $axios.onRequest((config: AxiosRequestConfig): void => {
    const token = getTokenFromCookie(req)
    // トークンがあればログイン済みなのでリクエストヘッダで送信する
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  })

  $axios.onResponse((response: any): void => {
    const token = response.data

    // CSR のときだけトークンをセットする、 SSR のときは nuxtClientInit でセットしている
    if (!process.client) return
    if (token) {
      if (token.access_token) Cookies.set('access_token', token.access_token)
      if (token.refresh_token) Cookies.set('refresh_token', token.refresh_token)
    }
  })
}
