import { useEffect, useMemo, useRef } from 'react';
import type { TerminalLine } from '../../store/AppStore';
import { renderAnsiLine } from '../../styles/ansi';

type Props = {
  lines: TerminalLine[];
  prompt: string;
};

const LIMIT = 600;

export function TerminalView({ lines, prompt }: Props) {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const atBottomRef = useRef(true);

  const visibleLines = useMemo(() => lines.slice(-LIMIT), [lines]);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport || !atBottomRef.current) {
      return;
    }
    viewport.scrollTop = viewport.scrollHeight;
  }, [visibleLines, prompt]);

  return (
    <section className="terminal-shell panel">
      <div
        className="terminal-viewport"
        ref={viewportRef}
        onScroll={(event) => {
          const el = event.currentTarget;
          const distance = el.scrollHeight - el.scrollTop - el.clientHeight;
          atBottomRef.current = distance < 32;
        }}
      >
        <div className="terminal-lines" aria-live="polite">
          {visibleLines.map((line) => (
            <TerminalLineView key={line.id} line={line} />
          ))}
        </div>
      </div>
      <div className="terminal-prompt" aria-label="Prompt">
        <span className="prompt-label">{prompt ?? '> '}</span>
      </div>
    </section>
  );
}

function TerminalLineView({ line }: { line: TerminalLine }) {
  switch (line.kind) {
    case 'text':
      return <div className="terminal-line">{renderAnsiLine(line.segments, line.text)}</div>;
    case 'room':
      return <div className="terminal-line system">{line.text}</div>;
    case 'prompt':
      return <div className="terminal-line system">{line.text}</div>;
    case 'input':
      return <div className="terminal-line input">› {line.text}</div>;
    case 'system':
      return <div className="terminal-line system">{line.text}</div>;
    default:
      return assertNever(line);
  }
}

function assertNever(_value: never): never {
  throw new Error('Unexpected terminal line kind.');
}
