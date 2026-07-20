import type { RoomInfoPayload } from '../../protocol/webProtocol';

type Props = {
  room: RoomInfoPayload | null;
};

export function RoomInfoPanel({ room }: Props) {
  if (!room) {
    return (
      <section className="panel">
        <h2>Pokój</h2>
        <p className="muted">Brak danych pokoju. Zaloguj się, aby pobrać aktualny widok.</p>
      </section>
    );
  }

  const exits = Object.entries(room.exits)
    .map(([direction, target]) => `${direction} → ${target}`)
    .join(', ');

  return (
    <section className="panel">
      <h2>Pokój</h2>
      <dl className="room-info">
        <div>
          <dt>Nazwa</dt>
          <dd>{room.name}</dd>
        </div>
        <div>
          <dt>Obszar</dt>
          <dd>{room.area}</dd>
        </div>
        <div>
          <dt>Współrzędne</dt>
          <dd>
            {room.coords.x}, {room.coords.y}, {room.coords.z}
          </dd>
        </div>
        {room.area_label ? (
          <div>
            <dt>Etykieta</dt>
            <dd>{room.area_label}</dd>
          </div>
        ) : null}
        {room.terrain ? (
          <div>
            <dt>Teren</dt>
            <dd>{room.terrain}</dd>
          </div>
        ) : null}
        <div>
          <dt>Wyjścia</dt>
          <dd>{exits || 'Brak'}</dd>
        </div>
      </dl>
    </section>
  );
}
