<template>
    <Big v-bind='obj' v-if="type =='big'" />
    <Afisha v-bind='obj' v-else-if="type =='afisha'"/>
    <Short v-bind='obj' v-else-if="type =='short'" />
</template>

<script>
import Big from './big.vue';
import Afisha from './afisha.vue';
import Short from './short.vue';

export default {
  name: 'Route',
  components: { Big, Afisha, Short },
  props: [
    'type',
    'obj',
  ],
};
</script>
