"""SQLite persistence. Uses WAL + a transaction per write for reliability."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS matches(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at REAL NOT NULL,
    ended_at REAL,
    duration_s REAL,
    chests INTEGER NOT NULL DEFAULT 0,
    session_id INTEGER
);
CREATE TABLE IF NOT EXISTS chest_events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    ts REAL NOT NULL,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    delta INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at REAL NOT NULL,
    ended_at REAL
);
CREATE INDEX IF NOT EXISTS idx_matches_started ON matches(started_at);
"""


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        if self.path != ":memory:":
            self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # ---- sessions / matches ---------------------------------------------
    def start_session(self, started_at: float) -> int:
        with self.conn:
            return self.conn.execute(
                "INSERT INTO sessions(started_at) VALUES(?)", (started_at,)).lastrowid

    def end_session(self, session_id: int, ended_at: float) -> None:
        with self.conn:
            self.conn.execute("UPDATE sessions SET ended_at=? WHERE id=?", (ended_at, session_id))

    def save_match(self, summary: dict, session_id: int | None = None) -> int:
        """Persist a finished match (from ChestCounter.new_match) and its events atomically."""
        with self.conn:
            mid = self.conn.execute(
                "INSERT INTO matches(started_at, ended_at, duration_s, chests, session_id)"
                " VALUES(?,?,?,?,?)",
                (summary["started_at"], summary["ended_at"], summary["duration_s"],
                 summary["chests"], session_id)).lastrowid
            self.conn.executemany(
                "INSERT INTO chest_events(match_id, ts, confidence, source, delta) VALUES(?,?,?,?,?)",
                [(mid, e.timestamp, e.confidence, e.source, e.delta) for e in summary["events"]])
        return mid

    # ---- stats -----------------------------------------------------------
    def total_chests(self) -> int:
        return self.conn.execute("SELECT COALESCE(SUM(chests),0) FROM matches").fetchone()[0]

    def total_matches(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

    def average_per_match(self) -> float:
        n = self.total_matches()
        return round(self.total_chests() / n, 2) if n else 0.0

    def personal_best(self) -> int:
        return self.conn.execute("SELECT COALESCE(MAX(chests),0) FROM matches").fetchone()[0]

    def recent_matches(self, limit: int = 20) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM matches ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()

    def reset_statistics(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM chest_events")
            self.conn.execute("DELETE FROM matches")
            self.conn.execute("DELETE FROM sessions")

    # ---- export ----------------------------------------------------------
    def export_matches_csv(self, path: str | Path) -> int:
        rows = self.conn.execute(
            "SELECT id, started_at, ended_at, duration_s, chests FROM matches ORDER BY started_at").fetchall()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["match_id", "started_at", "ended_at", "duration_s", "chests"])
            for r in rows:
                w.writerow(list(r))
        return len(rows)
