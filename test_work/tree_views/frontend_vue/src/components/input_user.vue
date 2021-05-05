<template>
<fragment>
<b-input-group tag='form'>
    <b-form-input :placeholder="field.username" v-model='myfield.username'  />
    <b-form-input :placeholder="field.email" v-model='myfield.email'  />
    <b-form-input :placeholder="field.phone" v-model='myfield.phone'  />
    <b-form-input  :list="index"  v-model='myfield.work' :placeholder='field.work'>
   </b-form-input>
      <datalist :id="index" v-if="field.select">
        <option v-for="(select,i) in selected"  class="col-4" :key="i">[[ size ]]</option>
      </datalist>
  <slot></slot>
      </b-input-group>
</fragment>
</template>

<script>
export default {
  delimiters: ['[[', ']]'],
  data() {
    return {

      myfield: this.field,
    };
  },
  props: ['field', 'selected', 'index'],

};
</script>
