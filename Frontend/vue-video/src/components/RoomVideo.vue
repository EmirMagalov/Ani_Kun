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
const episodesDataRef = ref([])
const epAll = ref([])
const video_url = ref()
const path = ref()
const videoRef = ref(null)
const episode = ref()

const props = defineProps({
  seasonId: Number,
  sendAction: Function,
  videoEvents: Array,
  currentTimeHandler: Function,
  time: Object,
})
const timeRef = toRef(props, 'time')
const sendAction = props.sendAction

// Обработка входящих событий WebSocket
// watch(
//   () => props.videoEvents,
//   (newEvents) => {
//     if (!player_room || !newEvents.length) return
//     const event = newEvents[newEvents.length - 1] // Последнее событие
//     if (event.user === player_room.user) return // Игнорируем свои события

//     switch (event.action) {
//       case 'synchron':
//         console.log(event.time)

//         if (event.time !== 'Pause') {
//           if (event.time) player_room.currentTime = event.time
//           player_room.play()
//         } else {
//           player_room.pause()
//         }
//         // case 'play':
//         //   if (!player_room.playing) {
//         //     isLocalEvent.value = true // Отключаем отправку события
//         //     player_room.play().catch(() => console.log('Автозапуск заблокирован браузером'))
//         //     if (event.time) player_room.currentTime = event.time
//         //   }
//         //   break
//         // case 'pause':
//         //   if (player_room.playing) {
//         //     isLocalEvent.value = true
//         //     player_room.pause()
//         //     if (event.time) player_room.currentTime = event.time
//         //   }
//         //   break
//         // case 'seek':
//         //   if (Math.abs(player_room.currentTime - event.time) > 1) {
//         //     isLocalEvent.value = true
//         //     player_room.currentTime = event.time
//         //   }
//         break
//     }
//   },
//   { deep: true },
// )

onMounted(async () => {
  if (player_room) {
    player_room.destroy()
    player_room = null
  }
  if (hls) {
    hls.destroy()
    hls = null
  }
  console.log(props.seasonId)
  try {
    const { data } = await axios.get(`${API_BASE_URL}/episodes/eps/?season=${props.seasonId}`)
    episodesDataRef.value = data
    epAll.value = data.map((ep) => ep.number)
    episode.value = data.find((ep) => ep.number === 1)
    console.log(episode.value)
    if (!episode.value) {
      episode.value = data[0] || null
    }
    await loadVideo()
  } catch (err) {
    console.log(err)
  }
  if (!videoRef.value || !path.value) return

  if (Hls.isSupported()) {
    hls = new Hls()
    hls.loadSource(path.value)
    hls.attachMedia(videoRef.value)
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = path.value // ✅ Safari
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
})
watch(timeRef, () => {
  const timeObj = timeRef.value

  if (timeObj.pause) {
    if (!player_room.paused) player_room.pause()
    if (timeObj.time) player_room.currentTime = Math.floor(timeObj.time)
    sendAction('time_update', { time: player_room.currentTime, pause: true })
  } else {
    player_room.play()
    if (timeObj.time) player_room.currentTime = Math.floor(timeObj.time) + 1.5
    sendAction('time_update', { time: player_room.currentTime })
  }
})
const syncInterval = setInterval(() => {
  if (player_room && player_room.playing) {
    sendAction('time_update', { time: player_room.currentTime })
  }
}, 1000) // каждую секунду

onBeforeUnmount(() => {
  if (player_room) player_room.destroy()
  if (player_room) player_room.destroy()
  clearInterval(syncInterval)
})

const loadVideo = async () => {
  if (!episode.value) return
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/video_url/get_video/?episode_number=${episode.value.number}&season_id=${props.seasonId}`,
    )
    video_url.value = data
    if (video_url.value?.video_file) {
      path.value = `${Ngin_Base_URL}/media/videos/episode_${video_url.value.video_id}/master.m3u8`
    }
  } catch (err) {
    console.log(err)
  }
}
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
