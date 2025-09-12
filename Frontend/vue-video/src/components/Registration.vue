<script setup>
import { ref, inject } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config'
import { useRouter } from 'vue-router'
const userAunth = inject('userAunth')
const router = useRouter()
const username = ref()
const email = ref()
const password = ref()
const errors = ref({})
const error = ref('') // для вывода ошибки
const regist = async () => {
  error.value = ''

  // простая клиентская валидация
  if (!username.value || username.value.length < 3) {
    error.value = 'Логин должен быть минимум 3 символа'
    return
  }
  if (!email.value || !email.value.includes('@')) {
    error.value = 'Введите корректную почту'
    return
  }
  if (!password.value || password.value.length < 8) {
    error.value = 'Пароль должен быть минимум 8 символов'
    return
  }

  try {
    const { data } = await axios.post(`${API_BASE_URL}/auth/users/`, {
      username: username.value,
      email: email.value,
      password: password.value,
    })

    // можно очистить поля после успешной регистрации
    username.value = ''
    email.value = ''
    password.value = ''
    // localStorage.setItem('access', data.access)
    // localStorage.setItem('refresh', data.refresh)
    router.push('/login')
    console.log('Токены сохранены в localStorage')
  } catch (err) {
    if (err.response && err.response.data) {
      errors.value = err.response.data

      // Проверяем конкретно username
      if (errors.value.username) {
        error.value = 'Пользователь с таким именем уже есть'
      }
    }
  }
}
</script>

<template>
  <div class="flex flex-col items-center text-white border p-4">
    <h1>Регистрация</h1>
    <p v-show="error">{{ error }}</p>
    <input
      v-model="username"
      class="border font-bold p-2 text-[#000000] bg-[#cda66c] mb-5"
      placeholder="Логин"
      type="text"
    />
    <input
      v-model="email"
      class="border font-bold p-2 text-[#000000] bg-[#cda66c] mb-5"
      placeholder="Почта"
      type="email"
    />
    <input
      v-model="password"
      class="border font-bold p-2 text-[#000000] bg-[#cda66c] mb-5"
      placeholder="Пароль"
      type="password"
    />

    <button @click="regist" class="bg-[#cda66c] hover:opacity-80 border p-2">
      Зарегистрироваться
    </button>
  </div>
</template>
