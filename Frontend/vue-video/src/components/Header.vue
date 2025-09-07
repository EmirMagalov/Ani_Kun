<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config'
const focus = ref(false)
const search = ref([])

const Input = async (event) => {
  try {
    const { data } = await axios.get(`${API_BASE_URL}/seasons/?search=${event.target.value}`)

    search.value = data.results
  } catch (err) {}
}
const onFocus = () => {
  focus.value = true
}

const onBlur = () => {
  // задержка нужна, чтобы можно было кликнуть по ссылке в списке,
  // иначе blur сразу закроет div
  setTimeout(() => {
    focus.value = false
  }, 200)
}
</script>

<template>
  <header class="bg-[#cba061] border-b border-white shadow-md mb-10 py-2 lg:py-6 xl:py-8">
    <div class="bg-[#00006d] text-shadow-lg shadow-white py-3 px-10 relative">
      <div class="flex items-center justify-center flex-1">
        <input
          @focus="onFocus"
          @blur="onBlur"
          @input="Input"
          :placeholder="focus ? '' : ['Поиск...']"
          type="text"
          class="p-2 border focus:outline-none focus:border-[#c23734] focus:border-1 rounded-lg bg-white w-40 lg:w-48 xl:w-64 xl:py-4"
        />
        <img
          src="/naruto_black.svg"
          :class="[
            'w-17 font-bold absolute pointer-events-none xl:w-22',
            focus ? 'opacity-15' : 'opacity-100',
          ]"
          alt=""
        />
        <div
          v-show="focus && search.length"
          class=" opacity-95 flex justify-center p-5 w-full absolute top-16 z-1  xl:top-20"
        style="background: url('/haven.png');">
          <ul>
            <li class="font-bold text-base text-[#2ea4d6] border-b border-black opacity-100 hover:text-[#cda66c] p-1 xl:text-xl" v-for="s in search" :key="s.id">
              <RouterLink :to="{ name: 'Episodes', params: { id: s.id } }">
                {{ s.title }}
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </header>
</template>
