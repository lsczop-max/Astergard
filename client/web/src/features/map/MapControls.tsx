type Props = {
  floors: number[];
  selectedFloor: number | null;
  zoom: number;
  onFloorChange: (floor: number) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onCenter: () => void;
  centerDisabled?: boolean;
};

export function MapControls({
  floors,
  selectedFloor,
  zoom,
  onFloorChange,
  onZoomIn,
  onZoomOut,
  onCenter,
  centerDisabled = false,
}: Props) {
  return (
    <div className="map-toolbar" aria-label="Sterowanie mapą">
      <div className="map-toolbar-group" aria-label="Piętra mapy">
        {floors.length === 0 ? (
          <span className="caption muted">Brak odkrytych pięter.</span>
        ) : (
          floors.map((floor) => (
            <button
              key={floor}
              type="button"
              className={`map-floor-button${floor === selectedFloor ? ' is-active' : ''}`}
              aria-label={`Piętro ${floor}`}
              aria-pressed={floor === selectedFloor}
              onClick={() => onFloorChange(floor)}
            >
              z = {floor}
            </button>
          ))
        )}
      </div>

      <div className="map-toolbar-group map-toolbar-actions">
        <button type="button" aria-label="Pomniejsz mapę" onClick={onZoomOut}>
          −
        </button>
        <span className="map-zoom-readout" aria-live="polite">
          {Math.round(zoom * 100)}%
        </span>
        <button type="button" aria-label="Powiększ mapę" onClick={onZoomIn}>
          +
        </button>
        <button type="button" aria-label="Wyśrodkuj bieżącą lokację" onClick={onCenter} disabled={centerDisabled}>
          Wyśrodkuj
        </button>
      </div>
    </div>
  );
}
