import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import { createWebHistory, createRouter } from 'vue-router'
import Home from './components/Home.vue'
import Seasons from './components/Seasons.vue'
import Episodes from './components/Episodes.vue'
import 'video.js/dist/video-js.css' // Импорт стилей Video.js
import LooksAnime from './components/LooksAnime.vue'
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/seasons/:id', name: 'Seasons', component: Seasons },
  { path: '/episodes/:id', name: 'Episodes', component: Episodes },
  { path: '/looks', name: 'Looks', component: LooksAnime },
]
const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)

app.use(router)
app.mount('#app')
