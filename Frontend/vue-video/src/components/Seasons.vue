<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import Card from './Card.vue'
import { API_BASE_URL } from '@/config.js'
import CardGrid from './CardGrid.vue'
const route = useRoute()
const seasons = ref([])
onMounted(async () => {
  try {
    const { data } = await axios.get(`${API_BASE_URL}/seasons/seasons?anime_id=${route.params.id}`)
    seasons.value = data
    console.log(data)
  } catch (err) {
    console.log(err)
  }
})
</script>

<template>
  <div class="flex flex-col items-center justify-center">
    <div class="">
      <h1
        v-if="seasons.length"
        class="text-3xl text-white font-bold text-center text-shadow-md text-shadow-[#cba061]"
      >
        {{ seasons[0].anime_name }}
      </h1>
    </div>
    <CardGrid :items="seasons" :description="(s) => `${s.type==='season'?s.number + ' сезон':'Фильм'}`" link-to="Episodes" />
  </div>
</template>
