import { useEffect, useMemo, useState } from 'react';
import { useAppStore, type MapState } from '../../store/AppStore';
import type { MapRoomPayload } from '../../protocol/webProtocol';
import { MapControls } from './MapControls';
import { MapViewport } from './MapViewport';

type Pan = {
  x: number;
  y: number;
};

const DEFAULT_PAN: Pan = { x: 0, y: 0 };

function isMapReady(map: MapState): boolean {
  return map.syncStatus === 'ready' && Object.keys(map.roomsById).length > 0;
}

function sortRooms(rooms: MapRoomPayload[]): MapRoomPayload[] {
  return [...rooms].sort((left, right) => {
    if (left.z !== right.z) return left.z - right.z;
    if (left.y !== right.y) return left.y - right.y;
    if (left.x !== right.x) return left.x - right.x;
    return left.room_id - right.room_id;
  });
}

function uniqueFloors(rooms: MapRoomPayload[]): number[] {
  return [...new Set(rooms.map((room) => room.z))].sort((left, right) => left - right);
}

function roomByFloor(rooms: MapRoomPayload[]): Map<number, MapRoomPayload[]> {
  const grouped = new Map<number, MapRoomPayload[]>();
  for (const room of rooms) {
    const entries = grouped.get(room.z) ?? [];
    entries.push(room);
    grouped.set(room.z, entries);
  }
  for (const [floor, entries] of grouped.entries()) {
    grouped.set(floor, sortRooms(entries));
  }
  return grouped;
}

function floorLabel(floor: number | null): string {
  return floor === null ? 'nieznane piętro' : `piętro z = ${floor}`;
}

export function WorldMapPanel() {
  const { state } = useAppStore();
  return <WorldMapPanelView map={state.map} />;
}

type ViewProps = {
  map: MapState;
};

export function WorldMapPanelView({ map }: ViewProps) {
  const rooms = useMemo(() => sortRooms(Object.values(map.roomsById)), [map.roomsById]);
  const roomLookup = useMemo(
    () =>
      new Map(
        Object.entries(map.roomsById).map(([id, room]) => [Number(id), room] as const),
      ),
    [map.roomsById],
  );
  const floors = useMemo(() => uniqueFloors(rooms), [rooms]);
  const roomsByFloor = useMemo(() => roomByFloor(rooms), [rooms]);
  const currentRoomId = map.currentRoomId;
  const currentRoom = currentRoomId !== null ? map.roomsById[currentRoomId] ?? null : null;
  const currentRoomZ = currentRoom?.z ?? null;

  const [selectedFloor, setSelectedFloor] = useState<number | null>(() => currentRoom?.z ?? null);
  const [focusRoomId, setFocusRoomId] = useState<number | null>(() => currentRoom?.room_id ?? null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState<Pan>(DEFAULT_PAN);

  useEffect(() => {
    if (currentRoomId === null || currentRoomZ === null) {
      return;
    }
    setSelectedFloor(currentRoomZ);
    setFocusRoomId(currentRoomId);
    setPan(DEFAULT_PAN);
  }, [currentRoomId, currentRoomZ]);

  useEffect(() => {
    if (selectedFloor !== null || floors.length === 0) {
      return;
    }
    const initialFloor = currentRoomZ ?? floors[0] ?? null;
    if (initialFloor === null) {
      return;
    }
    setSelectedFloor(initialFloor);
    const floorRooms = roomsByFloor.get(initialFloor) ?? [];
    setFocusRoomId(currentRoomZ === initialFloor ? currentRoomId : floorRooms[0]?.room_id ?? null);
    setPan(DEFAULT_PAN);
  }, [currentRoomId, currentRoomZ, floors, roomsByFloor, selectedFloor]);

  useEffect(() => {
    if (selectedFloor === null) {
      return;
    }
    const floorRooms = roomsByFloor.get(selectedFloor) ?? [];
    if (floorRooms.length === 0) {
      return;
    }
    if (focusRoomId !== null && floorRooms.some((room) => room.room_id === focusRoomId)) {
      return;
    }
    const nextFocus = currentRoomZ === selectedFloor ? currentRoomId : floorRooms[0]?.room_id ?? null;
    setFocusRoomId(nextFocus);
    setPan(DEFAULT_PAN);
  }, [currentRoomId, currentRoomZ, focusRoomId, roomsByFloor, selectedFloor]);

  const selectedRooms = useMemo(() => {
    if (selectedFloor === null) {
      return [];
    }
    return roomsByFloor.get(selectedFloor) ?? [];
  }, [roomsByFloor, selectedFloor]);

  const selectedRoom = focusRoomId !== null ? map.roomsById[focusRoomId] ?? selectedRooms[0] ?? currentRoom : currentRoom ?? selectedRooms[0] ?? rooms[0] ?? null;
  const onFloorChange = (floor: number) => {
    setSelectedFloor(floor);
    const floorRooms = roomsByFloor.get(floor) ?? [];
    const nextFocus = currentRoomZ === floor ? currentRoomId : floorRooms[0]?.room_id ?? null;
    setFocusRoomId(nextFocus);
    setPan(DEFAULT_PAN);
  };

  const centerOnSelectedRoom = (roomId: number | null = selectedRoom?.room_id ?? currentRoomId ?? null) => {
    if (roomId === null) {
      return;
    }
    const room = map.roomsById[roomId];
    if (!room) {
      return;
    }
    setSelectedFloor(room.z);
    setFocusRoomId(roomId);
    setPan(DEFAULT_PAN);
  };

  const canRenderMap = isMapReady(map) && selectedRoom !== null && selectedRooms.length > 0;

  if (map.syncStatus === 'idle' && !isMapReady(map)) {
    return (
      <section className="panel world-map-panel" aria-label="Mapa odkrytej okolicy">
        <header className="world-map-header">
          <div>
            <p className="eyebrow">Mapa</p>
            <h2>Odkryta mapa</h2>
          </div>
        </header>
        <div className="map-stage map-empty-frame">
          <div className="map-empty-state">
            <p>Mapa pojawi się po wejściu do gry.</p>
          </div>
        </div>
      </section>
    );
  }

  const syncing = map.syncStatus === 'syncing' && map.pendingSnapshot !== null;
  const currentRoomLabel = currentRoom ? currentRoom.name : 'Nieznana lokacja';
  const currentRegionLabel = currentRoom ? currentRoom.region : 'Nieznany region';

  return (
    <section className="panel world-map-panel" aria-label="Mapa odkrytej okolicy">
      <header className="world-map-header">
        <div>
          <p className="eyebrow">Mapa</p>
          <h2>Odkryta mapa</h2>
          <p className="caption">
            {currentRegionLabel} · {floorLabel(selectedFloor)} · {currentRoomLabel}
          </p>
        </div>
        <div className="world-map-summary">
          <span className="status-pill">{selectedRooms.length} pok.</span>
        </div>
      </header>

      <MapControls
        floors={floors}
        selectedFloor={selectedFloor}
        zoom={zoom}
        onFloorChange={onFloorChange}
        onZoomIn={() => setZoom((current) => Math.min(2.4, Math.round((current + 0.12) * 100) / 100))}
        onZoomOut={() => setZoom((current) => Math.max(0.55, Math.round((current - 0.12) * 100) / 100))}
        onCenter={() => centerOnSelectedRoom()}
        centerDisabled={selectedRoom === null}
      />

      <div className="map-stage">
        {canRenderMap ? (
          <MapViewport
            rooms={selectedRooms}
            roomLookup={roomLookup}
            edges={map.edges}
            focusRoom={selectedRoom}
            currentRoomId={currentRoom?.room_id ?? null}
            zoom={zoom}
            pan={pan}
            onPanChange={setPan}
            onZoomChange={setZoom}
            onCenterRoom={centerOnSelectedRoom}
          />
        ) : (
          <div className="map-empty-state">
            <p className="muted">Brak odkrytych pokoi na wybranym piętrze.</p>
          </div>
        )}
        {syncing ? <div className="map-sync-indicator" aria-live="polite">Synchronizacja mapy w tle…</div> : null}
      </div>
    </section>
  );
}
