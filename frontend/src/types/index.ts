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
  eyebrow: string;
  title: string;
  avatar_url: string;
  hero_subtitle: string;
  cover_image: string;
  content: string;
  content_type: string;
  tech_stack: string;
  info_cards: Array<{ label: string; value: string }>;
  contacts: Array<{ platform: string; url: string; name?: string }>;
  updated_at: string | null;
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
