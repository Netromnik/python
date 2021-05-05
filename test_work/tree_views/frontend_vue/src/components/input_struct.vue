<template>
<fragment>
<b-input-group tag='form'>
    <b-form-input :placeholder="field.username" v-model='myfield.label'  />
  <slot></slot>
            </b-input-group>
</fragment>
</template>

<script>
export default {
  delimiters: ['[[', ']]'],
  data() {
    const index = Math.random();
    return { index, myfield: this.fields };
  },
  props:
  {
    fields: {
      required: false,
      type: Object,
    },
  },

};
</script>
