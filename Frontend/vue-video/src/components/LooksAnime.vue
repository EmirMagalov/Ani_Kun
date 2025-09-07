<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config.js'
const itemsAnime = ref([])

onMounted(async () => {
  const looksAnime = JSON.parse(localStorage.getItem('animeList') || '[]').reverse()

  for (const anime of looksAnime) {
    const { data } = await axios.get(`${API_BASE_URL}/seasons/seasons?season_id=${anime}`)
    console.log(data)
    const episodeProgress = JSON.parse(localStorage.getItem(`episode-${anime}`)) || {}

    // добавляем новое поле каждому сезону
    const dataWithProgress = data.map((season) => ({
      ...season,
      seasonType: season.type,
      lastEpisode: episodeProgress,
      trashHover: false,
    }))

    itemsAnime.value.push(...dataWithProgress)
  }
})

const deleteLooksAnime = (animeId) => {
  const looksAnime = JSON.parse(localStorage.getItem('animeList') || '[]')
  const index = looksAnime.indexOf(animeId)
  if (index !== -1) looksAnime.splice(index, 1) // удалить его
  localStorage.setItem('animeList', JSON.stringify(looksAnime)) // записать обратно
  itemsAnime.value = itemsAnime.value.filter((anime) => anime.id !== animeId)
}
</script>

<template>
  <div class="text-white">
    <h1 class="text-white text-center text-2xl xl:text-2xl mb-10">Продолжить просмотр</h1>
    <div v-if="itemsAnime.length" class="grid grid-cols-1 p-5">
      <div v-for="anime in itemsAnime" :key="anime.id">
        <RouterLink :to="{ name: 'Episodes', params: { id: anime.id } }">
          <div
            class="flex items-center p-1 border border-white mb-5 rounded-xl p-3 justify-between hover:border-[#cba061]"
          >
            <div class="flex">
              <img :src="anime.poster" alt="" class="w-20" />
            </div>

            <div class="flex text-center w-full flex-col items-center xl:gap-5 items-center xl:cursor-pointer">
              <h1 class="text-[10px] xl:text-base">
                {{ new Date(anime.lastEpisode.date).toLocaleDateString() }}:
              </h1>

              <h1 class="text-[#2ea4d6]">
                {{ anime.title }}
              </h1>

              <h1>
                {{ anime.seasonType == 'season' ? anime.lastEpisode.episode + ' серия' : '' }}
              </h1>
            </div>

            <div>
              <button @click.prevent="deleteLooksAnime(anime.id)">
                <img
                  @mouseenter="anime.trashHover = true"
                  @mouseleave="anime.trashHover = false"
                  class="w-10 color-red cursor-pointer"
                  :src="anime.trashHover ? '/trash_hover.svg' : '/trash_1.svg'"
                  alt=""
                />
              </button>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
    <div v-else>
      <h1 class="text-center">
        Начните
        <RouterLink to="/"
          ><span class="text-[#2ea4d6] hover:underline">смотреть аниме</span></RouterLink
        >
        чтобы они сохранились для дальнейшего просмотра
      </h1>
    </div>
  </div>
</template>
