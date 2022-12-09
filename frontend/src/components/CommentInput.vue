<script setup lang="ts">
  import { mdiAccountCircle } from '@mdi/js'
  import { useFetch } from '@vueuse/core'
  import { onBeforeUnmount, ref } from 'vue'
  import { useUser } from '../hooks'
  import DialogLogin from './DialogLogin.vue'

  const props = defineProps<{
    commentNumber: number
    addComment: (name: string, comment: string) => void
  }>()

  const { profile, isLoggedIn } = useUser()
  const comment = ref('')
  const showLoginDialog = ref(false)

  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    () => import.meta.env.VITE_API_URL + 'comment',
    { method: 'POST', credentials: 'include' },
    {
      immediate: false,
      beforeFetch: ({ url, options, cancel }) => {
        options.body = JSON.stringify({
          user: profile.value.name,
          comment: comment.value,
        })
        return { url, options, cancel }
      },
      afterFetch: ({ data, response }) => {
        if (response.ok) {
          // Post comment success
          // add comment to list locally
          props.addComment(profile.value.name, comment.value)
          comment.value = ''
        }
        return { data, response }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
</script>

<template>
  <v-card class="comment">
    <dialog-login v-model="showLoginDialog" title="Login to comment!" />
    <!-- comment input -->
    <v-card-item style="align-items: start" @click="isLoggedIn || (showLoginDialog = true)">
      <template #prepend>
        <v-avatar size="36">
          <v-img v-if="isLoggedIn" :src="`https://api.multiavatar.com/${profile.name}.svg`" />
          <v-icon v-else size="36">
            {{ mdiAccountCircle }}
          </v-icon>
          <!-- <v-img src="https://scontent-tpe1-1.xx.fbcdn.net/v/t1.6435-1/50471991_1091733717672331_3849771090838552576_n.jpg?stp=dst-jpg_p200x200&_nc_cat=105&ccb=1-7&_nc_sid=7206a8&_nc_ohc=yzY_ncKKigYAX-EcvvX&_nc_ht=scontent-tpe1-1.xx&oh=00_AfB4IK4gKMPRsiy8h2XX86qXydHLNn1UOm-3pZkxB2DLfA&oe=63B8E5EE" /> -->
        </v-avatar>
      </template>
      <v-textarea
        v-model="comment"
        variant="underlined"
        density="compact"
        placeholder="Add a public comment..."
        rows="1"
        no-resize
        single-line
        hide-details
        auto-grow
        :disabled="!isLoggedIn" />
      <v-expand-transition>
        <div v-if="comment" style="display: flex; gap: 0.5rem; margin-top: 0.6rem">
          <v-btn size="small" variant="tonal" @click="execute" :loading="isFetching" :disabled="!comment">Comment</v-btn>
          <v-btn size="small" variant="text" @click="comment = ''" :disabled="!comment || isFetching">Cancel</v-btn>
        </div>
      </v-expand-transition>
      <v-expand-transition>
        <v-sheet v-if="error && comment" style="color: red; padding-top: 0.2rem">
          {{ data.data }}
        </v-sheet>
      </v-expand-transition>
    </v-card-item>
  </v-card>
</template>

<style scoped>
  .v-card-actions {
    padding: 0.5rem 1rem;
  }
  .v-textarea {
    margin-top: -0.8rem;
  }
  .v-textarea :deep(textarea) {
    padding-bottom: 0.35rem;
    mask-image: none;
    -webkit-mask-image: none;
    font-size: 1rem;
  }
</style>
