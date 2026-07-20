"""SQLite 저장소 — 세션·개인최고·스트릭. 단일 파일 ~/.warfront2/wf.db."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_DIR = Path.home() / ".warfront2"
DB_PATH = DB_DIR / "wf.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,              -- YYYY-MM-DD (로컬)
    kata_id TEXT NOT NULL,
    mode TEXT NOT NULL,             -- guided | cloze | recall
    wpm REAL, accuracy REAL, elapsed REAL, errors INTEGER,
    think_answer TEXT,              -- THINK 게이트에서 선언한 접근
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS bests (
    kata_id TEXT NOT NULL, mode TEXT NOT NULL,
    wpm REAL, accuracy REAL,
    PRIMARY KEY (kata_id, mode)
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA)
    return conn


def record_session(conn: sqlite3.Connection, kata_id: str, mode: str,
                   summary: dict, think_answer: str = "") -> dict:
    """세션 저장 + 개인최고 갱신 여부 반환."""
    today = date.today().isoformat()
    conn.execute(
        "INSERT INTO sessions (day, kata_id, mode, wpm, accuracy, elapsed, errors, think_answer)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (today, kata_id, mode, summary["wpm"], summary["accuracy"],
         summary["elapsed"], summary["errors"], think_answer),
    )
    row = conn.execute(
        "SELECT wpm FROM bests WHERE kata_id=? AND mode=?", (kata_id, mode)
    ).fetchone()
    new_best = row is None or summary["wpm"] > row[0]
    if new_best:
        conn.execute(
            "INSERT INTO bests (kata_id, mode, wpm, accuracy) VALUES (?,?,?,?)"
            " ON CONFLICT(kata_id, mode) DO UPDATE SET wpm=excluded.wpm, accuracy=excluded.accuracy",
            (kata_id, mode, summary["wpm"], summary["accuracy"]),
        )
    conn.commit()
    return {"new_best": new_best, "prev_wpm": row[0] if row else None}


def get_streak(conn: sqlite3.Connection) -> int:
    """오늘부터 역방향 연속 훈련일 수."""
    days = {r[0] for r in conn.execute("SELECT DISTINCT day FROM sessions")}
    streak, d = 0, date.today()
    while d.isoformat() in days:
        streak += 1
        d -= timedelta(days=1)
    return streak


def today_session_count(conn: sqlite3.Connection) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE day=?", (date.today().isoformat(),)
    ).fetchone()[0]
