<template>
  <section class="text-gray-400 bg-gray-900 body-font">
    <div class="container px-5 py-24 mx-auto flex flex-wrap items-center">
      <div class="lg:w-3/5 md:w-1/2 md:pr-16 lg:pr-0 pr-0">
        <h1 class="title-font font-medium text-3xl text-white">Slow-carb next level shoindxgoitch ethical authentic, poko scenester</h1>
        <p class="leading-relaxed mt-4">Poke slow-carb mixtape knausgaard, typewriter street art gentrify hammock starladder roathse. Craies vegan tousled etsy austin.</p>
      </div>
      <div class="lg:w-2/6 md:w-1/2 bg-gray-800 bg-opacity-50 rounded-lg p-8 flex flex-col md:ml-auto w-full mt-10 md:mt-0">
        <h2 class="text-white text-lg font-medium title-font mb-5">Sign Up</h2>
        <div class="relative mb-4">
          <label for="email" class="leading-7 text-sm text-gray-400">Email</label>
          <input v-model="login" type="email" id="email" name="email" class="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-indigo-900 rounded border border-gray-600 focus:border-indigo-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out">
        </div>
        <div class="relative mb-4">
          <label for="password" class="leading-7 text-sm text-gray-400">Password</label>
          <input v-model="password" type="password" id="password" name="password" class="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-indigo-900 rounded border border-gray-600 focus:border-indigo-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out">
        </div>
        <button @click="loginUser" class="text-white bg-indigo-500 border-0 py-2 px-8 focus:outline-none hover:bg-indigo-600 rounded text-lg">Войти</button>
        <p class="text-xs mt-3">Literally you probably haven't heard of them jean shorts.</p>
      </div>
    </div>
  </section>
</template>

<script>
import axios from "axios";

export default {
  name: "LoginView",
  data() {
    return {
      login: '',
      password: ''
    }
  },
  methods: {
    async loginUser() {
      axios.post('http://localhost:8000/api/v1/user/login', {
        email: this.login,
        password: this.password,
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log(response['data']['access']);
        document.cookie = `access=${response['data']['access']}`;
        document.cookie = `username=${this.login}`;
      })
      .catch(error => {
        console.log(error.response)
      });
    },
  },
}
</script>

<style scoped>

</style>