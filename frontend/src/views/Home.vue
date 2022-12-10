<script setup lang="ts">
  import { ref } from 'vue'
  import { mdiThumbUp, mdiThumbDown, mdiShare } from '@mdi/js'
  import { getRelativeTime } from '../utils'
  import { useUser } from '../hooks'
  import CommentList from '../components/CommentList.vue'
  import DialogLogin from '../components/DialogLogin.vue'
  import VideosRecommand from '../components/VideosRecommand.vue'

  const { isLoggedIn } = useUser()
  const showLoginDialog = ref(false)
  const showLoginDialog2 = ref(false)

  const info = ref({
    title: '[5452] LEC-11 (20221121)',
    description: '',
    views: 283,
    likes: 3,
    dislikes: 0,
    comments: 2,
    published: '2022-11-15T00:00:00Z',
    channel: {
      name: 'Chung-Wei Lin',
      subscribers: 53,
    },
  })
</script>

<template>
  <v-main>
    <div class="video-container">
      <video controls />
      <!-- <video controls src="/assets/video.mp4" /> -->
    </div>
    <v-container style="padding-bottom: 1rem">
      <v-row>
        <v-col cols="12" md="8">
          <!-- video info -->
          <v-card class="video-info">
            <v-card-title class="h1">{{ info.title }}</v-card-title>
            <v-card-subtitle>{{ info.views }} views ‧ {{ getRelativeTime(info.published) }}</v-card-subtitle>
            <v-card-text v-if="info.description">
              {{ info.description }}
            </v-card-text>
            <dialog-login v-model="showLoginDialog" title="Login to like or dislike the video!" />
            <v-card-actions @click="isLoggedIn || (showLoginDialog = true)">
              <v-btn :prepend-icon="mdiThumbUp" variant="outlined" rounded="pill" :disabled="!isLoggedIn">
                {{ info.likes }}
                <v-tooltip activator="parent" location="bottom"> I like this </v-tooltip>
              </v-btn>
              <v-btn :prepend-icon="mdiThumbDown" variant="outlined" rounded="pill" :disabled="!isLoggedIn">
                {{ info.dislikes }}
                <v-tooltip activator="parent" location="bottom"> I dislike this </v-tooltip>
              </v-btn>
            </v-card-actions>
          </v-card>
          <v-divider />
          <!-- author info -->
          <v-card class="author-info">
            <dialog-login v-model="showLoginDialog2" title="Login to subscribe!" />
            <v-card-item>
              <template #prepend>
                <v-avatar size="36">
                  <v-img :src="`https://api.multiavatar.com/${info.channel.name}.svg`" />
                </v-avatar>
              </template>
              <v-list-item-title class="h2">{{ info.channel.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ info.channel.subscribers }} subscribers</v-list-item-subtitle>
              <template #append>
                <v-btn color="error" rounded="pill" @click="isLoggedIn || (showLoginDialog2 = true)"> Subscribe </v-btn>
              </template>
            </v-card-item>
          </v-card>
          <v-divider />
          <comment-list />
        </v-col>
        <v-col cols="12" md="4">
          <videos-recommand></videos-recommand>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>
  .video-container {
    width: 100%;
  }
  .video-container video {
    display: block; /* Remove extra space below video element */
    width: 100%;
    height: 100%;
    max-height: calc(100vh - 56px);
  }
  .v-container {
    padding: 0;
  }
  .v-row {
    margin: 0;
  }
  .v-col-12 {
    padding: 0;
  }
  .video-info {
    margin: 0.25rem 0;
  }
  .video-info .v-card-title {
    font-size: 1.2rem;
    font-weight: 600;
    padding-bottom: 0;
    line-height: 1.5rem;
  }
</style>

<style>
  .v-card-item .v-card-item__prepend {
    padding-right: 0.7rem;
  }
  /* vuetify not implement yet */
  .rounded-pill {
    border-radius: 50vh;
  }
  .v-btn__prepend {
    margin-left: 0.2rem;
  }
</style>
