<template>
  <div>

      <view-email-address-properties-dialog
        :emailAddressStateDetails="emailAddressStateDetails"
        :doShow="showViewEmailAddressPropertiesDialog"
        @close="showViewEmailAddressPropertiesDialog=false"
        >
      </view-email-address-properties-dialog>

      <add-email-address-dialog
        ref="AddEmailAddressDialog"
        @save="saveNewEmailAddress($event.email_address)"
        >
      </add-email-address-dialog>




    <div class="container">

      1. Finalize data-state so we can use info on if data is available or not.<br/>
      2. In user admin, some way to assign email addresses to users.<br/><br/>
      3. List email address reports.
      A1. In ME, some way to add an email to ones accout. Maybe thats next feature branch that also includes password reset... <br/><br/>

      <nav class="level box">
        <!-- Left side -->
        <div class="level-left">
          <div class="level-item">
            <p class="subtitle is-5">
              <strong>{{ email_addresses.length }}</strong> addresses
            </p>
          </div>
          <div class="level-item">
            <div class="field has-addons">
              <p class="control">
                <input class="input" type="text" placeholder="Find a post">
              </p>
              <p class="control">
                <button class="button">
                  Search
                </button>
              </p>
            </div>
          </div>
        </div>

        <!-- Right side -->
        <div class="level-right">
          <p class="level-item"><a class="button" @click="addEmailAddressDialog()">Add Email Address</a></p>
          <p class="level-item"><a class="button is-link" @click="loadAddresses()">Re-Load Addresses</a></p>
          <state-change-dropdown
            :email_address_id="''"
            :email_address_state="showOnlyState"
            :state_list="email_states_list"
            @stateChoice="changeShowOnlyState( $event )"
            >Show Only State</state-change-dropdown>
        </div>
      </nav>


      <div class="content">
        <table class="table">
          <tbody>
            <tr v-for="email_address in email_address_filtered_by_state">
              <td>{{ email_address.email_address }}<br/><span v-if="email_address_state(email_address._id)" class="tag" :class="email_state_modifier(email_address_state(email_address._id)['state'])">{{ email_state_name(email_address_state(email_address._id)['state']) }}</span></td>
              <td>
                <!-- <a class="button is-small" @click="loadEmailAddressState(email_address._id)">Load State</a> -->
                <a class="button is-small is-link is-outlined" @click="requestEmailAddressConfirmation(email_address.email_address, email_address._id)">Request Confirmation</a>
                <a class="button is-small is-link is-outlined" @click="showEmailAddressDetails(email_address._id)">Show Details</a>

                <state-change-dropdown
                  :email_address_id="email_address._id"
                  :email_address_state="getStateValueOfEmailAddressState(email_address._id)"
                  :state_list="email_states_list"
                  :isSmall="true"
                  @stateChoice="changeEmailAddressState( $event )"
                >Set State</state-change-dropdown>


              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </article>

  </div>
</template>

<script>
import Vue from 'vue'
import {mapGetters} from 'vuex'
import AddEmailAddressDialog from './email_address/AddEmailAddressDialog'
import ViewEmailAddressPropertiesDialog from './email_address/ViewEmailAddressPropertiesDialog'
import StateChangeDropdown from './bulma/StateChangeDropdown'

export default {
  name: 'me-email-addresses',
  data () {
    return {
      modalIsActive: false,
      emailAddressStateDetails: {},
      showViewEmailAddressPropertiesDialog: false,
      showOnlyState: 0,
    }
  },
  computed: {
    ...mapGetters('EmailAddressStore', {
      whatevr: 'whatevr',
      email_addresses: 'email_addresses',
      email_address_state: 'email_address_state',
      email_states_list: 'email_states_list',
      email_state_name: 'email_state_name',
      email_state_modifier: 'email_state_modifier',
    }),
    email_address_filtered_by_state() {
      return this.email_addresses.filter(obj => {return this.getStateValueOfEmailAddressState(obj._id) == this.showOnlyState || this.showOnlyState == 0 })
    },
  },
  methods: {
    loadAddresses() {
      console.log('loadAddresses handler');
      this.$store.dispatch('EmailAddressStore/getEmailAddresses').then(email_address_list => {
        console.log('got response', email_address_list);
        for (var adr of email_address_list) {
          console.log('trying to load state', adr);
          this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:adr._id});
        }
      });
    },
    loadEmailAddressState(email_address_id) {
      console.log('loadEmailAddressState handler');
      this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:email_address_id});
    },
    addEmailAddressDialog() {
      this.$refs.AddEmailAddressDialog.show()
    },
    saveNewEmailAddress(email_address) {
      console.log('NEW EMAIL', email_address)

      // TODO validation using vee-validate
      this.$store.dispatch('EmailAddressStore/addEmailAddress', {email_address: email_address}).then(response => {
        this.$store.dispatch('EmailAddressStore/getEmailAddresses');
      });
    },


    requestEmailAddressConfirmation(email_address, email_address_id) {
      this.$store.dispatch('EmailAddressStore/requestEmailAddressConfirmation', {email_address:email_address, email_address_id:email_address_id}).then(response => {
        this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:email_address_id});
      });
    },


    changeEmailAddressState({email_address_id, email_address_state}) {
      this.$store.dispatch('EmailAddressStore/setEmailAddressState', {email_address_id: email_address_id, email_address_state:email_address_state}).then(response => {
        this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:email_address_id});
      });
    },
    changeEmailAddressGlobalState({email_address_id, email_address_state}) {
      this.$store.dispatch('EmailAddressStore/setEmailAddressGlobalState', {email_address_id: email_address_id, email_address_state:email_address_state}).then(response => {
        this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:email_address_id});
      });
    },



    showEmailAddressDetails(email_address_id) {
      this.$store.dispatch('EmailAddressStore/getEmailAddressState', {email_address_id:email_address_id}).then(response => {
        Vue.set(this, 'emailAddressStateDetails', this.email_address_state(email_address_id));
        Vue.set(this, 'showViewEmailAddressPropertiesDialog', true); // have a show property instead
      });

    },


    isStatesTheSame(email_address_id, email_address_state) {
      if (this.email_address_state(email_address_id)) {
        return email_address_state == this.email_address_state(email_address_id)['state']
      }  else {
        return 0;
      }

    },

    getStateValueOfEmailAddressState(email_address_id) {
      if (this.email_address_state(email_address_id)) {
        return this.email_address_state(email_address_id)['state']
      } else {
        return 0;
      }

    },

    changeShowOnlyState( {email_address_id, email_address_state} ) {
      this.showOnlyState = email_address_state;
    },
  },
  components: {
    addEmailAddressDialog: AddEmailAddressDialog,
    viewEmailAddressPropertiesDialog: ViewEmailAddressPropertiesDialog,
    stateChangeDropdown: StateChangeDropdown,
  },
  mounted() {
    this.loadAddresses();
  },


}
</script>
