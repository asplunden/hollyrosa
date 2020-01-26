import Vue from 'vue'
import App from './App.vue'
import store from './store'

import VModal from 'vue-js-modal'
import VeeValidate from 'vee-validate'

Vue.use(VModal)
Vue.use(VeeValidate)

document.addEventListener('DOMContentLoaded', function () {

new Vue({
  el: '#app',
  render: h => h(App),
  directives: {},
  store
})
})

// Debug
Vue.config.devtools = true
