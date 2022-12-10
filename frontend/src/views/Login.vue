<script setup lang="ts">
  import { useLogin } from '../hooks'
  const { method, input, isFetching, error, data, execute } = useLogin()
</script>

<template>
  <v-main>
    <v-card>
      <v-tabs v-model="method" centered fixed-tabs>
        <v-tab value="login">Login</v-tab>
        <v-tab value="register">Register</v-tab>
      </v-tabs>
      <v-card-text>
        <v-form @submit.prevent="execute()" style="gap: 1rem">
          <v-text-field v-model="input.name" placeholder="Username" variant="outlined" density="comfortable" hide-details autocomplete="username" />
          <v-text-field v-model="input.pass" placeholder="Password" variant="outlined" density="comfortable" hide-details type="password" autocomplete="current-password" />
          <v-expand-transition>
            <v-alert v-if="error || (data && !data.success)" type="error" style="width: 280px">{{ data.data }}</v-alert>
          </v-expand-transition>
          <div style="display: flex; justify-content: center; gap: 0.8rem">
            <v-btn type="submit" variant="outlined" color="error" :loading="isFetching" :disabled="!input.name || !input.pass">{{ method }}</v-btn>
            <v-btn type="reset" variant="outlined" :disabled="(!input.name && !input.pass) || isFetching">Reset</v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-main>
</template>

<style scoped>
  .v-card {
    margin: 0 auto;
    padding-top: 1rem;
    width: 320px;
  }
  .v-form {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  .v-text-field {
    max-width: 280px;
    width: 100%;
  }
</style>
