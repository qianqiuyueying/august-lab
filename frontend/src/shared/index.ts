// Types (export first to avoid conflicts)
export * from './types'

// API (explicit exports to avoid type conflicts)
export {
  portfolioAPI,
  blogAPI,
  profileAPI,
  authAPI,
  uploadAPI,
  productAPI
} from './api'
export { default as api } from './api'

// Utils
export * from './utils'

// Composables
export { useAuth } from './composables/useAuth'
export { useApi, useApiList, useApiMutation } from './composables/useApi'
export { useNotification } from './composables/useNotification'

// Components
export { default as LoadingSpinner } from './components/LoadingSpinner.vue'
export { default as EmptyState } from './components/EmptyState.vue'
export { default as ErrorMessage } from './components/ErrorMessage.vue'