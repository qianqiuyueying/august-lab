import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MotionConfig } from 'framer-motion';
import ArticleCard from './ArticleCard';
import type { ArticleListItem } from '../../types';

function renderWithRouter(ui: React.ReactElement) {
  return render(
    <MotionConfig reducedMotion="user">
      <MemoryRouter>{ui}</MemoryRouter>
    </MotionConfig>
  );
}

const mockArticle: ArticleListItem = {
  id: 1,
  slug: 'test-article',
  title: 'Test Article',
  summary: 'This is a test summary for the article.',
  status: 'published',
  tags: [
    { id: 1, name: 'react' },
    { id: 2, name: 'typescript' },
  ],
  created_at: '2024-01-15T10:00:00Z',
};

describe('ArticleCard', () => {
  it('renders article title', () => {
    renderWithRouter(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('Test Article')).toBeInTheDocument();
  });

  it('renders article summary', () => {
    renderWithRouter(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('This is a test summary for the article.')).toBeInTheDocument();
  });

  it('renders all tags as links', () => {
    renderWithRouter(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('#react')).toBeInTheDocument();
    expect(screen.getByText('#typescript')).toBeInTheDocument();
  });

  it('links to the correct article page', () => {
    renderWithRouter(<ArticleCard article={mockArticle} />);
    const titleLink = screen.getByRole('link', { name: /Test Article/i });
    expect(titleLink).toHaveAttribute('href', '/articles/test-article');
  });

  it('renders with empty tags', () => {
    const articleWithoutTags: ArticleListItem = {
      ...mockArticle,
      tags: [],
    };
    renderWithRouter(<ArticleCard article={articleWithoutTags} />);
    expect(screen.getByText('Test Article')).toBeInTheDocument();
  });

  it('uses the brand article fallback when no cover image is set', () => {
    const { container } = renderWithRouter(<ArticleCard article={mockArticle} />);
    expect(container.querySelector('img')).toHaveAttribute('src', '/images/brand/fallback-article.webp');
  });
});
