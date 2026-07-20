type StatusBannerProps = {
  message: string | null;
  kind: 'info' | 'error';
};

export function StatusBanner({ message, kind }: StatusBannerProps) {
  if (!message) {
    return null;
  }

  return (
    <div className={`status-banner status-${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {message}
    </div>
  );
}
