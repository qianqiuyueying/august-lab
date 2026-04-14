import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import TagList from './TagList';

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

const mockTags = [
  { id: 1, name: 'react' },
  { id: 2, name: 'vue' },
  { id: 3, name: 'typescript' },
];

describe('TagList', () => {
  it('shows loading state', () => {
    renderWithRouter(<TagList tags={[]} loading={true} />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders all tags when not loading', () => {
    renderWithRouter(<TagList tags={mockTags} loading={false} />);
    expect(screen.getByText('#react')).toBeInTheDocument();
    expect(screen.getByText('#vue')).toBeInTheDocument();
    expect(screen.getByText('#typescript')).toBeInTheDocument();
  });

  it('renders tags as links with correct href', () => {
    renderWithRouter(<TagList tags={mockTags} loading={false} />);
    const reactLink = screen.getByText('#react');
    expect(reactLink).toHaveAttribute('href', '/?tag=react');
  });

  it('renders empty when tags array is empty and not loading', () => {
    const { container } = renderWithRouter(<TagList tags={[]} loading={false} />);
    expect(container.textContent).toBe('');
  });
});
