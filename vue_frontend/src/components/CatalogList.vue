<template>
  <section class="text-gray-400 bg-gray-900 body-font">
    <div class="container px-5 py-24 mx-auto">
      <div class="flex flex-wrap -m-4">
        <div class="lg:w-1/4 md:w-1/2 p-4 w-full" v-for="product in products">
          <a class="block relative h-48 rounded overflow-hidden">
            <img alt="ecommerce" class="object-cover object-center w-full h-full block" src="https://dummyimage.com/420x260">
          </a>
          <div class="mt-4">
            <h3 class="text-gray-500 text-xs tracking-widest title-font mb-1">{{ product.category }}</h3>
            <h2 class="text-white title-font text-lg font-medium">
              <router-link :to="`/${product.id}`">{{ product.name }}</router-link>
            </h2>
            <p class="mt-1">₽{{ product.price }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: "CatalogList",
  data() {
    return {
      products : []
    }
  },
  methods: {
    async fetchProducts() {
      const response = await axios.get('http://localhost:8000/api/v1/catalog/products');

      response.data.results.forEach(product => this.products.push({
        id: product.id,
        name: product['product']['name'],
        category: product['product']['category'],
        price: product['price']
      }))
    },
    getProduct(id) {
      this.$router.push({name: 'product', params: {id: id}})
    }
  },
  mounted() {
    this.fetchProducts();
  }
}
</script>

<style scoped>

</style>