<script setup>
import axios from 'axios'
import { onMounted, onUnmounted, provide, ref, inject, watch, computed } from 'vue'

import { API_BASE_URL } from '@/config.js'
import CardGrid from './CardGrid.vue'
const animeItems = ref([])
const initialLoad = ref(true)
// fallback — если provide ещё не объявлен
const nextPage = ref(`${API_BASE_URL}/animes/`) // начальная страница
const loading = ref(false)

const onScroll = () => {
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const fullHeight = document.documentElement.scrollHeight

  if (scrollTop + windowHeight >= fullHeight - 100) {
    // мы почти дошли до конца страницы
    loadMoreAnimes()
  }
}
const loadMoreAnimes = async () => {
  if (!nextPage.value || loading.value) return
  loading.value = true

  try {
    const res = await axios.get(nextPage.value)
    const newAnimes = res.data.results

    // создаём массив промисов для всех запросов сезонов
    const seasonPromises = newAnimes.map(async (anime) => {
      const seasonResponse = await axios.get(
        `${API_BASE_URL}/seasons/seasons/?anime_id=${anime.id}`,
      )
      const allSeasons = seasonResponse.data || []
      anime.seasonsOnly = allSeasons.filter((s) => s.type === 'season')
      anime.moviesOnly = allSeasons.filter((s) => s.type === 'movie')
    })

    // ждём завершения всех промисов одновременно
    await Promise.all(seasonPromises)

    // добавляем элементы после обработки сезонов
    animeItems.value.push(...newAnimes)

    nextPage.value = res.data.next
    initialLoad.value = false
  } catch (err) {
    console.log(err)
  } finally {
    loading.value = false
  }
}
// обработка скролла

onMounted(() => {
  window.addEventListener('scroll', onScroll)
  loadMoreAnimes() // сразу подгружаем первую страницу
})
console.log(animeItems)

const pluralize = (count, type) => {
  // type = 'season' или 'movie'
  let word = ''
  if (type === 'season') {
    if (count % 10 === 1 && count % 100 !== 11) {
      word = 'сезон'
    } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
      word = 'сезона'
    } else {
      word = 'сезонов'
    }
  } else if (type === 'movie') {
    if (count % 10 === 1 && count % 100 !== 11) {
      word = 'фильм'
    } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
      word = 'фильма'
    } else {
      word = 'фильмов'
    }
  } else if (type === 'episode') {
    if (count % 10 === 1 && count % 100 !== 11) word = 'серия'
    else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) word = 'серии'
    else word = 'серий'
  }
  return `${count} ${word}`
}
const getDescription = (anime) => {
  const seasonsCount = anime.seasonsOnly?.length || 0
  // const episodeCount = anime.seasonsOnly?.episodes_count
  const episodesCount =
    anime.seasonsOnly?.reduce((sum, season) => sum + (season.episodes_count || 0), 0) || 0

  const moviesCount = anime.moviesOnly?.length || 0
  const seasonHTML = `<span class="season">${pluralize(seasonsCount, 'season')}</span>`
  const episodeHTML = `<span class="episode">${pluralize(episodesCount, 'episode')}</span>`
  const movieHTML = `<span class="movie">${pluralize(moviesCount, 'movie')}</span>`
  return `
    <div class="flex flex-col items-end opacity-65 ">
      ${seasonHTML}
      ${episodeHTML}
      ${moviesCount !== 0 ? movieHTML : ''}
    </div>
  `
}

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  
  <div class="flex flex-col items-center">
    <div v-if="initialLoad">
    <h1 class="text-white text-xl p-20 ">Загрузка...</h1>
  </div>
    <CardGrid v-else  :items="animeItems" :description="getDescription" link-to="Seasons" />
      <h1 v-if="loading && !initialLoad"  class="text-white">Загрузка...</h1>
  </div>

</template>
