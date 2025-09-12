<script setup>
import { onMounted, ref, inject, watch, onBeforeUnmount, compile } from 'vue'
import { WS_BASE_URL } from '@/config'
import { useRoute, useRouter } from 'vue-router'
import Episodes from './Episodes.vue'
import RoomVideo from './RoomVideo.vue'
const route = useRoute()
const router = useRouter()
const userData = inject('userData')
const userLoaded = inject('userLoaded')
const timeObj = ref({ value: 'Pause' })
const roomName = `${route.params.username}`
let ws = null
const participantsTime = ref({})
const videoEvents = ref([])
const messages = ref([])
const text = ref('')
const participants = ref([])
const ready = ref(false) // флаг, что можно открывать комнату
const pause = ref({})
const x = ref(100) // начальная позиция слева
const y = ref(100) // начальная позиция сверху
const dragWindow = ref(null)
let offsetX = 0
let offsetY = 0
let dragging = false
const isTouchDevice = inject('isTouchDevice')
const keybRoom = ref(false)
const initWebSocket = () => {
  if (!roomName || roomName === 'Null') return
  ws = new WebSocket(`${WS_BASE_URL}/room/${roomName}/?token=${localStorage.getItem('access')}`)
  ws.onopen = () => {
    console.log('WebSocket подключён!')

    // отправляем join только после подключения

    sendAction('join', { username: userData.value.username })
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.action === 'synchron') {
      // пробросим в RoomVideo
      videoEvents.value.push(data)
    } else if (data.action === 'time_update') {
      participantsTime.value[data.user] = data.time

      pause.value[data.user] = data.pause
    } else if (data.action === 'participants') {
      participants.value = data.participants
      const participantsArray = Array.isArray(participants.value) ? participants.value : []
      console.log('Обновлён список участников:', participants.value)
      if (
        route.params.username === userData.value.username || // текущий пользователь — админ комнаты
        participantsArray.includes(route.params.username) // текущий пользователь уже в комнате
      ) {
        ready.value = true
      } else {
        router.push('/')
        setTimeout(() => {
          alert(`Комната ${route.params.username} больше недоступна`)
        }, 100)
      }
    } else if (data.action === 'message') {
      messages.value.push(data)
    }
  }
}

// проверка авторизации и готовности
const checkUser = () => {
  if (!userLoaded.value) return // данные ещё не пришли
  if (!userData.value) {
    router.push('/login') // редирект если не авторизован
    return
  }
  initWebSocket()
}
const startDrag = (e) => {
  if (!isTouchDevice) return // только для мобильных
  e.preventDefault() // блокируем начало прокрутки
  dragging = true
  offsetX = e.touches[0].clientX - x.value
  offsetY = e.touches[0].clientY - y.value
  document.body.style.overflow = 'hidden' // блокируем скролл
  window.addEventListener('touchmove', onDrag, { passive: false })
  window.addEventListener('touchend', stopDrag)
}

const onDrag = (e) => {
  if (!dragging) return
  e.preventDefault()
  x.value = e.touches[0].clientX - offsetX
  y.value = e.touches[0].clientY - offsetY
}

const stopDrag = () => {
  dragging = false
  window.removeEventListener('touchmove', onDrag)
  window.removeEventListener('touchend', stopDrag)
}
// проверка сразу при монтировании
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

const synchronization = () => {
  console.log(roomName)
  const myTime = participantsTime.value[roomName]
  const myPause = pause.value[roomName]
  timeObj.value = { time: myTime, pause: myPause } // новое значение — новый объект
}

const onFocus = () => {
  keybRoom.value = true
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
        :seasonId="Number(route.params.seasonId)"
        :sendAction="sendAction"
        :videoEvents="videoEvents"
        :time="timeObj"
      />
    </div>
    <div class="w-full p-5">
      <div class="border p-2">
        <ul>
          <li v-for="participant in participants" :key="participant">
            <div class="flex gap-3">
              <div>{{ participant }}:</div>
              <div>
                {{
                  participantsTime[participant] != null
                    ? `${Math.floor(participantsTime[participant] / 60)}:${Math.floor(
                        participantsTime[participant] % 60,
                      )
                        .toString()
                        .padStart(2, '0')}`
                    : '0:00'
                }}
              </div>
              <div>
                {{ pause[participant] ? '(Пазуа)' : '' }}
              </div>
            </div>
          </li>
        </ul>
        
      </div>
      <div class="participants mb-2 mt-2 text-white float-right">
          <button class="border hover:opacity-80  px-5" @click="synchronization">Синхронизировать</button>
        </div>
      <div
        class="border h-20 max-h-50 xl:h-80 xl:max-h-100 w-full p-2 overflow-y-auto wrap-break-word"
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
        <button class="border float-right mt-2 px-5 hover:opacity-80" @click="send">Отправить</button>
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
