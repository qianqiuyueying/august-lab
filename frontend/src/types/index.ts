export interface User {
  id: number;
  username: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface Article {
  id: number;
  slug: string;
  title: string;
  content: string;
  summary: string;
  cover_image?: string | null;
  status: string;
  tags: Tag[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ArticleListItem {
  id: number;
  slug: string;
  title: string;
  summary: string;
  cover_image?: string | null;
  status: string;
  tags: Tag[];
  created_at: string | null;
}

export interface ArticleListResponse {
  items: ArticleListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AboutPage {
  id: number;
  eyebrow?: string | null;
  title?: string | null;
  avatar_url?: string | null;
  hero_subtitle?: string | null;
  cover_image?: string | null;
  content?: string | null;
  content_type?: string | null;
  tech_stack?: string | null;
  info_cards?: Array<{ label: string; value: string }>;
  contacts?: Array<{ platform: string; url: string; name?: string }>;
  updated_at?: string | null;
}

export interface Product {
  id: number;
  slug: string;
  title: string;
  description: string;
  cover_image?: string | null;
  runtime_url?: string | null;
  status: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

export interface Asset {
  id: number;
  filename: string;
  original_name: string;
  url: string;
  mime_type: string;
  size: number;
  kind: 'image';
  created_at: string | null;
}

export interface AssetListResponse {
  items: Asset[];
  total: number;
  page: number;
  page_size: number;
}

// 看板娘设置（公开字段）
export interface MascotSettings {
  persona: string;
  api_base_url: string;
  model: string;
  temperature: number;
  max_tokens: number;
  enabled: boolean;
  mascot_visible: boolean;
  mascot_scale: number;
  mascot_position_x: number | null;
  mascot_position_y: number | null;
  show_on_mobile: boolean;
  greeting_enabled: boolean;
  greeting_delay_seconds: number;
  random_action_interval: number;
  context_aware: boolean;
  drag_enabled: boolean;
}

// 管理后台完整设置（含 api_key）
export interface MascotSettingsAdmin extends MascotSettings {
  id: number;
  api_key: string;
}
