<template>

</template>

<script>


export default {
  props:{
    tabs
  }
  components: {
    tabs: Tabs,
    tab: Tab,
  },
  data() {
    return {
      tab: null,
      items: [
        'Appetizers', 'Entrees', 'Deserts', 'Cocktails',
      ],
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    };
  },
};
</script>
