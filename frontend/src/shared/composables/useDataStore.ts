import { computed, reactive } from 'vue'
import { portfolioAPI, blogAPI, profileAPI } from '../api'
import { useErrorHandler } from './useErrorHandler'
import { useLoading } from './useLoading'
import type { Portfolio, Blog, Profile } from '../types'

// 数据缓存配置
interface CacheConfig {
  ttl: number // 缓存时间（毫秒）
  maxSize: number // 最大缓存条目数
}

// 缓存条目
interface CacheEntry<T> {
  data: T
  timestamp: number
  key: string
}

// 全局数据缓存管理器
class DataCacheManager {
  private cache = new Map<string, CacheEntry<any>>()
  private config: CacheConfig = {
    ttl: 5 * 60 * 1000, // 5分钟
    maxSize: 100
  }

  // 设置缓存
  set<T>(key: string, data: T): void {
    // 清理过期缓存
    this.cleanup()

    // 如果缓存已满，删除最旧的条目
    if (this.cache.size >= this.config.maxSize) {
      const oldestKey = Array.from(this.cache.keys())[0]
      this.cache.delete(oldestKey)
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      key
    })
  }

  // 获取缓存
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    // 检查是否过期
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.cache.delete(key)
      return null
    }

    return entry.data as T
  }

  // 删除缓存
  delete(key: string): void {
    this.cache.delete(key)
  }

  // 清空缓存
  clear(): void {
    this.cache.clear()
  }

  // 清理过期缓存
  private cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.config.ttl) {
        this.cache.delete(key)
      }
    }
  }

  // 获取缓存统计
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      ttl: this.config.ttl
    }
  }
}

const cacheManager = new DataCacheManager()

// 全局数据状态
interface DataState {
  portfolios: Portfolio[]
  blogs: Blog[]
  profile: Profile | null
  lastUpdated: {
    portfolios: number
    blogs: number
    profile: number
  }
  syncStatus: {
    portfolios: 'idle' | 'syncing' | 'error'
    blogs: 'idle' | 'syncing' | 'error'
    profile: 'idle' | 'syncing' | 'error'
  }
}

const globalState = reactive<DataState>({
  portfolios: [],
  blogs: [],
  profile: null,
  lastUpdated: {
    portfolios: 0,
    blogs: 0,
    profile: 0
  },
  syncStatus: {
    portfolios: 'idle',
    blogs: 'idle',
    profile: 'idle'
  }
})

// 数据同步间隔（毫秒）
const SYNC_INTERVAL = 30 * 1000 // 30秒

// 作品数据管理
export function usePortfolioStore() {
  const { handleError, safeExecute } = useErrorHandler()
  const { loading, withLoading } = useLoading('portfolio_store')

  // 获取所有作品
  const fetchPortfolios = async (forceRefresh = false): Promise<Portfolio[]> => {
    const cacheKey = 'portfolios_all'
    
    // 检查缓存
    if (!forceRefresh) {
      const cached = cacheManager.get<Portfolio[]>(cacheKey)
      if (cached) {
        globalState.portfolios = cached
        return cached
      }
    }

    globalState.syncStatus.portfolios = 'syncing'

    const result = await safeExecute(
      () => withLoading(async () => {
        const response = await portfolioAPI.getAll()
        return response.data
      }),
      [],
      (error) => {
        globalState.syncStatus.portfolios = 'error'
        handleError(error, 'network')
      }
    )

    if (result) {
      globalState.portfolios = result
      globalState.lastUpdated.portfolios = Date.now()
      globalState.syncStatus.portfolios = 'idle'
      
      // 缓存数据
      cacheManager.set(cacheKey, result)
      
      return result
    }

    return globalState.portfolios
  }

  // 获取单个作品
  const fetchPortfolio = async (id: number, forceRefresh = false): Promise<Portfolio | null> => {
    const cacheKey = `portfolio_${id}`
    
    // 检查缓存
    if (!forceRefresh) {
      const cached = cacheManager.get<Portfolio>(cacheKey)
      if (cached) return cached
    }

    const result = await safeExecute(
      async () => {
        const response = await portfolioAPI.getById(id)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 缓存数据
      cacheManager.set(cacheKey, result)
      
      // 更新全局状态中的对应项
      const index = globalState.portfolios.findIndex(p => p.id === id)
      if (index !== -1) {
        globalState.portfolios[index] = result
      }
      return result
    }

    return null
  }

  // 创建作品
  const createPortfolio = async (data: Omit<Portfolio, 'id' | 'created_at' | 'updated_at'>): Promise<Portfolio | null> => {
    const result = await safeExecute(
      async () => {
        const response = await portfolioAPI.create({
          ...data,
          display_order: data.display_order ?? 0
        })
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 更新全局状态
      globalState.portfolios.unshift(result)
      globalState.lastUpdated.portfolios = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('portfolios_all')
      return result
    }

    return null
  }

  // 更新作品
  const updatePortfolio = async (id: number, data: Partial<Portfolio>): Promise<Portfolio | null> => {
    const result = await safeExecute(
      async () => {
        const response = await portfolioAPI.update(id, data)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 更新全局状态
      const index = globalState.portfolios.findIndex(p => p.id === id)
      if (index !== -1) {
        globalState.portfolios[index] = result
      }
      globalState.lastUpdated.portfolios = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('portfolios_all')
      cacheManager.delete(`portfolio_${id}`)
      return result
    }

    return null
  }

  // 删除作品
  const deletePortfolio = async (id: number): Promise<boolean> => {
    const success = await safeExecute(
      async () => {
        await portfolioAPI.delete(id)
        return true
      },
      false,
      (error) => handleError(error, 'network')
    )

    if (success) {
      // 更新全局状态
      const index = globalState.portfolios.findIndex(p => p.id === id)
      if (index !== -1) {
        globalState.portfolios.splice(index, 1)
      }
      globalState.lastUpdated.portfolios = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('portfolios_all')
      cacheManager.delete(`portfolio_${id}`)
      return true
    }

    return false
  }

  // 计算属性
  const featuredPortfolios = computed(() => 
    globalState.portfolios
      .filter(p => p.is_featured)
      .sort((a, b) => (b.display_order ?? 0) - (a.display_order ?? 0))
  )

  const publishedPortfolios = computed(() => 
    globalState.portfolios
      .sort((a, b) => (b.display_order ?? 0) - (a.display_order ?? 0))
  )

  return {
    // 状态
    portfolios: computed(() => globalState.portfolios),
    featuredPortfolios,
    publishedPortfolios,
    loading,
    syncStatus: computed(() => globalState.syncStatus.portfolios),
    lastUpdated: computed(() => globalState.lastUpdated.portfolios),

    // 方法
    fetchPortfolios,
    fetchPortfolio,
    createPortfolio,
    updatePortfolio,
    deletePortfolio,

    // 工具方法
    refreshPortfolios: () => fetchPortfolios(true),
    getPortfolioById: (id: number) => globalState.portfolios.find(p => p.id === id)
  }
}

// 博客数据管理
export function useBlogStore() {
  const { handleError, safeExecute } = useErrorHandler()
  const { loading, withLoading } = useLoading('blog_store')

  // 获取所有博客
  const fetchBlogs = async (forceRefresh = false, includeUnpublished = false): Promise<Blog[]> => {
    const cacheKey = includeUnpublished ? 'blogs_all_admin' : 'blogs_all'
    
    // 检查缓存
    if (!forceRefresh) {
      const cached = cacheManager.get<Blog[]>(cacheKey)
      if (cached) {
        globalState.blogs = cached
        return cached
      }
    }

    globalState.syncStatus.blogs = 'syncing'

    const result = await safeExecute(
      () => withLoading(async () => {
        const response = includeUnpublished 
          ? await blogAPI.getAllAdmin()
          : await blogAPI.getAll()
        return response.data
      }),
      [],
      (error) => {
        globalState.syncStatus.blogs = 'error'
        handleError(error, 'network')
      }
    )

    if (result) {
      globalState.blogs = result
      globalState.lastUpdated.blogs = Date.now()
      globalState.syncStatus.blogs = 'idle'
      
      // 缓存数据
      cacheManager.set(cacheKey, result)
      
      return result
    }

    return globalState.blogs
  }

  // 获取单个博客
  const fetchBlog = async (id: number, forceRefresh = false): Promise<Blog | null> => {
    const cacheKey = `blog_${id}`
    
    // 检查缓存
    if (!forceRefresh) {
      const cached = cacheManager.get<Blog>(cacheKey)
      if (cached) return cached
    }

    const result = await safeExecute(
      async () => {
        const response = await blogAPI.getById(id)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 缓存数据
      cacheManager.set(cacheKey, result)
      
      // 更新全局状态中的对应项
      const index = globalState.blogs.findIndex(b => b.id === id)
      if (index !== -1) {
        globalState.blogs[index] = result
      }
      return result
    }

    return null
  }

  // 创建博客
  const createBlog = async (data: Omit<Blog, 'id' | 'created_at' | 'updated_at'>): Promise<Blog | null> => {
    const result = await safeExecute(
      async () => {
        const response = await blogAPI.create(data)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 更新全局状态
      globalState.blogs.unshift(result)
      globalState.lastUpdated.blogs = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('blogs_all')
      cacheManager.delete('blogs_all_admin')
      return result
    }

    return null
  }

  // 更新博客
  const updateBlog = async (id: number, data: Partial<Blog>): Promise<Blog | null> => {
    const result = await safeExecute(
      async () => {
        const response = await blogAPI.update(id, data)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 更新全局状态
      const index = globalState.blogs.findIndex(b => b.id === id)
      if (index !== -1) {
        globalState.blogs[index] = result
      }
      globalState.lastUpdated.blogs = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('blogs_all')
      cacheManager.delete('blogs_all_admin')
      cacheManager.delete(`blog_${id}`)
      return result
    }

    return null
  }

  // 删除博客
  const deleteBlog = async (id: number): Promise<boolean> => {
    const success = await safeExecute(
      async () => {
        await blogAPI.delete(id)
        return true
      },
      false,
      (error) => handleError(error, 'network')
    )

    if (success) {
      // 更新全局状态
      const index = globalState.blogs.findIndex(b => b.id === id)
      if (index !== -1) {
        globalState.blogs.splice(index, 1)
      }
      globalState.lastUpdated.blogs = Date.now()
      
      // 清除相关缓存
      cacheManager.delete('blogs_all')
      cacheManager.delete('blogs_all_admin')
      cacheManager.delete(`blog_${id}`)
      return true
    }

    return false
  }

  // 计算属性
  const publishedBlogs = computed(() => 
    globalState.blogs
      .filter(b => b.is_published)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  )

  const recentBlogs = computed(() => 
    publishedBlogs.value.slice(0, 5)
  )

  return {
    // 状态
    blogs: computed(() => globalState.blogs),
    publishedBlogs,
    recentBlogs,
    loading,
    syncStatus: computed(() => globalState.syncStatus.blogs),
    lastUpdated: computed(() => globalState.lastUpdated.blogs),

    // 方法
    fetchBlogs,
    fetchBlog,
    createBlog,
    updateBlog,
    deleteBlog,

    // 工具方法
    refreshBlogs: () => fetchBlogs(true),
    getBlogById: (id: number) => globalState.blogs.find(b => b.id === id)
  }
}

// 个人信息数据管理
export function useProfileStore() {
  const { handleError, safeExecute } = useErrorHandler()
  const { loading, withLoading } = useLoading('profile_store')

  // 获取个人信息
  const fetchProfile = async (forceRefresh = false): Promise<Profile | null> => {
    const cacheKey = 'profile'
    
    // 检查缓存
    if (!forceRefresh) {
      const cached = cacheManager.get<Profile>(cacheKey)
      if (cached) {
        globalState.profile = cached
        return cached
      }
    }

    globalState.syncStatus.profile = 'syncing'

    const result = await safeExecute(
      () => withLoading(async () => {
        const response = await profileAPI.get()
        return response.data
      }),
      null,
      (error) => {
        globalState.syncStatus.profile = 'error'
        handleError(error, 'network')
      }
    )

    if (result) {
      globalState.profile = result
      globalState.lastUpdated.profile = Date.now()
      globalState.syncStatus.profile = 'idle'
      
      // 缓存数据
      cacheManager.set(cacheKey, result)
      
      return result
    }

    return globalState.profile
  }

  // 更新个人信息
  const updateProfile = async (data: Partial<Profile>): Promise<Profile | null> => {
    const result = await safeExecute(
      async () => {
        const response = await profileAPI.update(data)
        return response.data
      },
      null,
      (error) => handleError(error, 'network')
    )

    if (result) {
      // 更新全局状态
      globalState.profile = result
      globalState.lastUpdated.profile = Date.now()
      
      // 清除缓存
      cacheManager.delete('profile')
      return result
    }

    return null
  }

  return {
    // 状态
    profile: computed(() => globalState.profile),
    loading,
    syncStatus: computed(() => globalState.syncStatus.profile),
    lastUpdated: computed(() => globalState.lastUpdated.profile),

    // 方法
    fetchProfile,
    updateProfile,

    // 工具方法
    refreshProfile: () => fetchProfile(true)
  }
}

// 全局数据同步
export function useDataSync() {
  const portfolioStore = usePortfolioStore()
  const blogStore = useBlogStore()
  const profileStore = useProfileStore()

  let syncInterval: NodeJS.Timeout | null = null

  // 启动自动同步
  const startAutoSync = () => {
    if (syncInterval) return

    syncInterval = setInterval(async () => {
      // 只在数据较旧时才同步
      const now = Date.now()
      
      if (now - globalState.lastUpdated.portfolios > SYNC_INTERVAL) {
        await portfolioStore.fetchPortfolios()
      }
      
      if (now - globalState.lastUpdated.blogs > SYNC_INTERVAL) {
        await blogStore.fetchBlogs()
      }
      
      if (now - globalState.lastUpdated.profile > SYNC_INTERVAL) {
        await profileStore.fetchProfile()
      }
    }, SYNC_INTERVAL)
  }

  // 停止自动同步
  const stopAutoSync = () => {
    if (syncInterval) {
      clearInterval(syncInterval)
      syncInterval = null
    }
  }

  // 手动同步所有数据
  const syncAll = async () => {
    await Promise.all([
      portfolioStore.refreshPortfolios(),
      blogStore.refreshBlogs(),
      profileStore.refreshProfile()
    ])
  }

  // 清除所有缓存
  const clearCache = () => {
    cacheManager.clear()
  }

  // 获取同步状态
  const syncStatus = computed(() => ({
    portfolios: globalState.syncStatus.portfolios,
    blogs: globalState.syncStatus.blogs,
    profile: globalState.syncStatus.profile,
    isAnySyncing: Object.values(globalState.syncStatus).some(status => status === 'syncing'),
    hasAnyError: Object.values(globalState.syncStatus).some(status => status === 'error')
  }))

  return {
    // 状态
    syncStatus,
    lastUpdated: computed(() => globalState.lastUpdated),
    cacheStats: computed(() => cacheManager.getStats()),

    // 方法
    startAutoSync,
    stopAutoSync,
    syncAll,
    clearCache,

    // 存储访问
    portfolioStore,
    blogStore,
    profileStore
  }
}

export default {
  usePortfolioStore,
  useBlogStore,
  useProfileStore,
  useDataSync
}