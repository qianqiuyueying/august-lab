// 共享类型定义

export interface Portfolio {
  id: number
  title: string
  description?: string
  content?: string
  tech_stack: string[]
  project_url?: string
  github_url?: string
  image_url?: string
  development_timeline?: Array<{ date: string; description: string }>
  display_order?: number
  sort_order?: number
  is_featured: boolean
  created_at: string
  updated_at: string
}

export interface Blog {
  id: number
  title: string
  content: string
  excerpt?: string
  summary?: string
  tags: string[]
  is_published: boolean
  published_at?: string
  cover_image?: string
  reading_time?: number
  sort_order?: number
  seo_title?: string
  seo_description?: string
  seo_keywords?: string
  created_at: string
  updated_at: string
}

export interface Profile {
  id: number
  name: string
  title: string
  bio: string
  avatar_url?: string
  email?: string
  phone?: string
  location?: string
  github_url?: string
  linkedin_url?: string
  twitter_url?: string
  website_url?: string
  skills: Skill[]
  created_at: string
  updated_at: string
}

export interface Skill {
  name: string
  category: string
  level: number
  description?: string
}

export interface Product {
  id: number
  title: string
  description?: string
  tech_stack?: string[]
  product_type: 'static' | 'spa' | 'game' | 'tool'
  entry_file: string
  file_path?: string
  preview_image?: string
  project_url?: string
  github_url?: string
  config_data?: Record<string, any>
  is_published: boolean
  is_featured: boolean
  display_order: number
  version: string
  view_count?: number
  created_at: string
  updated_at: string
}

export interface ProductStats {
  id: number
  product_id: number
  visitor_ip?: string
  session_id?: string
  access_time: string
  duration_seconds: number
  user_agent?: string
  referrer?: string
}

export interface ProductLog {
  id: number
  product_id: number
  log_type: 'access' | 'error' | 'performance' | 'security'
  log_level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  details?: Record<string, any>
  timestamp: string
}

export interface ProductAnalytics {
  product_id: number
  total_visits: number
  unique_visitors: number
  average_duration: number
  last_access?: string
  popular_times: Array<Record<string, any>>
}

export interface ProductUploadResponse {
  message: string
  product_id: number
  file_path: string
  extracted_files: string[]
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface MessageResponse {
  message: string
}

export interface APIError {
  error: {
    code: string
    message: string
    timestamp: string
    error_id: string
  }
}

// 表单数据类型
export type PortfolioCreateData = Omit<Portfolio, 'id' | 'created_at' | 'updated_at'>
export type PortfolioUpdateData = Partial<PortfolioCreateData>

export type BlogCreateData = Omit<Blog, 'id' | 'created_at' | 'updated_at'>
export type BlogUpdateData = Partial<BlogCreateData>

export type ProfileUpdateData = Partial<Omit<Profile, 'id' | 'created_at' | 'updated_at'>>

export type ProductCreateData = Omit<Product, 'id' | 'file_path' | 'created_at' | 'updated_at'>
export type ProductUpdateData = Partial<ProductCreateData>

export type ProductStatsCreateData = Omit<ProductStats, 'id' | 'access_time'>
export type ProductLogCreateData = Omit<ProductLog, 'id' | 'timestamp'>

// 分页参数
export interface PaginationParams {
  skip?: number
  limit?: number
  search?: string
}

// 上传文件响应
export interface UploadResponse {
  message: string
  filename: string
  url: string
  size: number
}

// 监控相关类型
export interface ProductError {
  id: string
  product_id: number
  log_type: string
  log_level: string
  message: string
  details?: any
  timestamp: string
}

export interface ProductPerformanceLog {
  id: string
  product_id: number
  log_type: string
  message: string
  details?: {
    loadTime?: number
    renderTime?: number
    memoryUsage?: number
    errorCount?: number
  }
  timestamp: string
}

export interface DiagnosticResult {
  product_id: number
  timestamp: string
  overall_status: 'good' | 'warning' | 'critical'
  checks: {
    file_integrity: boolean
    entry_file_exists: boolean
    config_valid: boolean
    published_status: boolean
  }
  recommendations: string[]
}

export interface SystemStatus {
  timestamp: string
  overall_status: 'good' | 'warning' | 'critical'
  metrics: {
    total_products: number
    published_products: number
    error_rate: number
    recent_errors: number
  }
  storage: {
    total_size: number
    used_size: number
    available_size: number
  }
}

export interface MonitoringAlert {
  id: string
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  productId?: number
}

// 反馈相关类型
export interface ProductFeedback {
  id: number
  product_id: number
  user_name?: string
  user_email?: string
  feedback_type: 'bug' | 'feature' | 'improvement' | 'general'
  rating?: number
  title: string
  content: string
  status: 'pending' | 'reviewed' | 'resolved' | 'closed'
  admin_reply?: string
  user_agent?: string
  ip_address?: string
  created_at: string
  updated_at: string
  replied_at?: string
}

export interface ProductFeedbackStats {
  product_id: number
  total_feedback: number
  average_rating?: number
  feedback_by_type: Record<string, number>
  feedback_by_status: Record<string, number>
  recent_feedback: ProductFeedback[]
}

export interface FeedbackCreateData {
  product_id: number
  user_name?: string
  user_email?: string
  feedback_type: string
  rating?: number
  title: string
  content: string
}

export interface FeedbackUpdateData {
  status?: string
  admin_reply?: string
}