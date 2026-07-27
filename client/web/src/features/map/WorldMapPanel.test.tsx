import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { MapRoomPayload } from '../../protocol/webProtocol';
import type { MapState } from '../../store/AppStore';
import { WorldMapPanelView } from './WorldMapPanel';

function makeMap(partial: Partial<MapState>): MapState {
  return {
    syncStatus: 'ready',
    syncId: 'sync-1',
    currentRoomId: 1,
    roomsById: {},
    edges: [],
    pendingSnapshot: null,
    ...partial,
  };
}

function installTestPointerEvent(): () => void {
  const originalDescriptor = Object.getOwnPropertyDescriptor(window, 'PointerEvent');

  class TestPointerEvent extends MouseEvent {
    readonly pointerId: number;
    readonly pointerType: string;
    readonly isPrimary: boolean;

    constructor(type: string, init: PointerEventInit = {}) {
      super(type, init);
      this.pointerId = init.pointerId ?? 0;
      this.pointerType = init.pointerType ?? '';
      this.isPrimary = init.isPrimary ?? false;
    }
  }

  Object.defineProperty(window, 'PointerEvent', {
    configurable: true,
    writable: true,
    value: TestPointerEvent,
  });

  return () => {
    if (originalDescriptor) {
      Object.defineProperty(window, 'PointerEvent', originalDescriptor);
      return;
    }
    Reflect.deleteProperty(window, 'PointerEvent');
  };
}

function parseTranslate(transform: string | null): { x: number; y: number } {
  const match = /translate\(([-\d.]+), ([-\d.]+)\)/.exec(transform ?? '');
  if (!match) {
    throw new Error(`Cannot parse transform: ${transform ?? 'null'}`);
  }
  return {
    x: Number(match[1]),
    y: Number(match[2]),
  };
}

describe('WorldMapPanelView', () => {
  it('renders a small map with the current room highlighted and visible labels only for the current node', () => {
    const { container } = render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 2,
          roomsById: {
            1: { room_id: 1, name: 'Północna Brama', region: 'Miasto', x: 0, y: 1, z: 0 },
            2: { room_id: 2, name: 'Rynek', region: 'Miasto', x: 0, y: 0, z: 0 },
            3: { room_id: 3, name: 'Południowa Ulica', region: 'Miasto', x: 1, y: -1, z: 0 },
          },
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'poludnie' },
            { from_room_id: 2, to_room_id: 1, direction: 'polnoc' },
            { from_room_id: 2, to_room_id: 3, direction: 'poludniowy-wschod' },
          ],
        })}
      />,
    );

    expect(screen.getByText('Miasto · piętro z = 0 · Rynek')).toBeInTheDocument();
    expect(screen.getByText('Rynek')).toBeInTheDocument();
    expect(screen.queryByText('Północna Brama')).not.toBeInTheDocument();
    expect(screen.queryByText('Południowa Ulica')).not.toBeInTheDocument();
    expect(container.querySelectorAll('[data-room-id]').length).toBe(3);
    expect(container.querySelectorAll('[data-edge-key]').length).toBe(2);

    const currentRoom = screen.getByTestId('map-room-2');
    expect(currentRoom).toHaveAttribute('data-room-current', 'true');
    expect(screen.getByRole('img', { name: 'Mapa odkrytej okolicy' })).toBeInTheDocument();
    expect(screen.getByText('Północ')).toBeInTheDocument();
    expect(screen.getByText('Południe')).toBeInTheDocument();
    expect(screen.getByText('Zachód')).toBeInTheDocument();
    expect(screen.getByText('Wschód')).toBeInTheDocument();
  });

  it('keeps north at the top and renders diagonal geometry consistently', () => {
    render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: {
            1: { room_id: 1, name: 'Centrum', region: 'Miasto', x: 0, y: 0, z: 0 },
            2: { room_id: 2, name: 'Północ', region: 'Miasto', x: 0, y: 1, z: 0 },
            3: { room_id: 3, name: 'Płd-Zach', region: 'Miasto', x: -1, y: -1, z: 0 },
          },
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'polnoc' },
            { from_room_id: 1, to_room_id: 3, direction: 'poludniowy-zachod' },
          ],
        })}
      />,
    );

    const northEdge = screen.getByTestId('map-edge-1-2');
    const diagonalEdge = screen.getByTestId('map-edge-1-3');
    expect(Number(northEdge.getAttribute('y2'))).toBeLessThan(Number(northEdge.getAttribute('y1')));
    expect(Number(diagonalEdge.getAttribute('x2'))).toBeLessThan(Number(diagonalEdge.getAttribute('x1')));
    expect(Number(diagonalEdge.getAttribute('y2'))).toBeGreaterThan(Number(diagonalEdge.getAttribute('y1')));
  });

  it('projects all compass directions with north at the top and keeps compass labels fixed', () => {
    render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: {
            1: { room_id: 1, name: 'Centrum', region: 'Miasto', x: 0, y: 0, z: 0 },
            2: { room_id: 2, name: 'Północ', region: 'Miasto', x: 0, y: 1, z: 0 },
            3: { room_id: 3, name: 'Południe', region: 'Miasto', x: 0, y: -1, z: 0 },
            4: { room_id: 4, name: 'Wschód', region: 'Miasto', x: 1, y: 0, z: 0 },
            5: { room_id: 5, name: 'Zachód', region: 'Miasto', x: -1, y: 0, z: 0 },
            6: { room_id: 6, name: 'Północny wschód', region: 'Miasto', x: 1, y: 1, z: 0 },
            7: { room_id: 7, name: 'Północny zachód', region: 'Miasto', x: -1, y: 1, z: 0 },
            8: { room_id: 8, name: 'Południowy wschód', region: 'Miasto', x: 1, y: -1, z: 0 },
            9: { room_id: 9, name: 'Południowy zachód', region: 'Miasto', x: -1, y: -1, z: 0 },
          },
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'polnoc' },
            { from_room_id: 1, to_room_id: 3, direction: 'poludnie' },
            { from_room_id: 1, to_room_id: 4, direction: 'wschod' },
            { from_room_id: 1, to_room_id: 5, direction: 'zachod' },
            { from_room_id: 1, to_room_id: 6, direction: 'polnocny-wschod' },
            { from_room_id: 1, to_room_id: 7, direction: 'polnocny-zachod' },
            { from_room_id: 1, to_room_id: 8, direction: 'poludniowy-wschod' },
            { from_room_id: 1, to_room_id: 9, direction: 'poludniowy-zachod' },
          ],
        })}
      />,
    );

    const center = parseTranslate(screen.getByTestId('map-room-1').getAttribute('transform'));
    const north = parseTranslate(screen.getByTestId('map-room-2').getAttribute('transform'));
    const south = parseTranslate(screen.getByTestId('map-room-3').getAttribute('transform'));
    const east = parseTranslate(screen.getByTestId('map-room-4').getAttribute('transform'));
    const west = parseTranslate(screen.getByTestId('map-room-5').getAttribute('transform'));
    const northeast = parseTranslate(screen.getByTestId('map-room-6').getAttribute('transform'));
    const northwest = parseTranslate(screen.getByTestId('map-room-7').getAttribute('transform'));
    const southeast = parseTranslate(screen.getByTestId('map-room-8').getAttribute('transform'));
    const southwest = parseTranslate(screen.getByTestId('map-room-9').getAttribute('transform'));

    expect(north.y).toBeLessThan(center.y);
    expect(south.y).toBeGreaterThan(center.y);
    expect(east.x).toBeGreaterThan(center.x);
    expect(west.x).toBeLessThan(center.x);
    expect(northeast.x).toBeGreaterThan(center.x);
    expect(northeast.y).toBeLessThan(center.y);
    expect(northwest.x).toBeLessThan(center.x);
    expect(northwest.y).toBeLessThan(center.y);
    expect(southeast.x).toBeGreaterThan(center.x);
    expect(southeast.y).toBeGreaterThan(center.y);
    expect(southwest.x).toBeLessThan(center.x);
    expect(southwest.y).toBeGreaterThan(center.y);
    expect(screen.getByText('Północ')).toBeInTheDocument();
    expect(screen.getByText('Południe')).toBeInTheDocument();
    expect(screen.getByText('Zachód')).toBeInTheDocument();
    expect(screen.getByText('Wschód')).toBeInTheDocument();
  });

  it('deduplicates reciprocal edges visually and marks one-way links', () => {
    const { container } = render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: {
            1: { room_id: 1, name: 'A', region: 'Miasto', x: 0, y: 0, z: 0 },
            2: { room_id: 2, name: 'B', region: 'Miasto', x: 1, y: 0, z: 0 },
            3: { room_id: 3, name: 'C', region: 'Miasto', x: 2, y: 0, z: 0 },
          },
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
            { from_room_id: 2, to_room_id: 1, direction: 'zachod' },
            { from_room_id: 2, to_room_id: 3, direction: 'wschod' },
          ],
        })}
      />,
    );

    expect(container.querySelectorAll('[data-edge-key]').length).toBe(2);
    expect(screen.getByTestId('map-edge-1-2')).toHaveAttribute('data-directionality', 'bidirectional');
    expect(screen.getByTestId('map-edge-2-3')).toHaveAttribute('data-directionality', 'oneway');
  });

  it('shows floor switching, vertical markers and ignores missing rooms in edges', () => {
    const { container } = render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: {
            1: { room_id: 1, name: 'Parter', region: 'Miasto', x: 0, y: 0, z: 0 },
            2: { room_id: 2, name: 'Piętro', region: 'Miasto', x: 0, y: 0, z: 1 },
            3: { room_id: 3, name: 'Boczna Aleja', region: 'Miasto', x: 1, y: 1, z: 0 },
          },
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'gora' },
            { from_room_id: 2, to_room_id: 1, direction: 'dol' },
            { from_room_id: 1, to_room_id: 3, direction: 'wschod' },
            { from_room_id: 1, to_room_id: 99, direction: 'wschod' },
          ],
        })}
      />,
    );

    expect(screen.getByTestId('map-room-1')).toBeInTheDocument();
    expect(screen.getByText('↑')).toBeInTheDocument();
    expect(container.querySelectorAll('[data-edge-key]').length).toBe(1);
    expect(screen.queryByText('↓')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Piętro 1' }));
    expect(screen.getByText('Piętro')).toBeInTheDocument();
    expect(screen.queryByTestId('map-room-1')).not.toBeInTheDocument();
    expect(screen.getByText('↓')).toBeInTheDocument();
    expect(screen.queryByText('↑')).not.toBeInTheDocument();
  });

  it('supports zoom, pan, centering and preserves the view on update without room change', () => {
    const restorePointerEvent = installTestPointerEvent();
    const { rerender, container } = render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: {
            1: { room_id: 1, name: 'Start', region: 'Miasto', x: 0, y: 0, z: 0 },
            2: { room_id: 2, name: 'Wschód', region: 'Miasto', x: 1, y: 0, z: 0 },
          },
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        })}
      />,
    );

    const canvas = container.querySelector('.map-canvas') as HTMLDivElement;
    const pointerCapture = new Set<number>();
    const setPointerCapture = vi.fn((pointerId: number) => {
      pointerCapture.add(pointerId);
    });
    const hasPointerCapture = vi.fn((pointerId: number) => pointerCapture.has(pointerId));
    const releasePointerCapture = vi.fn((pointerId: number) => {
      pointerCapture.delete(pointerId);
    });
    Object.defineProperty(canvas, 'setPointerCapture', {
      configurable: true,
      value: setPointerCapture,
    });
    Object.defineProperty(canvas, 'hasPointerCapture', {
      configurable: true,
      value: hasPointerCapture,
    });
    Object.defineProperty(canvas, 'releasePointerCapture', {
      configurable: true,
      value: releasePointerCapture,
    });

    try {
      fireEvent.pointerDown(canvas, {
        button: 0,
        buttons: 1,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
        clientX: 100,
        clientY: 100,
      });
      expect(setPointerCapture).toHaveBeenCalledWith(1);

      fireEvent.pointerMove(canvas, {
        button: 0,
        buttons: 1,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
        clientX: 130,
        clientY: 120,
      });
      expect(screen.getByTestId('map-room-1')).toHaveAttribute('transform', 'translate(530, 370)');

      fireEvent.pointerUp(canvas, {
        button: 0,
        buttons: 0,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
        clientX: 130,
        clientY: 120,
      });
      expect(hasPointerCapture).toHaveBeenCalledWith(1);
      expect(releasePointerCapture).toHaveBeenCalledWith(1);
      expect(screen.getByTestId('map-room-1')).toHaveAttribute('transform', 'translate(530, 370)');

      fireEvent.click(screen.getByRole('button', { name: 'Powiększ mapę' }));
      expect(screen.getByRole('button', { name: 'Wyśrodkuj bieżącą lokację' })).toBeEnabled();
      expect(screen.getByText('112%')).toBeInTheDocument();

      rerender(
        <WorldMapPanelView
          map={makeMap({
            currentRoomId: 1,
            roomsById: {
              1: { room_id: 1, name: 'Start', region: 'Miasto', x: 0, y: 0, z: 0 },
              2: { room_id: 2, name: 'Wschód', region: 'Miasto', x: 1, y: 0, z: 0 },
              3: { room_id: 3, name: 'Północ', region: 'Miasto', x: 0, y: 1, z: 0 },
            },
            edges: [
              { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
              { from_room_id: 1, to_room_id: 3, direction: 'polnoc' },
            ],
          })}
        />,
      );

      expect(screen.getByTestId('map-room-1')).toHaveAttribute('transform', 'translate(530, 370)');

      fireEvent.click(screen.getByRole('button', { name: 'Wyśrodkuj bieżącą lokację' }));
      expect(screen.getByTestId('map-room-1')).toHaveAttribute('transform', 'translate(500, 350)');

      rerender(
        <WorldMapPanelView
          map={makeMap({
            currentRoomId: 4,
            roomsById: {
              1: { room_id: 1, name: 'Start', region: 'Miasto', x: 0, y: 0, z: 0 },
              2: { room_id: 2, name: 'Wschód', region: 'Miasto', x: 1, y: 0, z: 0 },
              3: { room_id: 3, name: 'Północ', region: 'Miasto', x: 0, y: 1, z: 0 },
              4: { room_id: 4, name: 'Piętro', region: 'Miasto', x: 0, y: 0, z: 1 },
            },
            edges: [
              { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
              { from_room_id: 1, to_room_id: 3, direction: 'polnoc' },
              { from_room_id: 1, to_room_id: 4, direction: 'gora' },
            ],
          })}
        />,
      );

      expect(screen.getByTestId('map-room-4')).toHaveAttribute('transform', 'translate(500, 350)');
      expect(screen.getByRole('button', { name: 'Piętro 1' })).toHaveAttribute('aria-pressed', 'true');
    } finally {
      restorePointerEvent();
    }
  });

  it('renders 500 rooms without exceptions and keeps hidden rooms absent', () => {
    const roomsById = Object.fromEntries(
      Array.from({ length: 500 }, (_, index) => {
        const roomId = index + 1;
        return [
          roomId,
          {
            room_id: roomId,
            name: `Pokój ${roomId}`,
            region: 'Astergard',
            x: index % 25,
            y: Math.floor(index / 25),
            z: 0,
          },
        ] as const;
      }),
    );
    const { container } = render(
      <WorldMapPanelView
        map={makeMap({
          currentRoomId: 1,
          roomsById: roomsById as Record<number, MapRoomPayload>,
          edges: Array.from({ length: 499 }, (_, index) => ({
            from_room_id: index + 1,
            to_room_id: index + 2,
            direction: 'wschod',
          })),
        })}
      />,
    );

    expect(container.querySelectorAll('[data-room-id]').length).toBe(500);
    expect(screen.getByTestId('map-room-500')).toBeInTheDocument();
    expect(screen.queryByTestId('map-room-501')).not.toBeInTheDocument();
  });

  it('handles idle, syncing and unknown current room states safely', () => {
    const { rerender } = render(<WorldMapPanelView map={makeMap({ syncStatus: 'idle', syncId: null, roomsById: {}, currentRoomId: null })} />);
    expect(screen.getByText('Mapa pojawi się po wejściu do gry.')).toBeInTheDocument();

    rerender(
      <WorldMapPanelView
        map={makeMap({
          syncStatus: 'syncing',
          pendingSnapshot: { syncId: 'sync-2', nextChunkIndex: 1, chunksByIndex: { 0: { map_version: 1, sync_id: 'sync-2', chunk_index: 0, complete: false, current_room_id: 1, rooms: [], edges: [] } } },
          roomsById: {},
          currentRoomId: null,
        })}
      />,
    );
    expect(screen.getByText('Synchronizacja mapy w tle…')).toBeInTheDocument();
    expect(screen.getByText('Brak odkrytych pokoi na wybranym piętrze.')).toBeInTheDocument();
  });
});
