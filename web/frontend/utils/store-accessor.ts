import { Store } from 'vuex'
import { getModule } from 'vuex-module-decorators'
import AuthModule from '~/store/auth'

// eslint-disable-next-line import/no-mutable-exports
let auth: AuthModule

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function initialiseStores(store: Store<any>): void {
  auth = getModule(AuthModule, store)
}

export { initialiseStores, auth }
