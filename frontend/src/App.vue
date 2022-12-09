<script setup lang="ts">
  import TheNavbar from './components/TheNavbar.vue'
</script>

<template>
  <v-app>
    <the-navbar />
    <router-view v-slot="{ Component }">
      <v-fade-transition mode="out-in">
        <component :is="Component" />
      </v-fade-transition>
    </router-view>
  </v-app>
</template>

<style>
  /* style selected text */
  ::selection {
    background-color: #ccc;
    color: #000;
  }
  /* in dark mode */
  .dark ::selection {
    background-color: #555;
    color: #fff;
  }
  /* remove v-card-background transition */
  .v-card {
    transition-property: box-shadow, opacity !important;
  }
</style>
