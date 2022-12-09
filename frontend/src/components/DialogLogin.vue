<!-- a login dialog -->

<script setup lang="ts">
  // v-model

  import { computed } from 'vue'

  const props = defineProps<{
    modelValue: boolean
    title: string
  }>()

  const emits = defineEmits(['update:modelValue'])

  const show = computed({
    get: () => props.modelValue,
    set: value => emits('update:modelValue', value),
  })
</script>

<template>
  <v-dialog v-model="show" width="fit-content">
    <v-card>
      <v-card-title>{{ title }}</v-card-title>
      <v-card-actions>
        <v-btn variant="outlined" to="/login">Login</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
  .v-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0.2rem;
  }
  .v-card-actions {
    padding: 1rem 0;
  }
  /* change dialog backdrop color to black */
  :deep(.v-overlay__scrim) {
    background: #000;
  }
</style>
