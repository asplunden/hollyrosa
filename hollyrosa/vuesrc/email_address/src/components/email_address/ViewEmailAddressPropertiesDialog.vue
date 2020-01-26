<template>
  <!-- end modal for add email address -->
  <div class="modal" :class="{'is-active': doShow }" v-if="doShow" >
    <div class="modal-background" @click="close()">
    </div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Email Address Details</p>
        <button class="delete" aria-label="close" @click="close()"></button>
      </header>
      <section class="modal-card-body" >
        <h2 class="title">Email Address Info</h2>
        <table class="table">
          <tbody>
            <tr>
              <td>id</td><td>{{ emailAddressStateDetails['email_address_id'] }}</td>
            </tr>
            <tr>
              <td>state</td><td><span class="tag is-info">{{ emailAddressStateDetails['state'] }}</span></td>
            </tr>
            <tr>
              <td>timestamp</td><td>{{ emailAddressStateDetails['timestamp'] }}</td>
            </tr>
            <tr>
            </tr>
            <tr v-for="(value, attr) in emailAddressStateDetails['email_address']">
              <td v-if="! (attr in {'_rev':0, 'type':0, 'subtype':0})">{{ attr }}</td>
              <td v-if="! (attr in {'_rev':0, 'type':0, 'subtype':0})">{{ value }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
  <!-- modal for show email address details -->
</template>

<script>
import Vue from 'vue'

export default {
  name: 'view-email-address-properties-dialog',
  props: {
    emailAddressStateDetails: {required: true, type:Object},
    doShow: {type:Boolean},
  },
  computed: {
  },
  methods: {
    close() {
      this.$emit('close', {});
    }
  },
}
</script>
