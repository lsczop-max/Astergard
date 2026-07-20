import { fireEvent, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { MutableRefObject } from 'react';
import type { AstergardWebSocketTransport } from '../../transport/AstergardWebSocketTransport';
import { renderWithStore } from '../../test/render';
import { useAppStore } from '../../store/AppStore';
import { MAX_COMMAND_BYTES } from '../../protocol/webProtocol';
import { CommandBar } from './CommandBar';

function createTransportRef(executeCommand: AstergardWebSocketTransport['executeCommand']): MutableRefObject<AstergardWebSocketTransport | null> {
  return {
    current: { executeCommand } as unknown as AstergardWebSocketTransport,
  };
}

function Wrapper({ transportRef, disabled = false }: { transportRef: MutableRefObject<AstergardWebSocketTransport | null>; disabled?: boolean }) {
  return (
    <>
      <CommandBar transportRef={transportRef} disabled={disabled} />
      <ErrorProbe />
    </>
  );
}

function ErrorProbe() {
  const { state } = useAppStore();
  return <div aria-live="polite">{state.userError}</div>;
}

describe('CommandBar', () => {
  it('allows 512 ASCII bytes', () => {
    const executeCommand = vi.fn().mockResolvedValue(undefined);
    renderWithStore(<Wrapper transportRef={createTransportRef(executeCommand)} />);

    const input = screen.getByLabelText('Komenda');
    fireEvent.change(input, { target: { value: 'a'.repeat(MAX_COMMAND_BYTES) } });
    fireEvent.submit(input.closest('form') as HTMLFormElement);

    expect(executeCommand).toHaveBeenCalledTimes(1);
    expect(executeCommand).toHaveBeenCalledWith('a'.repeat(MAX_COMMAND_BYTES));
    expect(input).toHaveValue('');
  });

  it('blocks 513 ASCII bytes, clears input, and does not add history', () => {
    const executeCommand = vi.fn().mockResolvedValue(undefined);
    renderWithStore(<Wrapper transportRef={createTransportRef(executeCommand)} />);

    const input = screen.getByLabelText('Komenda');
    fireEvent.change(input, { target: { value: 'a'.repeat(MAX_COMMAND_BYTES + 1) } });
    fireEvent.submit(input.closest('form') as HTMLFormElement);

    expect(executeCommand).not.toHaveBeenCalled();
    expect(screen.getByText(`Komenda przekracza limit ${MAX_COMMAND_BYTES} bajtów UTF-8.`)).toBeInTheDocument();
    expect(input).toHaveValue('');

    fireEvent.keyDown(input, { key: 'ArrowUp' });
    expect(input).toHaveValue('');
  });

  it('blocks Polish text over 512 bytes even with fewer characters', () => {
    const executeCommand = vi.fn().mockResolvedValue(undefined);
    renderWithStore(<Wrapper transportRef={createTransportRef(executeCommand)} />);

    const input = screen.getByLabelText('Komenda');
    fireEvent.change(input, { target: { value: 'ż'.repeat(300) } });
    fireEvent.submit(input.closest('form') as HTMLFormElement);

    expect(executeCommand).not.toHaveBeenCalled();
    expect(screen.getByText(`Komenda przekracza limit ${MAX_COMMAND_BYTES} bajtów UTF-8.`)).toBeInTheDocument();
    expect(input).toHaveValue('');
  });

  it('counts emoji by UTF-8 bytes', () => {
    const executeCommand = vi.fn().mockResolvedValue(undefined);
    renderWithStore(<Wrapper transportRef={createTransportRef(executeCommand)} />);

    const input = screen.getByLabelText('Komenda');
    const emojiCommand = '😀'.repeat(MAX_COMMAND_BYTES / 4);
    fireEvent.change(input, { target: { value: emojiCommand } });
    fireEvent.submit(input.closest('form') as HTMLFormElement);

    expect(executeCommand).toHaveBeenCalledTimes(1);
    expect(executeCommand).toHaveBeenCalledWith(emojiCommand);
    expect(input).toHaveValue('');
  });

  it('sends a valid trimmed Polish command', () => {
    const executeCommand = vi.fn().mockResolvedValue(undefined);
    renderWithStore(<Wrapper transportRef={createTransportRef(executeCommand)} />);

    const input = screen.getByLabelText('Komenda');
    fireEvent.change(input, { target: { value: '  idź na północ  ' } });
    fireEvent.submit(input.closest('form') as HTMLFormElement);

    expect(executeCommand).toHaveBeenCalledTimes(1);
    expect(executeCommand).toHaveBeenCalledWith('idź na północ');
    expect(input).toHaveValue('');
  });
});
