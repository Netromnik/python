<template>
    <tabs :class="'anniversary__menu lenta'" v-for="tab_ins in this.tabs" >
        <tab  :class="'anniversary__menu__item lenta'" :name="tab_ins.name">
          <dasb :url="tab_ins.url" />
        </tab>
    </tabs>
</template>
<script>

import { Tabs, Tab } from 'vue3-tabs-component';
import axios from 'axios';

import Dasboard from './components/dasbord.vue';
// import tabs from './components/tabs.vue';

export default {
  name: 'App',
  components: {
    tabs: Tabs,
    tab: Tab,
    dasb: Dasboard,
  },
  data() {
    return {
      tabs: null,
      loading: true,
      errored: false,
    };
  },

  async created() {
    const response = await axios.get('http://127.0.0.1:8000/api/tabs');
    this.tabs = response.data;
  },

};
</script>
