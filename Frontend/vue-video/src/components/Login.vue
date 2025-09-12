<script setup>
import { ref, inject } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '@/config'
import axios from 'axios'
const router = useRouter()
const username = ref('')
const password = ref('')
const errors = ref('')
const userAunth = inject('userAunth')
const userData = inject('userData')

const login = async () => {
  errors.value = ''
  try {
    const { data } = await axios.post(`${API_BASE_URL}/auth/token/login/`, {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('token', data.auth_token)
    window.location.href = '/'
  } catch (err) {
    console.log(err)
  }
  // сохраняем токены

  // localStorage.setItem('refresh', token.data.refresh)

  // const user = await api.get('/users/me/')

  // можно сразу получить данные пользователя
  // userData должен быть реактивным через provide/inject

  // userAunth.value = true // сохраняем объект пользователя
  // userData.value = user.data // редирект на главную
  //
}
</script>

<template>
  <div class="flex flex-col items-center text-white border p-4">
    <h1>Вход</h1>
    <p v-if="errors" class="text-red-500">{{ errors }}</p>
    <input
      v-model="username"
      class="border font-bold p-2 text-[#000000] bg-[#cda66c] mb-5"
      placeholder="Логин"
      type="text"
    />
    <input
      v-model="password"
      class="border font-bold p-2 text-[#000000] bg-[#cda66c] mb-5"
      placeholder="Пароль"
      type="password"
    />

    <button @click="login" class="bg-[#cda66c] hover:opacity-80 border p-2">Войти</button>
    <div class="mt-5">
      <router-link to="/registration">
        <h1 class="text-[#2ea4d6] hover:underline">Регистрация</h1>
      </router-link>
    </div>
  </div>
</template>
