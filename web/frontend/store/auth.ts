import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import Cookies from 'js-cookie'

@Module({
  name: 'auth',
  stateFactory: true,
  namespaced: true,
})
export default class AuthModule extends VuexModule {
  private _accessToken: string = ''
  private _refreshToken: string = ''
  private _user: any = null

  public get accessToken() {
    return this._accessToken
  }

  public get refreshToken() {
    return this._refreshToken
  }

  public get user() {
    return this._user
  }

  @Mutation
  private SET_ACCESS_TOKEN(token: string) {
    this._accessToken = token
  }

  @Mutation
  private SET_REFRESH_TOKEN(token: string) {
    this._refreshToken = token
  }

  @Mutation
  private SET_USER(user: any) {
    this._user = user
  }

  @Action
  public setAccessToken(token: string) {
    this.SET_ACCESS_TOKEN(token)
    Cookies.set('access_token', token)
  }

  @Action
  public setRefreshToken(token: string) {
    this.SET_REFRESH_TOKEN(token)
    Cookies.set('refresh_token', token)
  }

  @Action
  public setUser(userdata: any) {
    this.SET_USER(userdata)
  }
}
