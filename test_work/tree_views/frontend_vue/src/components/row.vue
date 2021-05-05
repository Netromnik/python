<template>
      <fragment v-if="row.type_obj=='user'">
    <!-- if element is user -->
        <div class="row p-2 " v-if='edit'>
         <b-input-group tag='form'>
            <b-form-input v-model='oldRow.fields.fullname'/>
            <b-form-input v-model='oldRow.fields.email'/>
            <b-form-input v-model='oldRow.fields.phone'/>
            <b-form-input :list='oldRow.pk.split(":").join("_")'
            v-model="oldRow.fields.work"></b-form-input>
            <b-form-datalist :id='oldRow.pk.split(":").join("_")'
            :options="selected"></b-form-datalist>
              <b-input-group-append>
                <b-button  @click="save()">Save</b-button>
                <b-button  @click="cansel()">Cansel</b-button>
              </b-input-group-append>
          </b-input-group>
        </div>
        <div class="row p-2" v-else>
          <b-col>{{row.fields.fullname}}</b-col>
          <b-col>{{row.fields.email}}</b-col>
          <b-col>{{row.fields.phone}}</b-col>
          <b-col>{{row.fields.work}}</b-col>
                    <b-col style="flex-grow:inherit;">
            <b-button-group  size="sm">
            <b-button variant="warning" @click="editRow()">Edit</b-button>
            <b-button variant="info"  @click="deleteRow()">Delete</b-button>
            </b-button-group>
                    </b-col>
        </div>
  </fragment>
  <fragment v-else>
    <!-- if element is strict -->
        <div class="row p-2 " v-if='edit'>
<b-input-group tag='form'>
    <b-form-input :placeholder="row.fields.fullname" v-model='oldRow.fields.name'  />
                <b-button  @click="save()">Save</b-button>
            <b-button  @click="cansel()">Cansel</b-button>
            </b-input-group>
        </div>
        <div class="row p-2" v-else>
                    <b-col>{{row.fields.name}}</b-col>
                    <b-col style="flex-grow:inherit;">
                      <b-button-group size="sm">
                        <b-button variant="success" @click='new_user()'>Add user</b-button>
                        <b-button variant="success" @click='new_struct()'>Add struct</b-button>
                        <b-button variant="warning" @click="editRow()">Edit</b-button>
                        <b-button variant="info" @click="deleteRow()">Delete</b-button>
                      </b-button-group>
                    </b-col>
        </div>
    </fragment>

</template>
<script>

export default {
  data() {
    return {
      oldRow: {},
      edit: false,
    };
  },
  computed: {
    selected: {
      get() {
        return this.$store.state.select;
      },
    },

  },
  props:
  {
    row: {
      required: false,
      type: Object,
    },
  },
  methods: {
    save() {
      this.$store.dispatch('changeNode', this.oldRow);
      this.edit = !this.edit;
      this.$store.state.isEdit = false;
    },
    new_user() {
      this.$store.dispatch('createNode',
        {
          type: 'u',
          username: this.row.pk,
          email: '',
          phone: '',
          parent: this.row.pk,
        });
    },

    new_struct() {
      this.$store.dispatch('createNode',
        {
          type: 's',
          name: this.row.pk,
          parent: this.row.pk,
        });
    },
    cansel() {
      this.edit = !this.edit;
      this.$store.state.isEdit = false;
    },
    editRow() {
      Object.assign(this.oldRow, this.row);
      this.$store.state.isEdit = true;
      this.edit = !this.edit;
    },
    deleteRow() {
      this.$store.dispatch('deleteTree', {
        dalete: true,
        target: this.row.pk,
      });
    },
  },
};
</script>
