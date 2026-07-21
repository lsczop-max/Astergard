import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { renderWithStore } from '../../test/render';
import { TerminalView } from './TerminalView';

function setViewportMetrics(viewport: HTMLElement, metrics: { scrollHeight: number; clientHeight: number; scrollTop: number }) {
  Object.defineProperty(viewport, 'scrollHeight', { configurable: true, value: metrics.scrollHeight });
  Object.defineProperty(viewport, 'clientHeight', { configurable: true, value: metrics.clientHeight });
  Object.defineProperty(viewport, 'scrollTop', { configurable: true, value: metrics.scrollTop, writable: true });
}

describe('TerminalView', () => {
  it('renders every terminal line kind without reading missing fields and keeps prompt whitespace', () => {
    const { rerender } = renderWithStore(
      <TerminalView
        lines={[
          { id: '1', kind: 'text', text: '\u001b[33mżółć\u001b[0m', segments: [{ text: 'żółć', style: { fg: 'var(--ansi-gold)' } }] },
          { id: '2', kind: 'room', text: 'Pokój: Sala' },
          { id: '3', kind: 'prompt', text: '>' },
          { id: '4', kind: 'input', text: 'spojrz' },
          { id: '5', kind: 'system', text: 'Gotowe.' },
        ]}
        prompt="> "
      />,
    );
    const promptElement = screen.getByLabelText('Prompt');
    expect(screen.getByText('żółć')).toBeInTheDocument();
    expect(screen.getByText('Pokój: Sala')).toBeInTheDocument();
    expect(screen.getByText('>', { selector: '.terminal-line' })).toBeInTheDocument();
    expect(screen.getByText('› spojrz')).toBeInTheDocument();
    expect(screen.getByText('Gotowe.')).toBeInTheDocument();
    expect(promptElement.textContent).toBe('> ');
    rerender(<TerminalView lines={[]} prompt="Wpisz komendę: > " />);
    expect(screen.getByLabelText('Prompt').textContent).toBe('Wpisz komendę: > ');
  });

  it('keeps the terminal viewport stable when the user scrolls up and resumes autoscroll near the bottom', () => {
    const { rerender, container } = render(
      <TerminalView
        lines={[
          { id: '1', kind: 'text', text: 'Linia 1', segments: [] },
          { id: '2', kind: 'text', text: 'Linia 2', segments: [] },
        ]}
        prompt="> "
      />,
    );
    const viewport = container.querySelector('.terminal-viewport') as HTMLElement;
    setViewportMetrics(viewport, { scrollHeight: 400, clientHeight: 100, scrollTop: 300 });

    rerender(
      <TerminalView
        lines={[
          { id: '1', kind: 'text', text: 'Linia 1', segments: [] },
          { id: '2', kind: 'text', text: 'Linia 2', segments: [] },
          { id: '3', kind: 'text', text: 'Linia 3', segments: [] },
        ]}
        prompt="> "
      />,
    );
    expect(viewport.scrollTop).toBe(400);

    viewport.scrollTop = 180;
    setViewportMetrics(viewport, { scrollHeight: 500, clientHeight: 100, scrollTop: 180 });
    fireEvent.scroll(viewport);

    rerender(
      <TerminalView
        lines={[
          { id: '1', kind: 'text', text: 'Linia 1', segments: [] },
          { id: '2', kind: 'text', text: 'Linia 2', segments: [] },
          { id: '3', kind: 'text', text: 'Linia 3', segments: [] },
          { id: '4', kind: 'text', text: 'Linia 4', segments: [] },
        ]}
        prompt="> "
      />,
    );
    expect(viewport.scrollTop).toBe(180);

    viewport.scrollTop = 392;
    setViewportMetrics(viewport, { scrollHeight: 520, clientHeight: 100, scrollTop: 392 });
    fireEvent.scroll(viewport);

    rerender(
      <TerminalView
        lines={[
          { id: '1', kind: 'text', text: 'Linia 1', segments: [] },
          { id: '2', kind: 'text', text: 'Linia 2', segments: [] },
          { id: '3', kind: 'text', text: 'Linia 3', segments: [] },
          { id: '4', kind: 'text', text: 'Linia 4', segments: [] },
          { id: '5', kind: 'text', text: 'Linia 5', segments: [] },
        ]}
        prompt="> "
      />,
    );
    expect(viewport.scrollTop).toBe(520);
  });
});
