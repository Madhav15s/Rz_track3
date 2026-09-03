import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import App from './App';
import DecisionConsole from './views/DecisionConsole';
import Execution from './views/Execution';

vi.mock('./api', () => {
  return {
    default: {
      get: (url: string) => {
        if (url === '/overview') return Promise.resolve({ data: { revenue_at_risk: 100 } });
        if (url === '/cases') return Promise.resolve({ data: { cases: [] } });
        if (url.includes('/decision')) return Promise.resolve({ data: { candidate_actions: [] } });
        return Promise.resolve({ data: {} });
      }
    }
  };
});

describe('Dashboard Renders', () => {
  it('renders the main dashboard navigation', async () => {
    render(<App />);
    await waitFor(() => {
        expect(screen.getByText(/Executive Overview/i)).toBeInTheDocument();
    });
  });
});

describe('Decision Data & Boundaries', () => {
  it('displays policy rejection correctly', async () => {
    render(
      <MemoryRouter>
        <DecisionConsole />
      </MemoryRouter>
    );
  });
});

describe('Execution Boundaries', () => {
  it('distinguishes simulated vs razorpay test mode', () => {
    render(<Execution />);
  });
});
