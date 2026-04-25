import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MotionConfig } from 'framer-motion';
import Layout from './Layout';
import ProductPage from '../../pages/ProductPage';
import { getProduct } from '../../api/products';

vi.mock('../../api/products', () => ({
  getProduct: vi.fn(),
}));

function renderAt(path: string, child: React.ReactElement) {
  return render(
    <MotionConfig reducedMotion="always">
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route path="products/:slug" element={child} />
            <Route path="plain" element={<div>Plain content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </MotionConfig>
  );
}

describe('Layout', () => {
  it('hides the site footer on product runtime detail pages', async () => {
    vi.mocked(getProduct).mockResolvedValue({
      id: 1,
      slug: 'fish-game',
      title: 'Fish Game',
      description: 'A playable static product.',
      cover_image: null,
      runtime_url: '/product-runtime/fish-game/',
      status: 'published',
      created_at: '2026-04-20T10:00:00Z',
      updated_at: '2026-04-21T10:00:00Z',
    });

    renderAt('/products/fish-game', <ProductPage />);

    expect(await screen.findByTitle('Fish Game')).toBeInTheDocument();
    expect(screen.queryByText('Navigation')).not.toBeInTheDocument();
  });

  it('keeps the site footer on regular pages', () => {
    renderAt('/plain', <div>Plain content</div>);

    expect(screen.getByText('Navigation')).toBeInTheDocument();
  });
});
