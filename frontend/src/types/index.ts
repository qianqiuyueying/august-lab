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

export interface Comment {
  id: number;
  article_id: number;
  author_name: string;
  author_email: string;
  content: string;
  created_at: string | null;
}

export interface Page {
  id: number;
  slug: string;
  title: string;
  content: string;
  description: string;
  content_type: string;  // "markdown" | "html"
  status: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface Product {
  id: number;
  slug: string;
  title: string;
  description: string;
  cover_image?: string | null;
  status: string;
  created_at: string | null;
  updated_at: string | null;
}
