<script setup lang="ts">
  import { onBeforeUnmount, reactive, ref } from 'vue'
  import { useFetch } from '@vueuse/core'
  import { useRouter } from 'vue-router'
  import { useUser } from '../hooks'

  const tab = ref('Login')
  const input = reactive({ name: '', pass: '' })
  const router = useRouter()
  const { login } = useUser()

  // use useFetch to login or register
  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    () => import.meta.env.VITE_API_URL + tab.value.toLowerCase(),
    { method: 'POST', credentials: 'include' },
    {
      immediate: false,
      beforeFetch: ({ url, options, cancel }) => {
        options.body = JSON.stringify(input)
        return { url, options, cancel }
      },
      afterFetch: ({ data, response }) => {
        if (response.ok) {
          if (tab.value === 'Register') tab.value = 'Login'
          else {
            // Login success
            router.push({ name: 'Home' })
            login({ name: input.name })
          }
        }
        return { data, response }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
</script>

<template>
  <v-main>
    <v-card>
      <v-tabs v-model="tab" centered fixed-tabs>
        <v-tab value="Login">Login</v-tab>
        <v-tab value="Register">Register</v-tab>
      </v-tabs>
      <v-card-text>
        <v-form @submit.prevent="execute()" style="gap: 1rem">
          <v-text-field v-model="input.name" placeholder="Username" variant="outlined" density="comfortable" hide-details autocomplete="username" />
          <v-text-field v-model="input.pass" placeholder="Password" variant="outlined" density="comfortable" hide-details type="password" autocomplete="current-password" />
          <v-expand-transition>
            <v-alert v-if="error || (data && !data.success)" type="error" style="width: 280px">{{ data.data }}</v-alert>
          </v-expand-transition>
          <div style="display: flex; justify-content: center; gap: 0.8rem">
            <v-btn type="submit" variant="outlined" color="error" :loading="isFetching" :disabled="!input.name || !input.pass">{{ tab }}</v-btn>
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
