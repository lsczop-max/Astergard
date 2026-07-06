CREATE TABLE IF NOT EXISTS save_manifests(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scope TEXT NOT NULL,
  reason TEXT NOT NULL,
  username TEXT,
  world_save_version INTEGER NOT NULL DEFAULT 0,
  character_save_version INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  error TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_save_manifests_scope_created_at
ON save_manifests(scope, created_at);
