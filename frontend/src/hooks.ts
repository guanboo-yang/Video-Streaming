import { createGlobalState, useColorMode, useCycleList } from '@vueuse/core'
import { useTheme } from 'vuetify'
import { ref, watch } from 'vue'

export const useMyTheme = createGlobalState(() => {
  const theme = useTheme()
  const mode = useColorMode({
    storageKey: 'color-mode',
  })
  const { next: nextMode } = useCycleList(['dark', 'light'], {
    initialValue: mode,
  })
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

  const profile = ref({
    name: '',
  })

  const login = (config: { name: string }) => {
    isLoggedIn.value = true
    profile.value = config
  }

  const logout = () => {
    isLoggedIn.value = false
    profile.value = { name: '' }
  }

  return { profile, isLoggedIn, login, logout }
})
