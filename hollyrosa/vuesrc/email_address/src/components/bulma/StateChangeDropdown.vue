<template>
  <div class="dropdown is-hoverable" :class="{ 'is-active':false}">
    <div class="dropdown-trigger">
      <button class="button" :class="{'is-small': isSmall}" aria-haspopup="true" aria-controls="dropdown-menu">
        <span><slot>Change State</slot></span>
        <span class="icon is-small">
          <i class="fas fa-angle-down" aria-hidden="true"></i>
        </span>
      </button>
    </div>
    <div class="dropdown-menu" role="menu">
      <div class="dropdown-content">
        <a :class="{'is-active': isStatesTheSame(state_choice[0]), 'dropdown-item':true}" v-for="state_choice in state_list" @click="stateChoice(email_address_id, state_choice[0])">
          {{ state_choice[1] }}
        </a>
      </div>
    </div>
  </div>
</template>
<script>
import Vue from 'vue'

export default {
  name: 'state-change-dropdown',
  props: {
    email_address_state: {required: false, default: 0},
    state_list: {required: true, type: Array},
    email_address_id: {required: true, type: String},
    isSmall: {required: false, default: false},
  },
  computed: {
  },
  methods: {
    isStatesTheSame(state_choice) {
      if (this.email_address_state != 0) {
        return (state_choice==this.email_address_state)
      } else {
        return 0;
      }
    },
    stateChoice(email_address_id, state_choice) {
      this.$emit('stateChoice', {email_address_id:email_address_id, email_address_state:state_choice});
    }
  },
}
</script>
