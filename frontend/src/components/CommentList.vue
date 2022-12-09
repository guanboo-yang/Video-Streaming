<script setup lang="ts">
  import { useFetch } from '@vueuse/core'
  import { onBeforeUnmount } from 'vue'
  import { getRelativeTime } from '../utils'
  import CommentInput from './CommentInput.vue'

  const {
    isFetching,
    error,
    data: comments,
    canAbort,
    abort,
  } = useFetch(() => import.meta.env.VITE_API_URL + 'comment', {
    afterFetch: async ({ data, response }) => {
      if (response.ok) {
        // wait for 1 second
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      return { data: data.data, response }
    },
  }).json<
    {
      name: string
      time: string
      comment: string
    }[]
  >()

  const addComment = (name: string, comment: string) => {
    comments.value = [
      {
        name: name,
        time: new Date().toISOString(),
        comment,
      },
      ...(comments.value || []),
    ]
  }

  onBeforeUnmount(() => canAbort && abort())
</script>

<template>
  <v-card>
    <v-card-title class="h2"> {{ comments ? comments.length : 0 }} Comments</v-card-title>
  </v-card>
  <comment-input :comment-number="comments ? comments.length : 0" :add-comment="addComment" />
  <!-- is fetching -->
  <v-progress-linear v-if="isFetching" indeterminate />
  <!-- error -->
  <v-alert v-else-if="error" type="error">
    {{ error }}
  </v-alert>
  <!-- no comments -->
  <v-card v-else-if="!comments || !comments.length" style="text-align: center">
    <v-card-text>No comments yet</v-card-text>
  </v-card>
  <!-- comments -->
  <v-list v-else :lines="false">
    <v-list-item v-for="(comment, idx) in comments" :key="idx" class="comments">
      <template #prepend>
        <v-avatar size="32">
          <v-img :src="`https://api.multiavatar.com/${comment.name}.svg`" />
        </v-avatar>
      </template>
      <v-list-item-title>
        {{ comment.name }}
        <span class="time">{{ getRelativeTime(comment.time) }}</span>
      </v-list-item-title>
      <v-list-item-subtitle>{{ comment.comment }}</v-list-item-subtitle>
    </v-list-item>
  </v-list>
</template>

<style scoped>
  .v-card-title {
    font-size: 1.1rem;
    font-weight: 600;
    padding-bottom: 0;
  }
  .time {
    font-size: 0.8rem;
    opacity: var(--v-medium-emphasis-opacity);
    margin-left: 0.1rem;
  }
  .v-list {
    padding-top: 0;
  }
  :deep(.v-list-item__prepend) {
    align-self: flex-start;
  }
  :deep(.v-list-item__prepend) .v-avatar {
    margin-right: 0.8rem;
  }
  .v-list-item-subtitle {
    font-size: 1rem;
    line-height: 1.35rem;
    opacity: 1;
  }
</style>
