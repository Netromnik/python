<template>
   <Route v-for="obj in list_data" v-bind='obj'/>
    <div class="anniversary__buttons">
    <div v-on:click='next' class="g-loading-button">
      <span class="g-loading-button__more g-height-60 g-line-height-60 g-font-bold j-showmore" data-type="json" data-target="anniversary-ajax">
      <span  >Показать еще</span>
      </span>
    </div>
    </div>
</template>

<script>
import axios from 'axios';
import Route from './card/card_route.vue';

export default {
  name: 'Dasboard',
  components: { Route },
  props: [
    'url',
  ],
  data() {
    return {
      obj_list: null,
      page: 1,
      page_old: 0,
    };
  },
  computed: {
    list_data() {
      if (this.page != this.page_old) {
        axios.get(`http://127.0.0.1:8000/api/tab/${this.url}/?page=${this.page}`).then(
          (v) => {
            this.obj_list = v.data;
          },
        );
        this.page_old += 1;
      }
      return this.obj_list;
    },
  },
  methods: {
    next() {
      this.page += 1;
    },
  },
};
</script>
