import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConnectionStatus } from './ConnectionStatus';

describe('ConnectionStatus', () => {
  it('shows readable labels', () => {
    render(<ConnectionStatus state="ready" />);
    expect(screen.getByText('Gotowe')).toBeInTheDocument();
  });
});
