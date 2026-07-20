"""career repo 싱크 — 오늘의 warfront 연습을 일일 루틴 관측에 반영.

James(2026-07-20): "warfront로 연습하면 일일 루틴 결과에 반영해."
경로: wf 세션 기록(~/.warfront2/wf.db) → career repo data/warfront-daily.json
      → git push(best-effort) → 저녁 회고·관측 콘솔이 읽음(클라우드는 GitHub만 봄).

원칙:
- 사실만 기록(세션 수·총 분·카타·모드·최고정확도). 판정(python 30분 충족 여부)은 회고가.
- push 실패는 조용히 무시(훈련 흐름 방해 금지) — 다음 세션 종료 때 재시도되는 구조.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import date
from pathlib import Path

from wf.store import db

CAREER_REPO = Path(os.environ.get("WF_CAREER_REPO", str(Path.home() / "cursor/career")))
EXPORT_REL = "data/warfront-daily.json"


def today_aggregate(conn) -> dict:
    """오늘 세션 집계 — 사실만."""
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT kata_id, mode, wpm, accuracy, elapsed FROM sessions WHERE day=?",
        (today,),
    ).fetchall()
    if not rows:
        return {}
    total_sec = sum(r[4] or 0 for r in rows)
    katas = sorted({r[0] for r in rows})
    modes = sorted({r[1] for r in rows})
    return {
        "date": today,
        "sessions": len(rows),
        "total_minutes": round(total_sec / 60, 1),
        "katas": katas,
        "modes": modes,
        "best_accuracy": max((r[3] or 0) for r in rows),
        "best_wpm": max((r[2] or 0) for r in rows),
    }


def push_records_repo() -> str:
    """wf setup으로 설정한 개인 기록 repo(~/.warfront2)에 오늘 기록 push."""
    from wf.store.db import DB_DIR
    if not (DB_DIR / ".git").exists():
        return "기록 repo 미설정"
    conn = db.connect()
    agg = today_aggregate(conn)
    conn.close()
    if not agg:
        return "오늘 세션 없음"
    rec_dir = DB_DIR / "records"
    rec_dir.mkdir(exist_ok=True)
    (rec_dir / f"{agg['date']}.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=1), encoding="utf-8")
    # 전체 세션 로그 — 새 기계에서 wf setup 시 복원의 원본
    conn2 = db.connect()
    sessions = db.dump_sessions(conn2)
    conn2.close()
    (rec_dir / "sessions.jsonl").write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in sessions), encoding="utf-8")
    def git(*a):
        return subprocess.run(["git", "-C", str(DB_DIR), *a],
                              capture_output=True, text=True, timeout=30)
    try:
        git("add", "records")
        if git("diff", "--cached", "--quiet").returncode != 0:
            git("commit", "-q", "-m",
                f"warfront 기록 {agg['date']} — {agg['sessions']}세션 {agg['total_minutes']}분")
            push = git("push", "-q", "-u", "origin", "main")
            return "기록 repo push 완료" if push.returncode == 0 else "기록 커밋됨·push 실패(다음 재시도)"
        return "변경 없음"
    except Exception as e:
        return f"기록 repo 오류 무시: {type(e).__name__}"


def export_and_push(repo: Path | None = None) -> str:
    """오늘 집계를 career repo에 기록하고 best-effort push. 반환: 상태 문자열."""
    repo = repo or CAREER_REPO
    if not (repo / ".git").exists():
        return "career repo 없음 — 싱크 생략"
    conn = db.connect()
    agg = today_aggregate(conn)
    conn.close()
    if not agg:
        return "오늘 세션 없음"

    export = repo / EXPORT_REL
    export.parent.mkdir(parents=True, exist_ok=True)
    # 날짜별 누적 파일 (기존 날짜 갱신)
    data = {}
    if export.exists():
        try:
            data = json.loads(export.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data[agg["date"]] = agg
    export.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, timeout=30)

    try:
        git("pull", "--rebase", "--autostash", "-q", "origin", "main")
        git("add", EXPORT_REL)
        diff = git("diff", "--cached", "--quiet")
        if diff.returncode != 0:  # 변경 있음
            git("commit", "-q", "-m",
                f"warfront 연습 기록 {agg['date']} — {agg['sessions']}세션 {agg['total_minutes']}분 [skip ci]")
            push = git("push", "-q", "origin", "main")
            if push.returncode == 0:
                return f"동기화 완료 — {agg['sessions']}세션 {agg['total_minutes']}분"
            return "커밋됨·push 실패(다음에 재시도)"
        return "변경 없음"
    except Exception as e:  # 훈련 흐름 방해 금지 — 조용히
        return f"싱크 오류 무시: {type(e).__name__}"


def sync_all() -> str:
    """세션 종료 시 호출 — career repo(James) + 개인 기록 repo(wf setup) 모두 best-effort.

    ★어떤 예외도 밖으로 던지지 않는다 — 싱크가 훈련 앱을 죽이면 안 됨
    (2026-07-20 실크래시: 구버전 프로세스 + 새 코드 혼합 → AttributeError → Worker 사망).
    """
    msgs = []
    for fn in (export_and_push, push_records_repo):
        try:
            m = fn()
            if m != "기록 repo 미설정":
                msgs.append(m)
        except Exception as e:
            msgs.append(f"싱크 스킵({type(e).__name__})")
    return " / ".join(msgs) if msgs else "싱크 없음"
