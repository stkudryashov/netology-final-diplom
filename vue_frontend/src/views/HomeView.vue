<template>
  <MyHeader msg="Netology Shop"/>
  <CatalogList/>
</template>

<script>
// @ is an alias to /src
import MyHeader from '@/components/MyHeader.vue'
import CatalogList from '@/components/CatalogList.vue'

export default {
  name: 'HomeView',
  components: {
    CatalogList,
    MyHeader
  }
}
</script>
