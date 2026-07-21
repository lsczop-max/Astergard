import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { CharacterVitalsPanel } from './CharacterVitalsPanel';

describe('CharacterVitalsPanel', () => {
  it('shows a safe fallback before vitals are available', () => {
    render(<CharacterVitalsPanel vitals={null} />);
    expect(screen.getByText(/Brak danych stanu/)).toBeInTheDocument();
  });

  it('renders aria-safe progressbars and clamps zero maxima', () => {
    render(
      <CharacterVitalsPanel
        vitals={{
          condition_current: 0,
          condition_max: 0,
          condition_label: 'jest na granicy upadku',
          stamina_current: 0,
          stamina_max: 0,
          stamina_label: 'na skraju wyczerpania',
        }}
      />,
    );

    const condition = screen.getByRole('progressbar', { name: 'Kondycja' });
    const stamina = screen.getByRole('progressbar', { name: 'Energia' });
    expect(condition).toHaveAttribute('aria-valuenow', '0');
    expect(condition).toHaveAttribute('aria-valuemax', '100');
    expect(condition).toHaveAttribute('aria-valuetext', 'Kondycja: jest na granicy upadku, 0%');
    expect(stamina).toHaveAttribute('aria-valuenow', '0');
    expect(screen.getAllByText('0%')).toHaveLength(2);
  });
});
