import Fragment from 'vue-fragment';
import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import Vuex from 'vuex';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';

const axios = require('axios').default;

Vue.prototype.axios = axios;
Vue.use(Fragment.Plugin);

Vue.use(BootstrapVue);

Vue.config.productionTip = false;
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    elements: [],
    alert: [],
    isEdit: false,
    select: [],
  },
  mutations: {
    UPDATE(state, pipline) {
      while (state.elements.length > 0) {
        state.elements.pop();
      }
      state.elements = pipline.slice(0);
    },
    ALERT(state) {
      state.alert.push({ showDismissibleAlert: true });
    },
    SELECT_UPDATE(state, pipline) {
      while (state.select.length > 0) {
        state.select.pop();
      }
      state.select = pipline.slice(0);
    },
  },
  actions: {
    longPulling: (context) => {
      if (!context.state.isEdit) {
        axios
          .get('/api/v1/tree')
          .then((response) => { context.commit('UPDATE', response.data); });
        axios
          .get('/api/v1/select')
          .then((response) => { context.commit('SELECT_UPDATE', response.data); });
      }
    },
    moveTree: (context, pipeline) => {
      axios.post('/api/v1/tree', pipeline).then(
        (request) => { if (request.data !== '301') { context.commit('ALERT'); } },
      );
    },
    deleteTree: (context, pipeline) => {
      axios.post('/api/v1/tree', pipeline).then(
        (request) => { if (request.data !== '301') { context.commit('ALERT'); } },
      );
    },

    createNode: (context, pipeline) => {
      axios.put('/api/v1/tree', pipeline).then(
        (request) => { if (request.data !== '201') { context.commit('ALERT'); } },
      );
    },
    changeNode: (context, pipeline) => {
      axios.patch('/api/v1/tree', pipeline).then(
        (request) => { if (request.data !== '201') { context.commit('ALERT'); } },
      );
    },
  },
});

new Vue({
  store,
  render: (h) => h(App),
  mounted() {
    // this.$store.dispatch('longPulling');
    setInterval(() => { this.$store.dispatch('longPulling'); }, 1000);
  },
}).$mount('#app');
