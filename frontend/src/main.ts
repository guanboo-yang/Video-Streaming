import { createApp } from 'vue'
import { createRouter } from './routes'
import { createVuetify } from './vuetify'
import App from './App.vue'

const app = createApp(App)
const router = createRouter()
const vuetify = createVuetify()

app.use(router).use(vuetify).mount('#app')
