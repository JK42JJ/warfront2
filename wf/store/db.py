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
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY, value TEXT
);
"""

MODES = ("guided", "cloze", "recall", "solve")  # 보고 → 빈칸 → 재현 → 구현
UNLOCK_ACCURACY = 95.0  # 다음 단계 해금 정확도


def course_day(conn: sqlite3.Connection) -> int:
    """50일 과정 일차 — 최초 실행일을 시작일로 기록."""
    row = conn.execute("SELECT value FROM meta WHERE key='start_date'").fetchone()
    if row is None:
        start = date.today()
        conn.execute("INSERT INTO meta (key, value) VALUES ('start_date', ?)",
                     (start.isoformat(),))
        conn.commit()
    else:
        start = date.fromisoformat(row[0])
    return (date.today() - start).days + 1


def kata_progress(conn: sqlite3.Connection, kata_id: str) -> dict:
    """카타별 모드 수행 횟수·최고 정확도·다음 단계."""
    counts = {m: 0 for m in MODES}
    best_acc = {m: 0.0 for m in MODES}
    for mode, cnt, acc in conn.execute(
        "SELECT mode, COUNT(*), MAX(accuracy) FROM sessions WHERE kata_id=? GROUP BY mode",
        (kata_id,),
    ):
        if mode in counts:
            counts[mode] = cnt
            best_acc[mode] = acc or 0.0
    # 다음 단계: 이전 단계를 해금 정확도로 통과했을 때만 전진
    next_mode = MODES[0]
    for i, m in enumerate(MODES[:-1]):
        if counts[m] > 0 and best_acc[m] >= UNLOCK_ACCURACY:
            next_mode = MODES[i + 1]
        else:
            break
    return {"counts": counts, "best_acc": best_acc, "next_mode": next_mode}


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


def dump_sessions(conn: sqlite3.Connection) -> list[dict]:
    """전체 세션을 복원 가능한 형태로 덤프 (records repo 백업용)."""
    rows = conn.execute(
        "SELECT day, kata_id, mode, wpm, accuracy, elapsed, errors, think_answer, created_at"
        " FROM sessions ORDER BY id").fetchall()
    keys = ["day", "kata_id", "mode", "wpm", "accuracy", "elapsed", "errors",
            "think_answer", "created_at"]
    return [dict(zip(keys, r)) for r in rows]


def import_sessions(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """백업 세션을 DB로 복원 — bests 재계산, 시작일은 최초 세션일로."""
    if not rows:
        return 0
    for r in rows:
        conn.execute(
            "INSERT INTO sessions (day, kata_id, mode, wpm, accuracy, elapsed, errors,"
            " think_answer, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (r["day"], r["kata_id"], r["mode"], r.get("wpm"), r.get("accuracy"),
             r.get("elapsed"), r.get("errors"), r.get("think_answer", ""),
             r.get("created_at")))
    # bests 재계산
    conn.execute("DELETE FROM bests")
    conn.execute(
        "INSERT INTO bests (kata_id, mode, wpm, accuracy)"
        " SELECT kata_id, mode, MAX(wpm), MAX(accuracy) FROM sessions GROUP BY kata_id, mode")
    # 50일 시작일 = 최초 세션일 (이어가기)
    first_day = conn.execute("SELECT MIN(day) FROM sessions").fetchone()[0]
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('start_date', ?)",
                 (first_day,))
    conn.commit()
    return len(rows)
