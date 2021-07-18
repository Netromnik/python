import { createApp } from 'vue';
import { createVuetify } from 'vuetify';
import axios from 'axios';
import VueAxios from 'vue-axios';

import App from './App.vue';

const vuetify = createVuetify();

const app = createApp(App);

app.use(vuetify);
app.use(VueAxios, axios);

app.mount('#app');
