<script setup lang="ts">
  import { mdiBrightness2, mdiWhiteBalanceSunny, mdiAccountCircle } from '@mdi/js'
  import { useFetch } from '@vueuse/core'
  import { onBeforeUnmount } from 'vue'
  // import { RouteRecordRaw, useRouter } from 'vue-router'
  import { useMyTheme, useUser } from '../hooks'

  // const router = useRouter()
  const { mode, nextMode } = useMyTheme()
  const { profile, isLoggedIn, logout } = useUser()

  // const routes = router.getRoutes().filter((route: RouteRecordRaw) => route.meta?.icon)

  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    () => import.meta.env.VITE_API_URL + 'logout',
    { method: 'POST', credentials: 'include' },
    {
      immediate: false,
      afterFetch: ({ data, response }) => {
        if (response.ok) {
          // Logout success
          logout()
        }
        return { data, response }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
</script>

<template>
  <v-app-bar color="background" density="comfortable" location="top" flat>
    <router-link to="/" style="width: 100px; margin-left: 16px">
      <v-img :src="mode === 'light' ? '/assets/timtube.svg' : '/assets/timtube_dark.svg'" alt="TimTube logo" max-width="100" />
    </router-link>
    <v-spacer style="flex-grow: 2" />
    <v-btn icon size="small" aria-label="Toggle light/dark theme" @click="nextMode()">
      <v-icon size="large">
        {{ mode === 'light' ? mdiBrightness2 : mdiWhiteBalanceSunny }}
      </v-icon>
    </v-btn>
    <v-btn v-if="isLoggedIn" icon size="small" aria-label="Logout" @click="execute()">
      <v-avatar size="small">
        <v-img :src="`https://api.multiavatar.com/${profile.name}.svg`" />
      </v-avatar>
    </v-btn>
    <v-btn v-else icon size="small" aria-label="Login" to="/login">
      <v-icon size="large">
        {{ mdiAccountCircle }}
      </v-icon>
    </v-btn>
  </v-app-bar>
</template>

<!-- <v-bottom-navigation bgColor="primary" mandatory grow class="elevation-24">
  <v-btn v-for="link in routes" :key="link.name" :to="{ name: link.name }">
    <v-icon size="large">{{ link.meta?.icon }}</v-icon>
    <span style="margin-top: 2px; text-transform: uppercase">
      {{ link.name }}
    </span>
  </v-btn>
</v-bottom-navigation> -->

<style scoped lang="scss">
  // .v-bottom-navigation .v-btn {
  //   &.v-btn--active :deep(.v-btn__overlay) {
  //     background: transparent !important;
  //   }
  //   &:not(.v-btn--active) {
  //     opacity: 0.6;
  //   }
  // }
</style>
