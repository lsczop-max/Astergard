import { connectionStateLabel } from '../../transport/AstergardWebSocketTransport';
import type { TransportState } from '../../transport/AstergardWebSocketTransport';

type Props = {
  state: TransportState;
};

export function ConnectionStatus({ state }: Props) {
  return <span className={`status-pill status-${state}`}>{connectionStateLabel(state)}</span>;
}
