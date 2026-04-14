import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SearchBar from './SearchBar';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...(actual as Record<string, unknown>),
    useNavigate: () => mockNavigate,
  };
});

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('SearchBar', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders search input and button', () => {
    renderWithRouter(<SearchBar />);
    expect(screen.getByPlaceholderText('搜索文章...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '搜索' })).toBeInTheDocument();
  });

  it('navigates to search page when submitting with query', () => {
    renderWithRouter(<SearchBar />);
    const input = screen.getByPlaceholderText('搜索文章...');
    fireEvent.change(input, { target: { value: 'react hooks' } });
    fireEvent.submit(input.closest('form')!);

    expect(mockNavigate).toHaveBeenCalledWith('/?search=react%20hooks');
  });

  it('does not navigate when submitting empty query', () => {
    renderWithRouter(<SearchBar />);
    const form = screen.getByPlaceholderText('搜索文章...').closest('form')!;
    fireEvent.submit(form);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('does not navigate when submitting whitespace-only query', () => {
    renderWithRouter(<SearchBar />);
    const input = screen.getByPlaceholderText('搜索文章...');
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.submit(input.closest('form')!);

    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
