<template>
  <div id="app">
    <div class="tabs">
      <ul>
        <li :class="{'is-active':tabChoice==='email-addresses'}"><a @click="setTab('email-addresses')">Email Addresses</a></li>
        <li :class="{'is-active':tabChoice==='overview'}"><a @click="setTab('overview')">Users</a></li>
        <li :class="{'is-active':tabChoice==='contact-info'}"><a @click="setTab('contact-info')">Visiting Groups</a></li>
        <li :class="{'is-active':tabChoice==='email-lists'}"><a @click="setTab('email-lists')">Email Lists</a></li>

      </ul>
    </div>
    <div class="tile is-ancestor">
      <div class="tile is-parent">
        <div class="tile is-child">
          <me-overview v-if="tabChoice==='overview'"></me-overview>
          <me-contact-info v-if="tabChoice==='contact-info'"></me-contact-info>
          <email-addresses v-if="tabChoice==='email-addresses'"></email-addresses>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import {mapGetters} from 'vuex'

import MeOverview from './components/MeOverview'
import MeContactInfo from './components/MeContactInfo'
import EmailAddresses from './components/EmailAddresses'


export default {
  name: 'app',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App',
      tab: 'email-addresses',
    }
  },
  computed: {
    ...mapGetters('mestore', {
      whatevr: 'whatevr',
    }),
    tabChoice() {
      return this.tab;
    },
  },
  methods: {
    setTab(choice) {
      this.tab = choice;
    },
  },
  components: {
    meOverview: MeOverview,
    meContactInfo: MeContactInfo,
    emailAddresses: EmailAddresses,
  },

}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
