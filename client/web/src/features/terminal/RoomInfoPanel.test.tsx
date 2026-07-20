import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithStore } from '../../test/render';
import { RoomInfoPanel } from './RoomInfoPanel';

describe('RoomInfoPanel', () => {
  it('formats room data instead of raw JSON', () => {
    renderWithStore(
      <RoomInfoPanel
        room={{
          num: 1,
          name: 'Komnata',
          area: 'Zamek',
          coords: { x: 10, y: 20, z: 0 },
          exits: { north: 2 },
        }}
      />,
    );
    expect(screen.getByText('Komnata')).toBeInTheDocument();
    expect(screen.getByText('north → 2')).toBeInTheDocument();
  });
});
