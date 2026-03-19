<script setup>
import { onMounted, ref, inject, watch, onBeforeUnmount, compile } from 'vue'
import { WS_BASE_URL } from '@/config'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import RoomVideo from './RoomVideo.vue'
import { API_BASE_URL } from '@/config'
import { Ngin_Base_URL } from '@/config'
const route = useRoute()
const router = useRouter()
const userData = inject('userData')
const userLoaded = inject('userLoaded')
const timeObj = ref({ value: 'Pause' })
const roomName = `${route.params.username}`
let ws = null
const epNumber = ref(Number(route.params.episodeNumber))
const participantsTime = ref({})
const videoEvents = ref([])
const messages = ref([])
const text = ref('')
const participants = ref([])
const ready = ref(false) // флаг, что можно открывать комнату
const pause = ref({})
const keybRoom = ref(false)
const episodesDataRef = ref([])
const epAll = ref([])
const video_url = ref()
const episode = ref()
const path = ref('')
const initWebSocket = () => {
  if (!roomName || roomName === 'Null') return
  ws = new WebSocket(`${WS_BASE_URL}/room/${roomName}/?token=${localStorage.getItem('access')}`)
  ws.onopen = () => {
    console.log('WebSocket подключён!')

    // отправляем join только после подключения

    sendAction('join', { username: userData.value.username, episode: epNumber.value })
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    videoEvents.value.push(data)
    if (data.action === 'change_episode') {
      epNumber.value = data.number
      episode.value = episodesDataRef.value.find((ep) => ep.number === data.number)
      sendAction('time_update', { time: 0 })
      loadVideo() // обновляем path
    }
    if (data.action === 'synchron') {
      // пробросим в RoomVideo
    } else if (data.action === 'time_update') {
      participantsTime.value[data.user] = data.time

      pause.value[data.user] = data.pause
    } else if (data.action === 'participants') {
      participants.value = data.participants
      const participantsArray = Array.isArray(participants.value) ? participants.value : []
      console.log('Обновлён список участников:', participants.value)
      ready.value = true
      if (
        route.params.username === userData.value.username || // текущий пользователь — админ комнаты
        participantsArray.includes(route.params.username) // текущий пользователь уже в комнате
      ) {
      } else {
        // router.push('/')
        // setTimeout(() => {
        //   alert(`Комната ${roomName} больше недоступна`)
        // }, 100)
      }
    } else if (data.action === 'message') {
      if (messages.value.length >= 35) {
        messages.value.shift()
      }
      messages.value.push(data)
    }
  }
}
1
// проверка авторизации и готовности
const checkUser = async () => {
  if (!userLoaded.value) return // данные ещё не пришли
  if (!userData.value) {
    router.push('/login') // редирект если не авторизован
    return
  }
  initWebSocket()

  try {
    console.log('number', epNumber.value)
    const { data } = await axios.get(
      `${API_BASE_URL}/episodes/eps/?season=${route.params.seasonId}`,
    )
    episodesDataRef.value = data
    episode.value = data.find((ep) => ep.number === epNumber.value)
    console.log(episodesDataRef.value)
    epAll.value = data.map((ep) => ep.number)
    if (!episode.value) {
      episode.value = data[0] || null
    }
    await loadVideo()
  } catch (err) {
    console.log(err)
  }
}

const loadVideo = async () => {
  if (!episode.value) return
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/video_url/get_video/?episode_number=${episode.value.number}&season_id=${route.params.seasonId}`,
    )
    video_url.value = data
    if (video_url.value?.video_file) {
      path.value = `${Ngin_Base_URL}/media/videos/episode_${video_url.value.video_id}/master.m3u8`
    }
  } catch (err) {
    console.log(err)
  }
}

onMounted(() => {
  checkUser()
  console.log(participants.value)
})

// watch на случай, если данные придут позже
watch(userLoaded, () => {
  checkUser()
})

const send = () => {
  if (text.value) {
    sendAction('message', { content: text.value })
    text.value = ''
  }
}

const sendAction = (action, payload = {}) => {
  if (!ws) return
  const message = {
    action,
    user: userData.value.username,
    ...payload,
  }
  ws.send(JSON.stringify(message))
}

const synchronization = (username) => {
  const myTime = participantsTime.value[username]
  const myPause = pause.value[username]
  sendAction('pause_all', { time: myTime, pause: myPause })
  // timeObj.value = { time: myTime, pause: myPause }
}

const onFocus = () => {
  keybRoom.value = true
}
const selectEpisode = async (num) => {
  epNumber.value = num
  episode.value = episodesDataRef.value.find((ep) => ep.number === num)
  await loadVideo()

  // отправляем событие в WS, чтобы все синхронизировались
  sendAction('change_episode', { number: num })
}
onBeforeUnmount(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<template>
  <div v-if="ready" class="xl:flex text-white gap-5 relative">
    <div>
      <RoomVideo
        :key="episode?.number"
        :path="path"
        :seasonId="Number(route.params.seasonId)"
        :sendAction="sendAction"
        :videoEvents="videoEvents"
        :time="timeObj"
      />
    </div>
    <div class="w-full p-5">
      <ul class="mb-3 flex divide-x overflow-auto border">
        <li
          :class="['p-2 cursor-pointer', ep === epNumber ? 'bg-[#A0A0A0]' : ' hover:bg-[#c23734] ']"
          v-for="ep in epAll"
          :key="ep"
          @click="selectEpisode(ep)"
        >
          {{ ep }} серия
        </li>
      </ul>
      <div class="border p-2 mb-2">
        <div>
          <ul>
            <li v-for="participant in participants" :key="participant">
              <div class="flex justify-between">
                <div class="flex gap-1">
                  <div>{{ participant }}:</div>
                  <div>
                    {{
                      participantsTime[participant] != null
                        ? `${Math.floor(Number(participantsTime[participant]) / 60)}:${Math.floor(
                            Number(participantsTime[participant]) % 60,
                          )
                            .toString()
                            .padStart(2, '0')}`
                        : sendAction('time_update', { time: 0, pause: true })
                    }}
                  </div>
                  <div>
                    {{ pause[participant] ? '(Пазуа)' : '' }}
                  </div>
                </div>
                <div>
                  <button
                    v-show="userData.username != participant"
                    class="hover:opacity-80"
                    @click="synchronization(participant)"
                  >
                    Синхронизировать
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div
        class="border h-50 max-h-50 xl:h-80 xl:max-h-100 w-full p-2 overflow-y-auto wrap-break-word"
      >
        <div v-for="(m, i) in messages" :key="i">
          <b class="">{{ m.user }}:</b> {{ m.content }}
        </div>
      </div>
      <div>
        <input
          placeholder="Написать в чат"
          @focus="onFocus"
          @blur="onBlur"
          v-model="text"
          type="text"
          class="border w-full p-2"
        />
        <button class="border float-right mt-2 px-5 hover:opacity-80" @click="send">
          Отправить
        </button>
      </div>
    </div>
  </div>
</template>
<style scoped>
/* .draggable {
  position: fixed;
  width: 300px;
  border: 1px solid #ccc;
  background: #fff;
  user-select: none;
} */
</style>
