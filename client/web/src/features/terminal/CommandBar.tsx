import { useEffect, useRef, useState } from 'react';
import type { MutableRefObject } from 'react';
import type { AstergardWebSocketTransport } from '../../transport/AstergardWebSocketTransport';
import { useAppStore } from '../../store/AppStore';
import { MAX_COMMAND_BYTES } from '../../protocol/webProtocol';
import { isWithinCommandByteLimit } from './commandLength';

type CommandBarProps = {
  transportRef: MutableRefObject<AstergardWebSocketTransport | null>;
  disabled: boolean;
};

const HISTORY_LIMIT = 80;

export function CommandBar({ transportRef, disabled }: CommandBarProps) {
  const { dispatch } = useAppStore();
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function commitCommand(nextCommand: string) {
    const trimmed = nextCommand.trim();
    if (!trimmed) {
      return;
    }
    if (!isWithinCommandByteLimit(trimmed)) {
      dispatch({ kind: 'set-error', message: `Komenda przekracza limit ${MAX_COMMAND_BYTES} bajtów UTF-8.` });
      setCommand('');
      setHistoryIndex(null);
      queueMicrotask(() => inputRef.current?.focus());
      return;
    }
    const transport = transportRef.current;
    if (!transport) {
      dispatch({ kind: 'set-error', message: 'Transport nie jest gotowy.' });
      return;
    }
    transport.executeCommand(trimmed).catch((error) => {
      dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się wysłać komendy.' });
    });
    dispatch({ kind: 'append-terminal-input', command: trimmed });
    setHistory((current) => [trimmed, ...current.filter((entry) => entry !== trimmed)].slice(0, HISTORY_LIMIT));
    setCommand('');
    setHistoryIndex(null);
    queueMicrotask(() => inputRef.current?.focus());
  }

  return (
    <form
      className="command-bar"
      onSubmit={(event) => {
        event.preventDefault();
        if (disabled) {
          dispatch({ kind: 'set-error', message: 'Najpierw zaloguj się do sesji.' });
          return;
        }
        commitCommand(command);
      }}
    >
      <label className="sr-only" htmlFor="command-input">
        Komenda
      </label>
      <input
        id="command-input"
        ref={inputRef}
        value={command}
        onChange={(event) => {
          setCommand(event.target.value);
          setHistoryIndex(null);
        }}
        onKeyDown={(event) => {
          if (event.key === 'ArrowUp') {
            event.preventDefault();
            if (!history.length) {
              return;
            }
            const nextIndex = historyIndex === null ? 0 : Math.min(historyIndex + 1, history.length - 1);
            setHistoryIndex(nextIndex);
            setCommand(history[nextIndex] ?? '');
          }
          if (event.key === 'ArrowDown') {
            event.preventDefault();
            if (historyIndex === null) {
              return;
            }
            const nextIndex = historyIndex - 1;
            if (nextIndex < 0) {
              setHistoryIndex(null);
              setCommand('');
              return;
            }
            setHistoryIndex(nextIndex);
            setCommand(history[nextIndex] ?? '');
          }
        }}
        placeholder="Wpisz komendę i naciśnij Enter"
        disabled={disabled}
        autoComplete="off"
        spellCheck={false}
      />
      <button type="submit" disabled={disabled || !command.trim()}>
        Wyślij
      </button>
    </form>
  );
}
