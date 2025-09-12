<script setup>
import Video from './components/Video.vue'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import { provide, ref, computed, onMounted, watch, inject } from 'vue'
import { useRoute } from 'vue-router'
import Scroll from './components/Scroll.vue'
import { API_BASE_URL } from '@/config'
import axios from 'axios'
const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0

const userLoaded = ref(false)
const userData = ref(null)
const userAunth = ref(false)
provide('userData', userData)
provide('userAunth', userAunth)
provide('userLoaded', userLoaded)
provide('isTouchDevice', isTouchDevice)
onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const { data } = await axios.get(`${API_BASE_URL}/auth/users/me`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })

    userData.value = data
    console.log(userData.value)
    userAunth.value = true
  } catch (err) {
    console.error('Ошибка:', err)
  } finally {
    userLoaded.value = true // данные загружены, независимо от результата
  }
})

const route = useRoute()
const mgSharingan = ref(false)
const hovered = ref(false)
const scrollState = ref(false)
const scrollMenu = ref(false)
const kunaiImg = ref('/kunai.png')

const kunai_show = ref(false)
let normalSrc = '/ANIKUN-1.png'
let hoverSrc = '/ANIKUN-2.png'
let timerId = null
const scrollY = ref(0)
const audio = new Audio('/sharingan.mp3')
const iconVolume = ref(JSON.parse(localStorage.getItem('iconVolume') || 'true'))

provide('iconVolume', iconVolume)

const handleScroll = () => {
  scrollY.value = window.scrollY
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

watch(iconVolume, (newVal) => {
  localStorage.setItem('iconVolume', JSON.stringify(newVal))
})
const iconAction = () => {
  if (!iconVolume.value) {
    mgSharingan.value = !mgSharingan.value
    return
  }
  if (route.name === 'Home') {
    if (!audio.paused) {
      audio.pause()
      audio.currentTime = 0
      mgSharingan.value = false
      clearTimeout(timerId)
      return // Сбрасываем время воспроизведения (опционально)
    }
    mgSharingan.value = true

    audio.play()
    timerId = setTimeout(() => {
      mgSharingan.value = false
    }, 3900)
  }
}

const mousEenter = () => {
  if (audio.paused) {
    mgSharingan.value = true
    hovered.value = true
  }
}

const mousEleave = () => {
  if (audio.paused) {
    mgSharingan.value = false
    hovered.value = false
  }
}

// watch(
//   () => route.name,
//   (newRouteName) => {
//     if (newRouteName === 'Home') {

//     }
//   },
// )

const iconSrc = computed(() => (mgSharingan.value ? hoverSrc : normalSrc))

watch(
  () => route.fullPath,
  () => {
    scrollState.value = false
    scrollMenu.value = false
    mgSharingan.value = false
    audio.pause()
    audio.currentTime = 0
  },
)
watch(scrollY, (val) => {
  let scrollVal = 0
  if (isTouchDevice) {
    scrollVal = 700
  } else {
    scrollVal = 1200
  }
  if (val >= scrollVal) {
    kunai_show.value = true
  } else {
    kunai_show.value = false
    kunaiImg.value = '/kunai.png'
  }
})

const scrollToTop = () => {
  kunaiImg.value = '/kunai_flash.png'
  window.scrollTo({
    top: 0,
    behavior: 'smooth', // плавная прокрутка
  })
}
</script>

<template>
  <div
    style="
      background-image: url('/back.jpg');
      background-size: cover;
      background-position: center;
      width: 100%;
      height: 100vh;
      position: fixed;
      z-index: -10;
    "
  ></div>

  <Header />

  <div class="relative flex items-center justify-center w-full">
    <div class="absolute left-0">
      <Scroll
        v-model:iconVolume="iconVolume"
        v-model:scrollState="scrollState"
        v-model:scrollMenu="scrollMenu"
      />
    </div>

    <RouterLink to="/">
      <div class="hoverImg">
        <img
          class="w-35 sm:w-40 md:w-40 lg:w-50 xl:w-60"
          :src="iconSrc"
          alt=""
          @click="iconAction"
          @mouseenter="!isTouchDevice && mousEenter()"
          @mouseleave="!isTouchDevice && mousEleave()"
        />
      </div>
    </RouterLink>
  </div>

  <main class="m-auto pt-5 pb-10 bg-black/80 rounded-xl mt-10 w-full xl:w-[80%]">
    <RouterView />
  </main>
  <div v-show="kunai_show" class="w-15 fixed right-0 bottom-0 md:w-25 xl:w-25">
    <img @click="scrollToTop" :src="kunaiImg" alt="" />
  </div>
  <!-- <Footer /> -->
</template>
