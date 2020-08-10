import { Store, ActionTree } from 'vuex'
import CookieParser from 'cookie'
import Cookies from 'js-cookie'
import { initialiseStores } from '~/utils/store-accessor'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const initializer = (store: Store<any>): void => initialiseStores(store)
export const plugins = [initializer]

// eslint-disable-next-line prettier/prettier
export interface RootState { }

export const actions: ActionTree<RootState, RootState> = {
  nuxtServerInit({ dispatch }, { req, $axios }) {
    if (req.headers.cookie) {
      const cookies = CookieParser.parse(req.headers.cookie)
      const accessToken = cookies.access_token
      const refreshToken = cookies.refresh_token
      dispatch('auth/setAccessToken', accessToken)
      dispatch('auth/setRefreshToken', refreshToken)
      $axios.setToken(accessToken, 'Bearer')
    }
  },
  nuxtClientInit({ getters }, _payload) {
    const accessToken = getters['auth/accessToken']
    const refreshToken = getters['auth/refreshToken']
    if (accessToken && refreshToken) {
      Cookies.set('access_token', accessToken)
      Cookies.set('refresh_token', refreshToken)
    } else {
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
    }
  },
}

export * from '~/utils/store-accessor'
