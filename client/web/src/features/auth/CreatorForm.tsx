import { useEffect, useState } from 'react';
import type { MutableRefObject } from 'react';
import type { AstergardWebSocketTransport } from '../../transport/AstergardWebSocketTransport';
import { useAppStore } from '../../store/AppStore';

type CreatorFormProps = {
  transportRef: MutableRefObject<AstergardWebSocketTransport | null>;
};

export function CreatorForm({ transportRef }: CreatorFormProps) {
  const { state, dispatch } = useAppStore();
  const [value, setValue] = useState('');

  const creator = state.creator;

  useEffect(() => {
    setValue('');
  }, [creator?.step.step_id]);

  if (!creator) {
    return null;
  }

  const step = creator.step;

  async function submitCurrentStep() {
    const transport = transportRef.current;
    if (!transport) {
      dispatch({ kind: 'set-error', message: 'Transport nie jest gotowy.' });
      return;
    }
    dispatch({ kind: 'clear-error' });
    try {
      await transport.submitCreator(step.step_id, value);
    } catch (error) {
      dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się wysłać odpowiedzi kreatora.' });
    }
  }

  async function goBack() {
    const transport = transportRef.current;
    if (!transport) {
      dispatch({ kind: 'set-error', message: 'Transport nie jest gotowy.' });
      return;
    }
    dispatch({ kind: 'clear-error' });
    try {
      await transport.goBackInCreator(step.step_id);
    } catch (error) {
      dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się cofnąć kroku.' });
    }
  }

  async function cancel() {
    const transport = transportRef.current;
    if (!transport) {
      dispatch({ kind: 'set-error', message: 'Transport nie jest gotowy.' });
      return;
    }
    dispatch({ kind: 'clear-error' });
    try {
      await transport.cancelCreator(step.step_id);
    } catch (error) {
      dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się anulować kreatora.' });
    }
  }

  return (
    <form
      className="panel creator-form"
      onSubmit={(event) => {
        event.preventDefault();
        void submitCurrentStep();
      }}
    >
      <h2>Kreator postaci</h2>
      <p className="muted">
        Konto: <strong>{creator.username}</strong>
      </p>
      <h3>{step.title}</h3>
      <div className="creator-prompt" style={{ whiteSpace: 'pre-line' }}>
        {step.prompt}
      </div>
      <div className="field">
        <label htmlFor="creator-step-input">
          {step.input_type === 'choice' ? 'Wybór' : step.input_type === 'number' ? 'Wartość liczbowa' : 'Odpowiedź'}
        </label>
        {step.input_type === 'choice' ? (
          <select
            id="creator-step-input"
            value={value}
            onChange={(event) => setValue(event.target.value)}
          >
            <option value="">Wybierz...</option>
            {step.choices?.map((choice) => (
              <option key={choice.value} value={choice.value}>
                {choice.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            id="creator-step-input"
            type={step.input_type === 'number' ? 'number' : 'text'}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
        )}
      </div>
      <div className="button-row">
        <button type="submit" disabled={step.input_type === 'choice' ? value.trim() === '' : value.trim() === ''}>
          Zatwierdź
        </button>
        <button type="button" className="ghost-button" onClick={() => void goBack()} disabled={!step.back_available}>
          Wstecz
        </button>
        <button type="button" className="ghost-button" onClick={() => void cancel()} disabled={!step.cancel_available}>
          Anuluj
        </button>
      </div>
    </form>
  );
}
