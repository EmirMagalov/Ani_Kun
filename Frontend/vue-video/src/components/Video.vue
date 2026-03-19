<script setup>
import { watch, ref, onMounted, onBeforeUnmount } from 'vue'
import Plyr from 'plyr'
import Hls from 'hls.js'
import 'plyr/dist/plyr.css'
const savedTimes = {}
const savedScroll = ref(0)
const videoRef = ref(null)
let player
let hls = null
const showNext = ref(false)
const props = defineProps({
  seasonId: Number,
  path: String,
  episode: Object,
  hasNextEpisode: Boolean,
  playVideo: Boolean,
  saveEpisodeProgress: Function,
  // episodesData: Array,
  // loadVideo:Function
})
const emit = defineEmits(['nextEpisode', 'update:dropdownOpen'])

onMounted(() => {
  if (!videoRef.value || !props.path) return

  // убиваем предыдущий плеер если был
  if (player) {
    player.destroy()
    player = null
  }
  if (hls) {
    hls.destroy()
    hls = null
  }

  if (Hls.isSupported()) {
    hls = new Hls()
    hls.loadSource(props.path) // ✅ вот тут props.path
    hls.attachMedia(videoRef.value)
  } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    videoRef.value.src = props.path // ✅ Safari
  }

  hls.on(Hls.Events.MANIFEST_PARSED, () => {
    const levels = hls.levels.map((l) => l.height).sort((a, b) => b - a)

    player = new Plyr(videoRef.value, {
      controls: [
        'play-large',
        'play',
        'progress',

        'current-time',
        'duration', // 👈
        // 'rewind',
        // 'fast-forward',
        'mute',
        'volume',

        'settings',

        'fullscreen',
      ],

      settings: ['captions', 'quality', 'speed'],
      keyboard: { global: true }, // важно
      quality: {
        forced: true,
        options: levels,
        onChange: (q) => setHlsQuality(q),
      },
    })
    document.addEventListener('keydown', (e) => {
      const tag = e.target.tagName.toLowerCase()
      const editable = e.target.isContentEditable

      // если печатаем в input / textarea / contenteditable — не реагируем
      if (tag === 'input' || tag === 'textarea' || editable) {
        return
      }

      if (e.code === 'KeyF') {
        player.fullscreen.toggle()
      }
    })

    player.on('exitfullscreen', () => {
      if (videoRef.value) {
        videoRef.value.scrollIntoView({ behavior: 'auto', block: 'start' })
      }
    })
    const pauseButton = document.createElement('button')
    pauseButton.className = 'plyr__pause-button hidden'
    pauseButton.textContent = '❚❚'
    player.elements.container.appendChild(pauseButton)

    // функция управления видимостью
    const updateButtonVisibility = () => {
      const controlsVisible = !player.elements.container.classList.contains('plyr--hide-controls')
      if (player.playing && controlsVisible) {
        pauseButton.classList.remove('hidden')
      } else {
        pauseButton.classList.add('hidden')
      }
    }
    pauseButton.addEventListener('click', () => {
      if (player.playing) player.pause()
      else player.play()
    })

    // события плеера
    player.on('play', updateButtonVisibility)
    player.on('pause', updateButtonVisibility)

    // MutationObserver для отслеживания изменения интерфейса
    const observer = new MutationObserver(updateButtonVisibility)
    observer.observe(player.elements.container, {
      attributes: true,
      attributeFilter: ['class'],
    })
    const onFirstPlay = () => {
      // берем id аниме (например, передаёшь через props или data)
      const seasonId = props.seasonId

      // достаём список из localStorage
      let list = JSON.parse(localStorage.getItem('animeList') || '[]')

      // проверяем, нет ли уже этого аниме
      if (!list.includes(seasonId)) {
        list.push(seasonId)
        localStorage.setItem('animeList', JSON.stringify(list))
        console.log('Добавлено в список:', seasonId)
      }

      // отписываемся, чтобы сработало только один раз
      player.off('play', onFirstPlay)
    }

    player.on('play', onFirstPlay)
    player.on('play', () => {
      props.saveEpisodeProgress(props.seasonId, props.episode.number)
    })
    player.on('loadedmetadata', () => {
      const savedTime = localStorage.getItem(`video-${props.episode.id}`)
      if (savedTime) player.currentTime = parseFloat(savedTime)
    })
    player.on('play', () => emit('update:dropdownOpen', false))
    player.on('pause', () => emit('update:dropdownOpen', false))
    // Сохраняем позицию при просмотре
    player.on('timeupdate', () => {
      localStorage.setItem(`video-${props.episode.id}`, player.currentTime.toString())
      savedTimes[props.episode.id] = player.currentTime
      if (player.currentTime >= 1200) {
        showNext.value = true
      } else {
        showNext.value = false
      }
    })
    player.on('ended', () => {
      emit('nextEpisode')
    })
  })
})
watch(showNext, () => updateNextButton())
let prevEpisodeId = props.episode?.id
watch(
  () => props.path,
  (newPath) => {
    if (!newPath || !videoRef.value) return

    // сохраняем прогресс предыдущей серии
    if (player && prevEpisodeId) {
      savedTimes[prevEpisodeId] = player.currentTime
      localStorage.setItem(`video-${prevEpisodeId}`, player.currentTime.toString())
    }

    const currentEpisodeId = props.episode?.id
    prevEpisodeId = currentEpisodeId

    const savedTime =
      savedTimes[currentEpisodeId] ??
      parseFloat(localStorage.getItem(`video-${currentEpisodeId}`)) ??
      0

    // очищаем старый HLS
    if (hls) {
      hls.destroy()
      hls = null
    }

    if (Hls.isSupported()) {
      hls = new Hls()
      hls.loadSource(newPath)
      hls.attachMedia(videoRef.value)
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        const setTime = () => {
          player.currentTime = savedTime
          if (props.playVideo) player.play()
          videoRef.value.removeEventListener('loadedmetadata', setTime)
        }

        if (videoRef.value.readyState >= 1) {
          setTime()
        } else {
          videoRef.value.addEventListener('loadedmetadata', setTime)
        }
      })
    } else {
      videoRef.value.src = newPath
      videoRef.value.addEventListener(
        'loadedmetadata',
        () => {
          player.currentTime = savedTime
          if (props.playVideo) player.play()
        },
        { once: true },
      )
    }
  },
)

const updateNextButton = () => {
  const nextButton = player.elements.controls.querySelector('.plyr__control--next')
  if (showNext.value && !nextButton && props.hasNextEpisode) {
    // вставляем кнопку
    player.elements.controls.insertAdjacentHTML(
      'beforeend',
      `
      <button type="button" class="plyr__control plyr__control--next" title="Следующая серия">
      Следующая серия
      </button>
    `,
    )
    player.elements.controls
      .querySelector('.plyr__control--next')
      .addEventListener('click', () => emit('nextEpisode'))
  } else if (!showNext.value && nextButton) {
    // удаляем кнопку
    nextButton.remove()
  }
}

function setHlsQuality(q) {
  if (!hls) return
  const levelIndex = hls.levels.findIndex((l) => l.height === q)
  if (levelIndex !== -1) {
    hls.currentLevel = levelIndex
    console.log('Установлено качество HLS:', q)
  } else {
    console.warn('Такого качества нет в HLS:', q)
  }
}
onBeforeUnmount(() => {
  if (player) player.destroy()
})
</script>

<template>
  <div class="player1">
    <video tabindex="0" ref="videoRef" playsinline controls></video>
  </div>
</template>

<style>
.plyr {
  --plyr-color-main: #cba061;
  box-shadow: 0 8px 24px #cba061;
  --plyr-video-control-background-hover: #c23734;
}

.plyr__pause-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  font-size: 30px;
  padding: 15px 20px;
  border-radius: 6px;
  background-color: #cba061;
  color: white;
  border: none;
  cursor: pointer;
  opacity: 70%;
}

.hidden {
  display: none;
}

.plyr__progress {
  position: absolute;
  width: 100%;
  top: -1px; /* отступ от верха */
}

.plyr__controls__item.plyr__time--current.plyr__time {
  position: absolute;
  left: 40px;
  font-size: 15px;
}
.plyr__time--duration {
  display: inline-block !important;
  position: absolute;
  left: 90px;
  font-size: 15px;
}
.plyr__control--next {
  position: absolute;
  bottom: 90px; /* смещение от верха плеера */
  right: 10px; /* смещение от правого края */
  z-index: 10; /* чтобы была над контролами */
  background-color: #cba061;
  color: white;
  border: none;
  font-size: 20px !important;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  opacity: 70%;
}
.plyr__control--next:hover {
  opacity: 100%;
}

.plyr__control.plyr__control--overlaid {
  background-color: #cba061 !important; /* цвет круга */
  padding: 30px;
  border-radius: 20% !important; /* круглая форма */
  color: white !important; /* цвет стрелки Play */
  font-size: 36px !important; /* размер стрелки */
}
.plyr__control.plyr__control--overlaid:hover {
  background-color: #c23734 !important;
}

.plyr__control.plyr__control--overlaid svg {
  display: none !important; /* скрываем встроенный значок */
}
.plyr__control.plyr__control--overlaid::before {
  content: '';
  position: absolute;
  inset: 0;
  font: bold;
  margin: auto;
  width: 50px;
  height: 40px;
  background: url('/naruto_white.svg') no-repeat center center;
  background-size: contain;
  color: white;
}

.player1 .plyr {
  width: 800px; /* для десктопа */
  height: 500px;
}

@media screen and (max-width: 768px) {
  .player1 .plyr {
    width: 100%; /* для телефонов */
    height: 100%;
  }
}
</style>
