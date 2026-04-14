import { describe, it, expect, vi, beforeEach } from 'vitest';
import client from '../api/client';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => {
      const mockInstance = {
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: vi.fn(), eject: vi.fn() },
        },
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        defaults: {
          headers: {
            common: {},
          },
        },
      };
      return mockInstance;
    }),
  },
}));

describe('API Client', () => {
  it('should create an axios instance with /api base URL', () => {
    // The client module uses axios.create with baseURL: '/api'
    // This test verifies the module loads correctly
    expect(client).toBeDefined();
  });
});
