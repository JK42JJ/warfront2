"""M1 코어 검증 — 타이핑 엔진·DB·콘텐츠 로더·앱 스모크."""
import time

import pytest

from wf.content.loader import load_katas, get_kata
from wf.engine.typing_engine import TypingSession
from wf.store import db


# ---------- 타이핑 엔진 ----------
def test_typing_correct_advances():
    s = TypingSession(target="ab")
    assert s.feed("a") == "ok"
    assert s.pos == 1
    assert s.feed("b") == "done"
    assert s.done


def test_typing_wrong_does_not_advance():
    s = TypingSession(target="ab")
    assert s.feed("x") == "err"
    assert s.pos == 0
    assert s.errors == 1
    assert s.feed("a") == "ok"


def test_newline_skips_indent():
    s = TypingSession(target="a\n    b")
    s.feed("a")
    s.feed("\n")          # 줄바꿈 후 들여쓰기 4칸 자동 스킵
    assert s.target[s.pos] == "b"
    assert s.feed("b") == "done"


def test_accuracy_and_wpm():
    s = TypingSession(target="abcd")
    for ch in "axbcd":    # 오타 1회 포함
        s.feed(ch)
    assert s.done
    assert s.keystrokes == 5
    assert s.errors == 1
    assert s.accuracy == pytest.approx(80.0)
    assert s.wpm > 0


# ---------- DB ----------
def test_db_session_best_streak(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    r1 = db.record_session(conn, "bfs-grid", "guided",
                           {"wpm": 30.0, "accuracy": 95.0, "elapsed": 60.0, "errors": 3}, "큐")
    assert r1["new_best"] is True
    r2 = db.record_session(conn, "bfs-grid", "guided",
                           {"wpm": 25.0, "accuracy": 97.0, "elapsed": 60.0, "errors": 1}, "큐")
    assert r2["new_best"] is False       # WPM 낮으면 갱신 아님
    assert db.get_streak(conn) == 1      # 오늘 세션 존재
    assert db.today_session_count(conn) == 2
    conn.close()


# ---------- 콘텐츠 ----------
def test_load_katas():
    katas = load_katas()
    assert len(katas) >= 2
    k = get_kata("bfs-grid")
    assert "deque" in k.code
    assert k.think_prompt and k.think_model
    assert all("url" in r for r in k.resources)


# ---------- 앱 스모크 (Textual headless) ----------
@pytest.mark.asyncio
async def test_app_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    app = WarfrontApp()
    async with app.run_test(size=(100, 40)) as pilot:
        # 홈 → Enter → 카타 화면 THINK 게이트
        await pilot.press("enter")
        await pilot.pause()
        from wf.screens.kata import KataScreen
        assert isinstance(app.screen, KataScreen)
        assert app.screen.phase == "think"
        # THINK 게이트: 5자 미만은 거부
        await pilot.press(*"큐")
        await pilot.press("enter")
        assert app.screen.phase == "think"
        # 유효 선언 → 타이핑 해금
        for ch in "큐로 층별 확장하면 최단":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        assert app.screen.phase == "type"


@pytest.mark.asyncio
async def test_result_screen_renders_with_urls(tmp_path, monkeypatch):
    """회귀: 타이핑 완주 → Result 화면 (URL 포함 콘텐츠) 렌더가 죽지 않아야.

    2026-07-20 실사용 크래시: [link=https://...] 마크업 보간 → MarkupError.
    Result 화면까지 실제 도달시켜 렌더를 검증한다.
    """
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    from wf.screens.kata import KataScreen
    from wf.screens.result import ResultScreen

    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        await pilot.press("enter")            # 홈 → 카타
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, KataScreen)
        # THINK 통과
        for ch in "큐로 층별 확장":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        # 타이핑을 엔진에 직접 완주시킨 뒤 마지막 키만 실제 입력 → _finish 경로 실행
        target = screen.session.target
        for c in target[:-1]:
            screen.session.feed(c)
        last = target[-1]
        await pilot.press("enter" if last == "\n" else last)
        await pilot.pause()
        # Result 화면이 크래시 없이 마운트·렌더됐는가 (URL 포함 resources 위젯 존재)
        assert isinstance(app.screen, ResultScreen)
        assert app.screen.query_one("#resources") is not None
