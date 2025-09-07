<script setup>
defineProps({
  id: Number,
  poster: String,
  title: String,
  description: String,
  linkTo: String,
  titleClass: String,
  descriptionClass: String,
})
</script>

<template>
  <div
    class="group bg-[#cba061] text-white hover:text-black  hover:bg-white rounded-b-md overflow-hidden  transition-colors duration-300"
  >
    <RouterLink :to="{ name: linkTo, params: { id: id } }">
      <div class="relative bg-[#cba061]  group-hover:bg-white transition-colors duration-300">
        <!-- Картинка -->
        <img
          class="w-full transition-opacity duration-300 group-hover:opacity-50"
          :src="poster"
          alt=""
        />
        <!-- Текст по центру при hover -->
      </div>

      <div class="text-center pb-5 px-4">
        <p :class="titleClass">{{ title }}</p>
        <p class="text-sm text-black xl:text-xl" v-html="description"></p>
      </div>
    </RouterLink>
  </div>
</template>
