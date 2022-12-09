import { createVuetify as createVuetifyBase } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'
import 'vuetify/styles'

const vuetify = createVuetifyBase({
  defaults: {
    VCard: {
      elevation: 0,
    },
    VAlert: {
      variant: 'outlined',
      density: 'compact',
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#121212',
          secondary: '#121212',
          background: '#ffffff',
          surface: '#ffffff',
          error: '#ff0000',
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#ffffff',
          secondary: '#ffffff',
          background: '#121212',
          surface: '#121212',
          error: '#ff0000',
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
})

export const createVuetify = () => vuetify
