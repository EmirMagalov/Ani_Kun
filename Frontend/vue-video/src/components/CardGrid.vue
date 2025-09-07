<script setup>
import Card from './Card.vue'

defineProps({
  items: Array,
  description: Function,
  linkTo: String,
})
</script>

<template>
  <div
    class="px-4 py-4 grid grid-cols-2 w-full sm:w-[70%] lg:w-[70%] gap-6 items-end sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 xl:w-[80%] xl:px-0"
  >
    <Card
      v-for="item in items"
      :key="item.id"
      :id="item.id"
      :poster="item.poster"
      :title="item.title"
      titleClass="font-bold mt-3 mb-3 text-md lg:text-lg xl:text-2xl"
      :description="description(item)"
     
      :link-to="linkTo"
    />
  </div>
</template>
