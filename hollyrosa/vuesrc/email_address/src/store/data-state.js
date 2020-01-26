import Vue from 'vue'

export const DataState = {
  nextState(current, next) {
    return next;
  },
  setNext(a, k, next) {
    if (next === this.States.RELOADING) {
      if (k in a) {
        Vue.set(a,k, this.nextState(a[k], next));
      } else {
        Vue.set(a, k, this.States.Empty);
      }
    } else {
      Vue.set(a, k, this.nextState(a[k], next));
    }
  },

  States = {
    INIT:0, CREATED:5, FAILED:-10, INIT_REQ:10, READY:30, RELOADING:40, UPDATING:50, PENDING_DELETE:101, DELETED:102,
  }
}
