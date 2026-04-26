import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MotionConfig } from 'framer-motion';
import ProductPage from './ProductPage';
import { getProduct } from '../api/products';
import type { Product } from '../types';

vi.mock('../api/products', () => ({
  getProduct: vi.fn(),
}));

const mockProduct: Product = {
  id: 1,
  slug: 'demo-product',
  title: 'Demo Product',
  description: 'A runnable static product.',
  cover_image: null,
  runtime_url: '/product-runtime/demo-product/',
  status: 'published',
  created_at: '2026-04-20T10:00:00Z',
  updated_at: '2026-04-21T10:00:00Z',
};

function renderProductPage() {
  return render(
    <MotionConfig reducedMotion="always">
      <MemoryRouter initialEntries={['/products/demo-product']}>
        <Routes>
          <Route path="/products/:slug" element={<ProductPage />} />
        </Routes>
      </MemoryRouter>
    </MotionConfig>
  );
}

describe('ProductPage', () => {
  beforeEach(() => {
    vi.mocked(getProduct).mockReset();
  });

  it('renders the uploaded static runtime in an iframe', async () => {
    vi.mocked(getProduct).mockResolvedValue(mockProduct);

    renderProductPage();

    const frame = await screen.findByTitle('Demo Product');
    expect(frame).toHaveAttribute('src', '/product-runtime/demo-product/');
    expect(screen.getByRole('link', { name: '新窗口打开' })).toHaveAttribute('href', '/product-runtime/demo-product/');
  });

  it('shows a clear empty state when the product has no runtime file', async () => {
    vi.mocked(getProduct).mockResolvedValue({ ...mockProduct, runtime_url: null });

    renderProductPage();

    expect(await screen.findByText('作品尚未上传运行文件')).toBeInTheDocument();
  });

  it('keeps product metadata in a collapsible side panel', async () => {
    vi.mocked(getProduct).mockResolvedValue(mockProduct);

    renderProductPage();

    fireEvent.click(await screen.findByRole('button', { name: /作品信息/ }));

    expect(screen.getByText('A runnable static product.')).toBeInTheDocument();
    expect(screen.getByText('/demo-product')).toBeInTheDocument();
  });
});
