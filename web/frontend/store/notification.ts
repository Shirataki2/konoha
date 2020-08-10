import { Module, VuexModule, Mutation } from 'vuex-module-decorators'

export interface SnackBar {
  enable?: boolean
  content: string
  color: string
  multiline?: boolean
}

@Module({
  name: 'notification',
  stateFactory: true,
  namespaced: true,
})
export default class NotificationModule extends VuexModule {
  private _snackbar: SnackBar = {
    enable: false,
    content: '',
    color: 'error',
    multiline: false,
  }

  public get snackbar() {
    return this._snackbar.enable
  }

  public get snackbarContent() {
    return this._snackbar
  }

  @Mutation
  public setSnackBarContent({ content, color, multiline }: SnackBar) {
    this._snackbar.content = content
    this._snackbar.color = color
    this._snackbar.multiline = multiline
  }

  @Mutation
  public setSnackBar(state: boolean) {
    this._snackbar.enable = state
  }

  @Mutation
  public fireSnackBar() {
    this._snackbar.enable = true
  }
}
