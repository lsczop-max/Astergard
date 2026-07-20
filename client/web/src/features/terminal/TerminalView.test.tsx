import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithStore } from '../../test/render';
import { TerminalView } from './TerminalView';

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
});
