<template>
<div class="container">
  <h1> Test nested set  </h1>
    <template     v-for="(alert,index)  in this.$store.state.alert" >
          <b-alert v-model="alert.showDismissibleAlert" variant="danger" :key = 'index' dismissible>
              Dismissible Alert!
        </b-alert>
    </template>
      <b-card no-body>
    <b-tabs pills card vertical>
      <b-tab title="Tab 1" active><b-card-text>
    <div class="row m-2 d-flex" >
            <b-button @click="add_struct">add struct</b-button>
    </div>
    <nested :elems='this.$store.state.elements' />
        </b-card-text></b-tab>
      <b-tab title="Tab 2"><b-card-text>Tab contents 2</b-card-text></b-tab>
      <b-tab title="Tab 3"><b-card-text>Tab contents 3</b-card-text></b-tab>

        </b-tabs>
  </b-card>

</div>
</template>

<script>
import nested from './components/nested.vue';

export default {
  name: 'App',
  delimiters: ['[[', ']]'],
  components: {
    nested,
  },
  methods: {
    add_struct() {
      this.$store.dispatch('createNode',
        {
          type: 's',
          name: 'root',
        });
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
