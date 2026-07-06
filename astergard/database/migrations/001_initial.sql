CREATE TABLE IF NOT EXISTS players(
  username TEXT PRIMARY KEY,
  password_hash TEXT NOT NULL,
  salt TEXT NOT NULL,
  room_id INTEGER NOT NULL,
  gold INTEGER NOT NULL,
  stats_json TEXT NOT NULL,
  skills_json TEXT NOT NULL,
  wounds_json TEXT NOT NULL,
  reputation_json TEXT NOT NULL,
  quests_json TEXT NOT NULL,
  completed_json TEXT NOT NULL,
  inventory_json TEXT NOT NULL DEFAULT '[]',
  equipment_json TEXT NOT NULL DEFAULT '{}',
  effects_json TEXT NOT NULL DEFAULT '[]'
);
