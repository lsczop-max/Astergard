import type { CSSProperties, ReactNode } from 'react';

export type AnsiStyle = {
  fg?: string;
  bg?: string;
  bold?: boolean;
  dim?: boolean;
};

export type AnsiSegment = {
  text: string;
  style: AnsiStyle;
};

export const ANSI_VARIABLE_NAMES = [
  '--ansi-black',
  '--ansi-red',
  '--ansi-red-bright',
  '--ansi-green',
  '--ansi-green-bright',
  '--ansi-gold',
  '--ansi-gold-bright',
  '--ansi-blue',
  '--ansi-blue-bright',
  '--ansi-magenta',
  '--ansi-magenta-bright',
  '--ansi-cyan',
  '--ansi-cyan-bright',
  '--ansi-dim',
  '--ansi-ink',
  '--ansi-white',
] as const;

type AnsiVariableName = (typeof ANSI_VARIABLE_NAMES)[number];

function ansiVar(name: AnsiVariableName): string {
  return `var(${name})`;
}

const COLORS: Record<number, string> = {
  30: ansiVar('--ansi-black'),
  31: ansiVar('--ansi-red'),
  32: ansiVar('--ansi-green'),
  33: ansiVar('--ansi-gold'),
  34: ansiVar('--ansi-blue'),
  35: ansiVar('--ansi-magenta'),
  36: ansiVar('--ansi-cyan'),
  37: ansiVar('--ansi-ink'),
  90: ansiVar('--ansi-dim'),
  91: ansiVar('--ansi-red-bright'),
  92: ansiVar('--ansi-green-bright'),
  93: ansiVar('--ansi-gold-bright'),
  94: ansiVar('--ansi-blue-bright'),
  95: ansiVar('--ansi-magenta-bright'),
  96: ansiVar('--ansi-cyan-bright'),
  97: ansiVar('--ansi-white'),
};

const BACKGROUND: Record<number, string> = {
  40: ansiVar('--ansi-black'),
  41: ansiVar('--ansi-red'),
  42: ansiVar('--ansi-green'),
  43: ansiVar('--ansi-gold'),
  44: ansiVar('--ansi-blue'),
  45: ansiVar('--ansi-magenta'),
  46: ansiVar('--ansi-cyan'),
  47: ansiVar('--ansi-ink'),
  100: ansiVar('--ansi-dim'),
  101: ansiVar('--ansi-red-bright'),
  102: ansiVar('--ansi-green-bright'),
  103: ansiVar('--ansi-gold-bright'),
  104: ansiVar('--ansi-blue-bright'),
  105: ansiVar('--ansi-magenta-bright'),
  106: ansiVar('--ansi-cyan-bright'),
  107: ansiVar('--ansi-white'),
};

export function parseAnsi(text: string): AnsiSegment[] {
  const segments: AnsiSegment[] = [];
  let current: AnsiStyle = {};
  let buffer = '';
  let index = 0;

  function flush() {
    if (buffer) {
      segments.push({ text: buffer, style: { ...current } });
      buffer = '';
    }
  }

  while (index < text.length) {
    const char = text[index];
    if (char === '\u001b' && text[index + 1] === '[') {
      flush();
      const end = text.indexOf('m', index);
      if (end === -1) {
        break;
      }
      const codes = text.slice(index + 2, end).split(';').filter(Boolean).map(Number);
      if (codes.length === 0) {
        current = {};
      }
      for (const code of codes) {
        if (code === 0) {
          current = {};
          continue;
        }
        if (code === 1) {
          current = { ...current, bold: true };
          continue;
        }
        if (code === 2) {
          current = { ...current, dim: true };
          continue;
        }
        if (code === 22) {
          const { bold: _bold, dim: _dim, ...rest } = current;
          current = rest;
          continue;
        }
        if (code === 39) {
          const { fg: _fg, ...rest } = current;
          current = rest;
          continue;
        }
        if (code === 49) {
          const { bg: _bg, ...rest } = current;
          current = rest;
          continue;
        }
        if (COLORS[code]) {
          current = { ...current, fg: COLORS[code] };
          continue;
        }
        if (BACKGROUND[code]) {
          current = { ...current, bg: BACKGROUND[code] };
        }
      }
      index = end + 1;
      continue;
    }
    buffer += char;
    index += 1;
  }
  flush();
  return segments;
}

export function renderAnsiLine(segments: AnsiSegment[], fallback: string): ReactNode {
  if (segments.length === 0) {
    return fallback;
  }
  return segments.map((segment, index) => {
    const style: CSSProperties = {};
    if (segment.style.fg) style.color = `var(${segment.style.fg.slice(4, -1)})`;
    if (segment.style.bg) style.backgroundColor = `var(${segment.style.bg.slice(4, -1)})`;
    if (segment.style.bold) style.fontWeight = 700;
    if (segment.style.dim) style.opacity = 0.8;
    return (
      <span key={`${index}-${segment.text}`} style={style}>
        {segment.text}
      </span>
    );
  });
}
