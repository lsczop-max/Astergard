import { useEffect, useMemo, useRef, useState } from 'react';
import type { PointerEvent as ReactPointerEvent } from 'react';
import type { MapEdgePayload, MapRoomPayload } from '../../protocol/webProtocol';

type Pan = {
  x: number;
  y: number;
};

type Props = {
  rooms: MapRoomPayload[];
  roomLookup: Map<number, MapRoomPayload>;
  edges: MapEdgePayload[];
  focusRoom: MapRoomPayload | null;
  currentRoomId: number | null;
  zoom: number;
  pan: Pan;
  onPanChange: (next: Pan) => void;
  onZoomChange: (next: number) => void;
  onCenterRoom: (roomId: number) => void;
};

const VIEWPORT_WIDTH = 1000;
const VIEWPORT_HEIGHT = 700;
const GRID_SPACING = 78;
const BASE_ROOM_SIZE = 16;

type VisibleRoom = MapRoomPayload & {
  screenX: number;
  screenY: number;
  isCurrent: boolean;
  isFocused: boolean;
  verticalUp: boolean;
  verticalDown: boolean;
};

type VisibleEdge = {
  key: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  bidirectional: boolean;
  oneWayFrom: number;
  oneWayTo: number;
};

function clampZoom(zoom: number): number {
  return Math.max(0.55, Math.min(2.4, Number.isFinite(zoom) ? zoom : 1));
}

function projectRoom(room: MapRoomPayload, focusRoom: MapRoomPayload, zoom: number, pan: Pan): { x: number; y: number } {
  const scaled = GRID_SPACING * zoom;
  return {
    x: VIEWPORT_WIDTH / 2 + pan.x + (room.x - focusRoom.x) * scaled,
    y: VIEWPORT_HEIGHT / 2 + pan.y + (focusRoom.y - room.y) * scaled,
  };
}

function oppositeEdgeExists(edges: MapEdgePayload[], fromId: number, toId: number): boolean {
  return edges.some((edge) => edge.from_room_id === toId && edge.to_room_id === fromId);
}

function buildVisibleEdges(roomsById: Map<number, MapRoomPayload>, rooms: MapRoomPayload[], edges: MapEdgePayload[], focusRoom: MapRoomPayload, zoom: number, pan: Pan): VisibleEdge[] {
  const visibleRoomIds = new Set(rooms.map((room) => room.room_id));
  const grouped = new Map<string, MapEdgePayload[]>();
  for (const edge of edges) {
    if (!visibleRoomIds.has(edge.from_room_id) || !visibleRoomIds.has(edge.to_room_id)) {
      continue;
    }
    const from = roomsById.get(edge.from_room_id);
    const to = roomsById.get(edge.to_room_id);
    if (!from || !to || from.z !== focusRoom.z || to.z !== focusRoom.z) {
      continue;
    }
    const key = edge.from_room_id < edge.to_room_id ? `${edge.from_room_id}:${edge.to_room_id}` : `${edge.to_room_id}:${edge.from_room_id}`;
    const entries = grouped.get(key) ?? [];
    entries.push(edge);
    grouped.set(key, entries);
  }

  return [...grouped.entries()].map(([key, entries]) => {
    const first = entries[0] as MapEdgePayload;
    const fromRoom = roomsById.get(first.from_room_id) ?? focusRoom;
    const toRoom = roomsById.get(first.to_room_id) ?? focusRoom;
    const reciprocal = entries.some((edge) => oppositeEdgeExists(entries, edge.from_room_id, edge.to_room_id));
    const startRoom = reciprocal ? (fromRoom.room_id < toRoom.room_id ? fromRoom : toRoom) : fromRoom;
    const endRoom = reciprocal ? (startRoom.room_id === fromRoom.room_id ? toRoom : fromRoom) : toRoom;
    const start = projectRoom(startRoom, focusRoom, zoom, pan);
    const end = projectRoom(endRoom, focusRoom, zoom, pan);
    const bidirectional = reciprocal;
    return {
      key,
      x1: start.x,
      y1: start.y,
      x2: end.x,
      y2: end.y,
      bidirectional,
      oneWayFrom: startRoom.room_id,
      oneWayTo: endRoom.room_id,
    };
  });
}

function buildVisibleRooms(
  rooms: MapRoomPayload[],
  edges: MapEdgePayload[],
  roomLookup: Map<number, MapRoomPayload>,
  focusRoom: MapRoomPayload,
  currentRoomId: number | null,
  zoom: number,
  pan: Pan,
): VisibleRoom[] {
  return rooms.map((room) => {
    const { x, y } = projectRoom(room, focusRoom, zoom, pan);
    let verticalUp = false;
    let verticalDown = false;
    for (const edge of edges) {
      if (edge.from_room_id !== room.room_id && edge.to_room_id !== room.room_id) {
        continue;
      }
      const otherRoomId = edge.from_room_id === room.room_id ? edge.to_room_id : edge.from_room_id;
      const otherRoom = roomLookup.get(otherRoomId);
      if (!otherRoom || otherRoom.z === room.z) {
        continue;
      }
      if (otherRoom.z > room.z) {
        verticalUp = true;
      }
      if (otherRoom.z < room.z) {
        verticalDown = true;
      }
    }
    return {
      ...room,
      screenX: x,
      screenY: y,
      isCurrent: room.room_id === currentRoomId,
      isFocused: room.room_id === focusRoom.room_id,
      verticalUp,
      verticalDown,
    };
  });
}

export function MapViewport({ rooms, roomLookup, edges, focusRoom, currentRoomId, zoom, pan, onPanChange, onZoomChange, onCenterRoom }: Props) {
  const [activeRoomId, setActiveRoomId] = useState<number | null>(currentRoomId);
  const [dragging, setDragging] = useState(false);
  const dragState = useRef<{
    pointerId: number;
    startX: number;
    startY: number;
    startPanX: number;
    startPanY: number;
  } | null>(null);

  const actualFocusRoom = focusRoom ?? rooms[0] ?? null;
  const safeZoom = clampZoom(zoom);

  useEffect(() => {
    setActiveRoomId(currentRoomId);
  }, [currentRoomId]);

  const visibleRooms = useMemo(() => {
    if (!actualFocusRoom) {
      return [];
    }
    return buildVisibleRooms(rooms, edges, roomLookup, actualFocusRoom, currentRoomId, safeZoom, pan);
  }, [actualFocusRoom, currentRoomId, edges, pan, roomLookup, rooms, safeZoom]);

  const visibleEdges = useMemo(() => {
    if (!actualFocusRoom) {
      return [];
    }
    return buildVisibleEdges(roomLookup, rooms, edges, actualFocusRoom, safeZoom, pan);
  }, [actualFocusRoom, edges, pan, roomLookup, rooms, safeZoom]);

  const activeRoom = visibleRooms.find((room) => room.room_id === activeRoomId) ?? visibleRooms.find((room) => room.isCurrent) ?? visibleRooms[0] ?? null;
  const roomLabelZoom = Math.max(0.85, safeZoom);
  const roomSize = BASE_ROOM_SIZE * roomLabelZoom;
  const roomStrokeWidth = Math.max(1.1, 1.8 * roomLabelZoom);
  const labelOffset = 14 * roomLabelZoom;

  const startDrag = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) {
      return;
    }
    if (typeof event.currentTarget.setPointerCapture === 'function') {
      event.currentTarget.setPointerCapture(event.pointerId);
    }
    setDragging(true);
    dragState.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startPanX: pan.x,
      startPanY: pan.y,
    };
  };

  const moveDrag = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!dragState.current || dragState.current.pointerId !== event.pointerId) {
      return;
    }
    onPanChange({
      x: dragState.current.startPanX + (event.clientX - dragState.current.startX),
      y: dragState.current.startPanY + (event.clientY - dragState.current.startY),
    });
  };

  const endDrag = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!dragState.current || dragState.current.pointerId !== event.pointerId) {
      return;
    }
    if (
      typeof event.currentTarget.hasPointerCapture === 'function' &&
      event.currentTarget.hasPointerCapture(event.pointerId) &&
      typeof event.currentTarget.releasePointerCapture === 'function'
    ) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    dragState.current = null;
    setDragging(false);
  };

  if (!actualFocusRoom) {
    return (
      <div className="map-stage map-empty-frame">
        <div className="map-empty-state">
          <p className="caption muted">Brak danych mapy.</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`map-stage map-canvas${dragging ? ' is-dragging' : ''}`}
      onWheel={(event) => {
        event.preventDefault();
        const delta = event.deltaY > 0 ? -0.12 : 0.12;
        const nextZoom = clampZoom(safeZoom + delta);
        if (nextZoom !== safeZoom) {
          onZoomChange(nextZoom);
        }
      }}
      onPointerDown={startDrag}
      onPointerMove={moveDrag}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      onPointerLeave={endDrag}
    >
      <svg
        className="map-svg"
        viewBox={`0 0 ${VIEWPORT_WIDTH} ${VIEWPORT_HEIGHT}`}
        role="img"
        aria-label="Mapa odkrytej okolicy"
      >
        <defs>
          <marker
            id="map-arrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L8,4 L0,8 z" />
          </marker>
        </defs>

        <rect className="map-background" x={0} y={0} width={VIEWPORT_WIDTH} height={VIEWPORT_HEIGHT} rx={24} />

        {visibleEdges.map((edge) => (
          <line
            key={edge.key}
            className={`map-edge${edge.bidirectional ? ' map-edge-bidirectional' : ' map-edge-oneway'}`}
            x1={edge.x1}
            y1={edge.y1}
            x2={edge.x2}
            y2={edge.y2}
            markerStart={edge.bidirectional ? 'url(#map-arrow)' : undefined}
            markerEnd="url(#map-arrow)"
            data-testid={`map-edge-${edge.key.replace(':', '-')}`}
            data-edge-key={edge.key}
            data-directionality={edge.bidirectional ? 'bidirectional' : 'oneway'}
          />
        ))}

        {visibleRooms.map((room) => {
          const isActive = activeRoom?.room_id === room.room_id;
          const title = `${room.name} | ${room.region} | ${room.x}, ${room.y}, ${room.z}`;
          const label = room.isCurrent || isActive ? room.name : '';
          return (
            <g
              key={room.room_id}
              className={`map-room${room.isCurrent ? ' is-current' : ''}${room.isFocused ? ' is-focus-target' : ''}${isActive ? ' is-active' : ''}`}
              transform={`translate(${room.screenX}, ${room.screenY})`}
              tabIndex={0}
              role="button"
              aria-label={title}
              data-testid={`map-room-${room.room_id}`}
              data-room-id={room.room_id}
              data-room-floor={room.z}
              data-room-current={room.isCurrent ? 'true' : 'false'}
              data-room-active={isActive ? 'true' : 'false'}
              onPointerEnter={() => setActiveRoomId(room.room_id)}
              onPointerLeave={() => setActiveRoomId((current) => (current === currentRoomId ? current : null))}
              onFocus={() => setActiveRoomId(room.room_id)}
              onBlur={() => setActiveRoomId((current) => (current === currentRoomId ? current : null))}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  onCenterRoom(room.room_id);
                }
              }}
              onClick={(event) => {
                event.stopPropagation();
                onCenterRoom(room.room_id);
              }}
            >
              <title>{title}</title>
              <rect
                className="map-room-hit"
                x={-roomSize}
                y={-roomSize}
                width={roomSize * 2}
                height={roomSize * 2}
                rx={2}
              />
              <rect
                className="map-room-tile"
                x={-roomSize / 2}
                y={-roomSize / 2}
                width={roomSize}
                height={roomSize}
                rx={2}
                strokeWidth={roomStrokeWidth}
              />
              {room.verticalUp ? (
                <g className="map-level-indicator map-level-up" transform={`translate(0, ${-labelOffset * 1.2})`}>
                  <circle cx={0} cy={0} r={5 * roomLabelZoom} />
                  <text x={0} y={0} textAnchor="middle" dominantBaseline="middle">
                    ↑
                  </text>
                </g>
              ) : null}
              {room.verticalDown ? (
                <g className="map-level-indicator map-level-down" transform={`translate(0, ${labelOffset * 1.2})`}>
                  <circle cx={0} cy={0} r={5 * roomLabelZoom} />
                  <text x={0} y={0} textAnchor="middle" dominantBaseline="middle">
                    ↓
                  </text>
                </g>
              ) : null}
              {label ? (
                <g className="map-room-label" transform={`translate(${labelOffset}, ${-labelOffset * 0.85})`}>
                  <text x={0} y={0} dominantBaseline="central">
                    {label}
                  </text>
                </g>
              ) : null}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
