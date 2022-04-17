<template>
  <my-header msg="Netology Shop"/>
  <router-view/>
</template>

<script>
import MyHeader from '@/components/MyHeader.vue'

export default {
  components: {
    MyHeader
  }
}
</script>

<style>
  body {
    --tw-bg-opacity: 1;
    background-color: rgb(17 24 39 / var(--tw-bg-opacity));
  }
</style>
