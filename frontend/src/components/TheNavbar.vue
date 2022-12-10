<script setup lang="ts">
  import { mdiBrightness2, mdiWhiteBalanceSunny, mdiAccountCircle } from '@mdi/js'
  import { useLogout, useMyTheme, useUser } from '../hooks'

  const { mode, nextMode } = useMyTheme()
  const { profile, isLoggedIn } = useUser()
  const { execute: logout } = useLogout()
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
      <v-tooltip activator="parent" location="bottom"> Toggle light/dark theme </v-tooltip>
    </v-btn>
    <v-btn v-if="isLoggedIn" icon size="small" aria-label="Logout" @click="logout()">
      <v-avatar size="small">
        <v-img :src="`https://api.multiavatar.com/${profile.name}.svg`" />
      </v-avatar>
      <v-tooltip activator="parent" location="bottom" scrim> {{ profile.name }}, Click to logout </v-tooltip>
    </v-btn>
    <v-btn v-else icon size="small" aria-label="Login" to="/login">
      <v-icon size="large">
        {{ mdiAccountCircle }}
      </v-icon>
      <v-tooltip activator="parent" location="bottom" scrim> Login </v-tooltip>
    </v-btn>
  </v-app-bar>
</template>
