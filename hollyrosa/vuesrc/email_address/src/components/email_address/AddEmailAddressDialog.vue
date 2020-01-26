<template>
  <!-- modal for add email address -->
  <div class="modal" :class="{'is-active': modalIsActive}">
    <div class="modal-background">
    </div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Add Email Address</p>
        <button class="delete" aria-label="close" @click="cancelNewEmailAddress()"></button>
      </header>
      <section class="modal-card-body">
        <div class="field">
          <div class="control" @keyup.enter="saveNewEmailAddress()">
            <input class="input" type="email" placeholder="Email Address" v-bind:value="newEmailAddress" />
          </div>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-primary" @click="saveNewEmailAddress()">Save changes</button>
        <button class="button" @click="cancelNewEmailAddress()">Cancel</button>
      </footer>
    </div>
  </div>
</template>
<script>
import Vue from 'vue'

export default {
  name: 'add-email-address-dialog',
  data () {
    return {
      modalIsActive: false,
      newEmailAddress: 'a@b.c',
    }
  },
  props: {

  },
  computed: {
  },
  methods: {
    show () {
      this.modalIsActive = true;
    },
    hide () {
      this.modalIsActive = false;
    },
    saveNewEmailAddress() {
      this.hide();
      this.$emit('save', this.newEmailAddress);
    },
    cancelNewEmailAddress() {
      this.hide();
      this.$emit('cancel', '');
    },
  },
  components: {

  },
  mounted() {

  },


}
</script>
