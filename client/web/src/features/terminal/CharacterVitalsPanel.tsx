import type { CharacterVitalsPayload } from '../../protocol/webProtocol';

type Props = {
  vitals: CharacterVitalsPayload | null;
};

function clampPercent(current: number, maximum: number): number {
  if (!Number.isFinite(current) || !Number.isFinite(maximum) || maximum <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(100, Math.round((current / maximum) * 100)));
}

function toneForCondition(percent: number): string {
  if (percent >= 70) {
    return 'good';
  }
  if (percent >= 35) {
    return 'warn';
  }
  return 'bad';
}

function toneForEnergy(percent: number): string {
  if (percent >= 70) {
    return 'calm';
  }
  if (percent >= 35) {
    return 'amber';
  }
  return 'low';
}

function Meter({
  label,
  percent,
  detail,
  tone,
}: {
  label: string;
  percent: number;
  detail: string;
  tone: string;
}) {
  const id = `vitals-${label.toLowerCase().replace(/\s+/g, '-')}`;
  return (
    <div className={`vitals-meter vitals-meter-${tone}`}>
      <div className="vitals-meter-head">
        <span id={id} className="vitals-label">
          {label}
        </span>
        <span className="vitals-percent" aria-hidden="true">
          {percent}%
        </span>
      </div>
      <div
        className="vitals-track"
        role="progressbar"
        aria-labelledby={id}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-valuetext={`${label}: ${detail}, ${percent}%`}
      >
        <div className="vitals-fill" style={{ width: `${percent}%` }} />
      </div>
      <p className="vitals-detail">{detail}</p>
    </div>
  );
}

export function CharacterVitalsPanel({ vitals }: Props) {
  if (!vitals) {
    return (
      <section className="panel vitals-panel">
        <h2>Stan postaci</h2>
        <p className="muted">Brak danych stanu. Zaloguj się, aby zobaczyć kondycję i energię.</p>
      </section>
    );
  }

  const conditionPercent = clampPercent(vitals.condition_current, vitals.condition_max);
  const staminaPercent = clampPercent(vitals.stamina_current, vitals.stamina_max);

  return (
    <section className="panel vitals-panel" aria-label="Stan postaci">
      <h2>Stan postaci</h2>
      <div className="vitals-grid">
        <Meter
          label="Kondycja"
          percent={conditionPercent}
          detail={vitals.condition_label ?? 'Stan zdrowia wyznacza suma ran.'}
          tone={toneForCondition(conditionPercent)}
        />
        <Meter
          label="Energia"
          percent={staminaPercent}
          detail={vitals.stamina_label ?? 'Energia pochodzi z kondycji postaci.'}
          tone={toneForEnergy(staminaPercent)}
        />
      </div>
    </section>
  );
}
