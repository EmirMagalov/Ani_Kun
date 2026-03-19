<script setup>
import { watch, ref, toRef, onMounted, onBeforeUnmount, provide } from 'vue'
import axios from 'axios'
import Plyr from 'plyr'
import Hls from 'hls.js'
import 'plyr/dist/plyr.css'
import { API_BASE_URL } from '@/config.js'
import { Ngin_Base_URL } from '@/config.js'

let player_room

let hls = null
const path = ref('')
const videoRef = ref(null)

const props = defineProps({
  path: String,
  seasonId: Number,
  sendAction: Function,
  videoEvents: Array,
  currentTimeHandler: Function,
  time: Object,
})

const timeRef = toRef(props, 'time')
const sendAction = props.sendAction

watch(
  () => props.videoEvents.slice(), // создаём копию массива для срабатывания watch
  (events) => {
    if (!events.length) return
    const lastEvent = events[events.length - 1] // берём последнее событие
    console.log(lastEvent)
    if (lastEvent.action === 'pause_all' && player_room) {
      player_room.pause()
      if (lastEvent.pause) {
        if (lastEvent.time) player_room.currentTime = Math.floor(lastEvent.time)
        sendAction('time_update', { time: player_room.currentTime, pause: true })
      } else {
        if (lastEvent.time) player_room.currentTime = Math.floor(lastEvent.time)
        sendAction('time_update', { time: player_room.currentTime })
        setTimeout(() => {
          player_room.play()
        }, 1500)
      }
    }
  },
  { deep: true },
)

watch(
  () => props.path,
  (newPath) => {
    if (!newPath) return
    initPlayer(newPath)
  },
)
const initPlayer = (path) => {
  if (player_room) {
    player_room.destroy()
    player_room = null
  }
  if (hls) {
    hls.destroy()
    hls = null
  }

  if (!videoRef.value || !path) return

  if (Hls.isSupported()) {
    hls = new Hls()
    hls.loadSource(path)
    hls.attachMedia(videoRef.value)
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = path // ✅ Safari
  }

  hls.on(Hls.Events.MANIFEST_PARSED, () => {
    const levels = hls.levels.map((l) => l.height).sort((a, b) => b - a)
    player_room = new Plyr(videoRef.value, {
      controls: [
        'play-large',
        'play',
        'progress',
        'current-time',
        'duration',
        'mute',
        'volume',
        'settings',
        'fullscreen',
      ],
      settings: ['captions', 'quality', 'speed'],
      keyboard: { global: true },
    })
    // Сохраняем имя пользователя в плеере для фильтрации событий
    player_room.user = props.userData?.username || 'unknown'

    // player_room.on('play', () => {
    //   if (!isLocalEvent.value) {
    //     sendAction('play', { time: player_room.currentTime })
    //   }
    //   isLocalEvent.value = false
    // })
    player_room.on('pause', () => {
      sendAction('time_update', { time: player_room.currentTime, pause: true })
    })
    // player_room.on('seeked', () => {
    //   if (!isLocalEvent.value) {
    //     sendAction('seek', { time: player_room.currentTime })
    //   }
    //   isLocalEvent.value = false
    // })

    const pauseButton = document.createElement('button')
    pauseButton.className = 'plyr__pause-button hidden'
    pauseButton.textContent = '❚❚'
    player_room.elements.container.appendChild(pauseButton)

    const updateButtonVisibility = () => {
      const controlsVisible =
        !player_room.elements.container.classList.contains('plyr--hide-controls')
      if (player_room.playing && controlsVisible) {
        pauseButton.classList.remove('hidden')
      } else {
        pauseButton.classList.add('hidden')
      }
    }

    pauseButton.addEventListener('click', () => {
      if (player_room.playing) player_room.pause()
      else player_room.play()
    })

    player_room.on('play', updateButtonVisibility)
    player_room.on('pause', updateButtonVisibility)
    const observer = new MutationObserver(updateButtonVisibility)
    observer.observe(player_room.elements.container, {
      attributes: true,
      attributeFilter: ['class'],
    })
  })
}
// const time = (time, pause) => {
//   const timeObj = time

// }
const syncInterval = setInterval(() => {
  if (player_room && player_room.playing) {
    sendAction('time_update', { time: player_room.currentTime })
  }
}, 1000) // каждую секунду

onBeforeUnmount(() => {
  if (player_room) player_room.destroy()
  clearInterval(syncInterval)
})
</script>

<template>
  <div>
    <div class="player2">
      <video tabindex="0" ref="videoRef" playsinline controls width="400px"></video>
    </div>
  </div>
</template>

<style>
.player2 .plyr {
  width: 1100px; /* для десктопа */
  height: 800px;
}

@media screen and (max-width: 768px) {
  .player2 .plyr {
    width: 100%; /* для телефонов */
    height: 100%;
  }
}
</style>
