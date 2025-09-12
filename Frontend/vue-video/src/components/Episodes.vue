<script setup>
import axios from 'axios'
import { ref, onMounted, watch, computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import Video from './Video.vue'
import { API_BASE_URL } from '@/config.js'
import { Ngin_Base_URL } from '@/config.js'

const props = defineProps({
  seasonId: Number,
})



const route = useRoute()
const routeParams = route.params


const episode = ref()
const video_url = ref()
const path = ref()
const saved = JSON.parse(localStorage.getItem(`episode-${routeParams.id}`) || '{}')
const epNumper = ref(saved.episode ? Number(saved.episode) : 1)
const epAll = ref([])
const episodesDataRef = ref([])
const dropdownOpen = ref(false)
const playVideo = ref(true)
const userData = inject('userData')
const usernameForRoom = computed(() => userData?.value?.username || 'Null')
function saveEpisodeProgress(seasonId, episodeNumber) {
  console.log(seasonId)
  const key = `episode-${seasonId}`

  // Получаем текущий прогресс или создаем новый объект
  const existing = JSON.parse(localStorage.getItem(key)) || {}

  // Обновляем или добавляем поля
  existing.episode = episodeNumber
  existing.date = new Date().toISOString()

  // Сохраняем обратно
  localStorage.setItem(key, JSON.stringify(existing))
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`${API_BASE_URL}/episodes/eps/?season=${routeParams.id}`)
    episodesDataRef.value = data

    epAll.value = data.map((ep) => ep.number)

    episode.value = data.find((ep) => ep.number === epNumper.value)
    if (!episode.value) {
      episode.value = data[0] || null
    }
    await loadVideo()
  } catch (err) {
    console.log(err)
  }
  // saveEpisodeProgress(video_url.value.season_id, 1)
})

const loadVideo = async () => {
  if (!episode.value) return
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/video_url/get_video/?episode_number=${episode.value.number}&season_id=${routeParams.id}`,
    )
    video_url.value = data
    if (video_url.value?.video_file) {
      path.value = `${Ngin_Base_URL}/media/videos/episode_${video_url.value.video_id}/master.m3u8`
    }
  } catch (err) {
    console.log(err)
  }
}

const selectEpisode = async (num) => {
  epNumper.value = num
  saveEpisodeProgress(video_url.value.season_id, num)
  episode.value = episodesDataRef.value.find((ep) => ep.number === num)
  await loadVideo()
  playVideo.value = false
  dropdownOpen.value = false
}

const hasNextEpisode = computed(() => {
  return episodesDataRef.value.some((ep) => ep.number === episode.value.number + 1)
})

const nextEpisode = async (player = null) => {
  const nextEp = episodesDataRef.value.find((ep) => ep.number === episode.value.number + 1)

  if (nextEp) {
    playVideo.value = true
    epNumper.value = nextEp.number
    episode.value = nextEp

    await loadVideo()
    console.log(player)
    if (player) {
      player.play().catch(() => console.log('Автозапуск заблокирован браузером'))
    }
    saveEpisodeProgress(video_url.value.season_id, nextEp.number)
  }
}

watch(
  () => routeParams.id,
  async (newId) => {
    if (!newId) return

    // Загружаем новые эпизоды сезона
    try {
      const { data } = await axios.get(`${API_BASE_URL}/episodes/eps/?season=${newId}`)
      episodesDataRef.value = data
      epAll.value = data.map((ep) => ep.number)

      // Восстанавливаем прогресс из localStorage
      const saved = JSON.parse(localStorage.getItem(`episode-${newId}`) || '{}')
      epNumper.value = saved.episode ? Number(saved.episode) : 1

      episode.value = data.find((ep) => ep.number === epNumper.value) || data[0] || null
      playVideo.value = false
      await loadVideo() // загружаем видео для нового эпизода
    } catch (err) {
      console.log(err)
    }
  },
)
</script>

<template>
  <div class="relative flex text-white flex-col items-center justify-center m-b">
    <div v-if="episode" class="p-5">
      <div class="">
        <h1 class="text-3xl font-bold text-center mb-5 text-shadow-md text-shadow-[#cba061]">
          {{ video_url.anime_name }}
        </h1>
        <h1 class="text-2xl font-bold">{{ video_url.episode_title }}</h1>
        <h1 class="text-">
          {{ video_url.type === 'season' ? video_url.season_number + ' сезон' : 'Фильм' }}
          {{
            video_url.type === 'season'
              ? video_url.episode_number + ' серия'
              : video_url.episode_number
          }}
        </h1>
        <div class="mb-10">
          <div class="flex gap-5 items-center">
            <RouterLink :to="{ name: 'Seasons', params: { id: video_url.anime_id } }">
              <div
                class="gap-10 mt-5 bg-[#cba061] text-white px-4 py-2 rounded-lg hover:bg-[#c23734]"
              >
                <p class="truncate text-center">К сезонам</p>
              </div>
            </RouterLink>
            <RouterLink
              :to="{
                name: 'Room',
                params: { username: usernameForRoom, seasonId: video_url.season_id },
              }"
            >
              <div
                class="gap-10 mt-5 bg-[#cba061] text-white px-4 py-2 rounded-lg hover:bg-[#c23734]"
              >
                <p class="truncate text-center">Совместный просмотр</p>
              </div>
            </RouterLink>
          </div>
          <div v-if="video_url.type === 'season'" class="z-10 w-24 mt-5">
            <button
              @click="dropdownOpen = !dropdownOpen"
              :class="[
                'bg-[#cba061] text-white rounded-lg w-full px-4 py-2 whitespace-nowrap',
                dropdownOpen ? 'bg-[#cba061]' : 'hover:bg-[#c23734] hover:opacity-100',
              ]"
            >
              {{ epNumper }} серия
            </button>

            <ul
              v-show="dropdownOpen"
              class="max-h-[150px] overflow-y-auto absolute bg-[#cba061]text-white mt-1 rounded-lg shadow-lg overflow-auto z-50"
            >
              <li
                v-for="ep in epAll"
                :key="ep"
                @click="selectEpisode(ep)"
                :class="[
                  'cursor-pointer whitespace-nowrap px-4 py-2',
                  ep === epNumper ? 'bg-[#A0A0A0]' : 'bg-[#cba061] hover:bg-[#c23734]',
                ]"
              >
                {{ ep }} серия
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- <video :src="path" controls></video> -->
      <Video
        :season-id="video_url.season_id"
        :path="path"
        v-model:episode="episode"
        @nextEpisode="nextEpisode"
        :hasNextEpisode="hasNextEpisode"
        v-model:dropdownOpen="dropdownOpen"
        :playVideo="playVideo"
        :saveEpisodeProgress="saveEpisodeProgress"
      />
      <!-- <div v-if="hasNextEpisode && showNext" class="relative">
        <button
          @click="nextEpisode"
          class="bg-[#cba061] absolute bottom-15 right-2 text-white px-4 py-2 rounded-lg opacity-80 hover:opacity-100 z-50"
        >
          Следующая серия
        </button>
      </div> -->
    </div>
  </div>
</template>
