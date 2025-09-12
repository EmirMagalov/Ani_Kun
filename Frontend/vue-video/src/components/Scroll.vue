<script setup>
import axios from 'axios'
import { ref, computed, inject } from 'vue'
const userData = inject('userData')
const userAunth = inject('userAunth')
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '@/config'
const router = useRouter()
const logout = async () => {
  const token = localStorage.getItem('token')
  await axios.post(
    `${API_BASE_URL}/auth/token/logout/`,
    {},
    {
      headers: {
        Authorization: `Token ${token}`,
      },
    },
  )
  localStorage.removeItem('token')

  if (userAunth) userAunth.value = false // если используешь provide/inject
  if (userData) userData.value = null
  router.push('/')
}
const props = defineProps({
  scrollState: Boolean,
  iconVolume: Boolean,
  scrollMenu: Boolean,
})

const emit = defineEmits(['update:iconVolume', 'update:scrollState', 'update:scrollMenu'])

const scrollOpen = '/scroll-open.png'
const scrollClose = '/scroll-close.png'

const openOption = computed(() => (props.scrollState ? scrollOpen : scrollClose))
const scrollButton = () => {
  emit('update:scrollState', !props.scrollState)
  emit('update:scrollMenu', !props.scrollMenu)
}

const handleCheck = (e) => {
  emit('update:iconVolume', e.target.checked)
  scrollButton()
}
</script>

<template>
  <div @click="scrollButton">
    <img :src="openOption" class="h-60 xl:h-90 lg:h-80 md:h-70" alt="" />
  </div>

  <!-- Анимация появления меню -->
  <transition name="fade">
    <div v-show="scrollMenu" class="absolute left-[25%] top-[20%]">
      <div class="flex flex-col text-md md:text-xl lg:text-xl xl:text-2xl font-bold gap-3">
        <RouterLink active-class="text-[#c23734]" to="/">
          <h1 class="hover:text-[#c23734] inline-block">Аниме</h1>
        </RouterLink>
        <RouterLink active-class="text-[#c23734]" to="/looks">
          <h1 class="hover:text-[#c23734] inline-block">Просмотренные</h1>
        </RouterLink>
        <div class="flex gap-3 items-center">
          <input type="checkbox" :checked="props.iconVolume" @change="handleCheck" />

          <label for="checkbox">Проигрывание иконки</label>
        </div>
        <div v-if="!userAunth">
          <RouterLink to="/login">
            <h1 class="hover:text-[#c23734] inline-block">Вход</h1>
          </RouterLink>
        </div>
        <div v-else>
          <h1 @click="logout" class="cursor-pointer hover:text-[#c23734] inline-block">Выход</h1>
        </div>
      </div>
    </div>
  </transition>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 1s ease,
    transform 1s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-leave-active {
  transition: none;
}
.fade-leave-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(0);
}
</style>
