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
  cover_image: string;
  content: string;
  content_type: string;  // "markdown" | "html"
  tech_stack: string;  // JSON array string
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
