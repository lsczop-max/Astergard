import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { AppStoreProvider } from '../store/AppStore';

export function renderWithStore(ui: ReactElement) {
  return render(<AppStoreProvider>{ui}</AppStoreProvider>);
}
