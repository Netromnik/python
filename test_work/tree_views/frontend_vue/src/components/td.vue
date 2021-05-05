<template>
    <div class="col text-center">
        {{ field }}
    </div>
</template>
<script>
export default {
  delimiters: ['[[', ']]'],
  props:
  {
    field: {
      required: false,
      type: Array,
    },
  },

};
</script>
