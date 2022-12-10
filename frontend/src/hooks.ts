import { createGlobalState, useColorMode, useCycleList, useFetch } from '@vueuse/core'
import { useTheme } from 'vuetify'
import { onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

export const useMyTheme = createGlobalState(() => {
  const theme = useTheme()
  const mode = useColorMode({ storageKey: 'color-mode' })
  const { next: nextMode } = useCycleList(['dark', 'light'], { initialValue: mode })

  watch(
    mode,
    newVal => {
      theme.global.name.value = newVal
      if (!document.querySelector('meta[name="theme-color"]')) {
        const meta = document.createElement('meta')
        meta.name = 'theme-color'
        document.head.appendChild(meta)
      }
      document.querySelector('meta[name="theme-color"]')!.setAttribute('content', theme.current.value.colors.background)
    },
    { immediate: true }
  )

  return { mode, nextMode }
})

export const useUser = createGlobalState(() => {
  const isLoggedIn = ref(false)
  const profile = ref({ name: '' })

  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    import.meta.env.VITE_API_URL + '/profile',
    { method: 'GET', credentials: 'include' },
    {
      initialData: { name: 'Guest' },
      afterFetch: ({ data, response }) => {
        if (response.ok) {
          if (data.success) {
            isLoggedIn.value = true
            profile.value = data.data
          } else {
            isLoggedIn.value = false
            profile.value = { name: 'Guest' }
          }
        }
        return { data, response }
      },
      onFetchError: ({ data, response, error }) => {
        isLoggedIn.value = false
        profile.value = { name: 'Guest' }
        return { data, response, error }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
  return { profile, refetch: execute, isLoggedIn, isFetching, error }
})

export const useLogin = () => {
  const router = useRouter()
  const { refetch } = useUser()
  const method = ref('login')
  const config = reactive({ name: '', pass: '' })

  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    () => import.meta.env.VITE_API_URL + '/' + method.value,
    { method: 'POST', credentials: 'include' },
    {
      immediate: false,
      beforeFetch: ({ url, options, cancel }) => {
        if (!config.name || !config.pass) cancel()
        options.body = JSON.stringify(config)
        return { url, options, cancel }
      },
      afterFetch: async ({ data, response }) => {
        if (response.ok) {
          if (method.value === 'register') method.value = 'login'
          else {
            // Login success, refetch user profile
            await refetch()
            router.push({ name: 'Home' })
          }
        }
        return { data, response }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
  return { method, input: config, isFetching, error, data, execute }
}

export const useLogout = () => {
  const { refetch } = useUser()

  const { isFetching, error, data, execute, canAbort, abort } = useFetch(
    () => import.meta.env.VITE_API_URL + '/logout',
    { method: 'POST', credentials: 'include' },
    {
      immediate: false,
      afterFetch: async ({ data, response }) => {
        if (response.ok) {
          // Logout success, refetch user profile
          await refetch()
        }
        return { data, response }
      },
    }
  ).json()

  onBeforeUnmount(() => canAbort && abort())
  return { isFetching, error, data, execute }
}
