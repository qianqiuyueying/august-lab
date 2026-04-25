import client from './client';

export interface TagDist {
  name: string;
  count: number;
}

export interface RecentArticle {
  id: number;
  title: string;
  status: string;
  created_at: string | null;
  tags: { id: number; name: string }[];
}

export interface DashboardStats {
  article_count: number;
  published_count: number;
  draft_count: number;
  product_count: number;
  page_count: number;
  tag_count: number;
  user_count: number;
  recent_articles: RecentArticle[];
  tag_distribution: TagDist[];
  database_size: number | null;
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const { data } = await client.get<DashboardStats>('/dashboard/stats');
  return data;
};
