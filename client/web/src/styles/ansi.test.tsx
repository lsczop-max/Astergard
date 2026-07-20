// @vitest-environment node

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { parseAnsi, renderAnsiLine, ANSI_VARIABLE_NAMES } from './ansi';

const ansiCssPath = join(dirname(fileURLToPath(import.meta.url)), 'global.css');
const globalCss = readFileSync(ansiCssPath, 'utf8');

function extractAnsiNames(css: string): string[] {
  return Array.from(new Set(css.match(/--ansi-[a-z-]+/g) ?? [])).sort();
}

describe('ANSI styles', () => {
  it('keeps renderer variables in sync with global CSS', () => {
    expect(extractAnsiNames(globalCss)).toEqual([...ANSI_VARIABLE_NAMES].sort());
  });

  it('renders red, green, gold, blue, and reset correctly', () => {
    const markup = renderToStaticMarkup(
      <div>
        {renderAnsiLine(
          parseAnsi('\u001b[31mCzerwony\u001b[0m \u001b[32mZielony\u001b[0m \u001b[33mZloty\u001b[0m \u001b[34mNiebieski\u001b[0m \u001b[0mBazowy'),
          '',
        )}
      </div>,
    );

    expect(markup).toContain('<span style="color:var(--ansi-red)">Czerwony</span>');
    expect(markup).toContain('<span style="color:var(--ansi-green)">Zielony</span>');
    expect(markup).toContain('<span style="color:var(--ansi-gold)">Zloty</span>');
    expect(markup).toContain('<span style="color:var(--ansi-blue)">Niebieski</span>');
    expect(markup).toContain('<span>Bazowy</span>');
  });
});
