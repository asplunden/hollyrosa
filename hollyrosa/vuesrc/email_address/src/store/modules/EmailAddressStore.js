import {HTTP} from './../../axios-common.js'
//import {DataAvailable} from './../data-available.js'

import Vue from 'vue'

export const EmailAddressStore = {

  namespaced: true,
  state: {
    whatevr: {},
    twer: false,

    email_addresses: [],
    email_addresses_state: {},


    email_states_list: [[0, 'not set'], [10, 'created'], [20, 'need confirmation'], [30, 'confirmation_sent'], [40, 'confirmed'], [50, 'active'], [-10, 'inactive'], [-100, 'terminated'], [25, 'non-confirmed'] ],
    email_state_name_by_number: {0:'not set', 10: 'created', 20:'need confirmation', 30:'confirmation_sent', 40:'confirmed', 50:'active', '-10':'inactive', '-100':'terminated', 25:'non-confirmed' },
    email_state_modifier_by_number: {0:'is-error', 10: 'is-link', 20:'is-primary', 30:'is-primary', 40:'is-success', 50:'is-success', '-10':'', '-100':'', 25:'is-warning' },
  },
  getters: {
    whatr: state => {return state.whatevr},
    email_addresses: state => { return state.email_addresses },

    email_address_state: state => addrid => { return state.email_addresses_state[addrid]; },
    email_states_list: state => { return state.email_states_list },
    email_state_name: state => state_num => { return state.email_state_name_by_number[state_num]},
    email_state_modifier: state => state_num => { return state.email_state_modifier_by_number[state_num]},
  },
  mutations: {
    setEmailAddress(state, {email_address}) {
      console.log('commit - setEmailAddress', email_address);
      state.email_addresses.push(email_address) // TODO: make reactive
    },
    clearEmailAddressList(state, arg) {
      console.log('commit - clearEmailAddress', arg);
      Vue.set(state, 'email_addresses', []);// TODO: make reactive
    },

    setEmailAddressState(state, {email_address_id, email_address_state}) {
      console.log('commit - setEmailAddressState', email_address_id, email_address_state);
      Vue.set(state.email_addresses_state, email_address_id, email_address_state); // TODO: make reactive
    },
  },
  actions: {
    getEmailAddresses({commit, state, rootState}, arg) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/get_email_addresses';
        HTTP.get(url, {
          params: {
            a:1,
            b:2
          }
        }).then(response => {
          commit('clearEmailAddressList', {email_address: adr});
          console.log(response.data);

          for (var adr of response.data.email_addresses) {
            commit('setEmailAddress', {email_address: adr});
          }


          //...we return the list of emails on resolve, that way the caller can loop and load all states if desired for example
          resolve(response.data.email_addresses);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },

    addEmailAddress({commit, state, rootState}, {email_address}) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/add_email_address';

        let data = new FormData();
        data.append('email_address', email_address);

        HTTP.post(url, data).then(response => {
          console.log(response.data);

          //...if all went well, we should load this email address and updte list of emails

          resolve(true);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },


    getEmailAddressState({commit, state, rootState}, {email_address_id}) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/get_email_address_state';
        HTTP.get(url, {
          params: {
            email_address_id: email_address_id
          }
        }).then(response => {
          console.log('got email address states', response.data);
          if (response.data.found) {
            commit('setEmailAddressState', {email_address_id:email_address_id, email_address_state:response.data.email_address_state});
          }
          //for (var adr of response.data.email_addresses) {
          //  commit('setEmailAddressState', adr);
          //}



          resolve(true);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },

    requestEmailAddressConfirmation({commit, state, rootState}, {email_address, email_address_id}) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/request_email_address_confirmation';

        let data = new FormData();
        data.append('email_address', email_address);

        HTTP.post(url, data).then(response => {
          console.log(response.data);

          //...if all went well, we should load this email address and updte list of emails

          resolve(true);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },

    setEmailAddressState({commit, state, rootState}, {email_address_id, email_address_state}) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/set_email_address_state';

        let data = new FormData();
        data.append('email_address_id', email_address_id);
        data.append('state', email_address_state);

        HTTP.post(url, data).then(response => {
          console.log(response.data);

          //...if all went well, we should load this email address and updte list of emails

          resolve(true);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },

    // TODO: only one set of methods to set state!!!!!
    setGlobalEmailAddressState({commit, state, rootState}, {email_address_id, email_address_global_state}) {
      return new Promise((resolve, reject) => {
        let url = rootState.urlprefix + '/email_address/set_email_address_global_state';

        let data = new FormData();
        data.append('email_address_id', email_address_id);
        data.append('globla_state', email_address_global_state);

        HTTP.post(url, data).then(response => {
          console.log(response.data);

          //...if all went well, we should load this email address and updte list of emails

          resolve(true);
        }, error => {
          console.log(error)
          reject(error)
        })
      })
    },
  },
}
