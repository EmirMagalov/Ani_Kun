import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import { createWebHistory, createRouter } from 'vue-router'
import Home from './components/Home.vue'
import Seasons from './components/Seasons.vue'
import Episodes from './components/Episodes.vue'
import 'video.js/dist/video-js.css' // Импорт стилей Video.js
import LooksAnime from './components/LooksAnime.vue'
import Room from './components/Room.vue'
import Registration from './components/Registration.vue'
import Login from './components/Login.vue'



const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/seasons/:id', name: 'Seasons', component: Seasons },
  { path: '/episodes/:id', name: 'Episodes', component: Episodes },
  { path: '/looks', name: 'Looks', component: LooksAnime },
  { path: '/room_name/:username/:seasonId', name: 'Room', component: Room },
  { path: '/registration', name: 'Registration', component: Registration },
  { path: '/login', name: 'Login', component: Login },
  

]
const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)

app.use(router)
app.mount('#app')
