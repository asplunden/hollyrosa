import Vue from 'vue'
import Vuex from 'vuex'

import {EmailAddressStore} from './modules/EmailAddressStore'

Vue.use(Vuex)


export default new Vuex.Store({
  state: {
    urlprefix: 'http://localhost:8090'
  },
  modules: {
    EmailAddressStore,
  },
})
