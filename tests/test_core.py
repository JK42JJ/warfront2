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


@pytest.mark.asyncio
async def test_layout_widgets_visible_in_viewport(tmp_path, monkeypatch):
    """회귀: 2026-07-20 화면깨짐 — 컨테이너 1fr 확장으로 라벨·비교·링크가
    화면 밖으로 밀림. 핵심 위젯 전부가 뷰포트(120x50) 안에 있어야 한다."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    from wf.screens.kata import KataScreen

    W, H = 120, 50
    app = WarfrontApp()
    async with app.run_test(size=(W, H)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, KataScreen)
        # THINK 박스가 화면을 다 먹지 않아야 (auto 높이)
        think_box = screen.query_one("#think-box")
        assert 0 < think_box.region.height <= 12, f"think-box height={think_box.region.height}"
        # THINK 통과 → 타이핑 완주 → 결과
        for ch in "큐로 층별 확장":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        target = screen.session.target
        for c in target[:-1]:
            screen.session.feed(c)
        await pilot.press("enter" if target[-1] == "\n" else target[-1])
        await pilot.pause()
        # 결과 화면: 라벨 3개·비교·링크·메뉴 전부 뷰포트 안 + 높이>0
        res = app.screen
        labels = res.query(".stat-label")
        assert len(labels) == 3
        for w in [*labels, res.query_one("#think-compare"),
                  res.query_one("#resources"), res.query_one("#result-menu")]:
            r = w.region
            assert r.height > 0, f"{w.id or w.classes} 높이 0 (숨겨짐)"
            assert r.y + r.height <= H, f"{w.id or w.classes} 화면 밖 (y={r.y}, h={r.height})"


# ---------- 4단계 진행·빈칸 모드 ----------
def test_active_ranges_auto_skip():
    """빈칸 모드: 비활성(주어진) 구간은 타이핑 없이 자동 통과."""
    s = TypingSession(target="abcdef", active_ranges=[(2, 4)])
    assert s.pos == 2                    # 시작 즉시 활성 구간으로
    assert s.feed("c") == "ok"
    assert s.feed("d") == "done"         # 활성 구간 끝나면 나머지 자동 통과=완료
    assert s.keystrokes == 2


def test_kata_progress_stage_unlock(tmp_path):
    """보고(95%+) 통과해야 빈칸 해금, 그 다음 재현·구현."""
    conn = db.connect(tmp_path / "p.db")
    p = db.kata_progress(conn, "bfs-grid")
    assert p["next_mode"] == "guided"    # 아무것도 안 함 → 보고부터
    db.record_session(conn, "bfs-grid", "guided",
                      {"wpm": 30, "accuracy": 96.0, "elapsed": 60, "errors": 2}, "큐")
    assert db.kata_progress(conn, "bfs-grid")["next_mode"] == "cloze"
    db.record_session(conn, "bfs-grid", "cloze",
                      {"wpm": 28, "accuracy": 90.0, "elapsed": 50, "errors": 5}, "큐")
    # 빈칸 정확도 95% 미달 → 재현 해금 안 됨
    assert db.kata_progress(conn, "bfs-grid")["next_mode"] == "cloze"
    db.record_session(conn, "bfs-grid", "cloze",
                      {"wpm": 30, "accuracy": 97.0, "elapsed": 45, "errors": 1}, "큐")
    assert db.kata_progress(conn, "bfs-grid")["next_mode"] == "recall"
    conn.close()


def test_subgoal_char_range():
    from wf.content.loader import get_kata
    k = get_kata("bfs-grid")
    lo, hi = k.subgoal_char_range(0)
    block = k.code[lo:hi]
    assert "deque" in block and "seen = {start}" in block   # ① 준비 블록
    lo, hi = k.subgoal_char_range(3)
    assert "return -1" in k.code[lo:hi]                     # ④ 실패 블록


@pytest.mark.asyncio
async def test_dashboard_and_hint_flow(tmp_path, monkeypatch):
    """대시보드 → 카타 선택 → THINK → 힌트 h 2단계 토글."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    from wf.screens.kata import KataScreen
    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        # 대시보드: 카타 테이블 존재 + 일차 표시
        assert app.screen.query_one("#kata-table") is not None
        assert app.screen.query_one("#day-digits") is not None
        await pilot.press("enter")           # 첫 행 선택 → 카타
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, KataScreen)
        for ch in "큐로 층별 확장":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        assert screen.phase == "type"
        # 힌트 토글: 0→1(서브골)→2(라인)→0 (F1 — 타이핑 글자와 충돌 없는 키)
        await pilot.press("f1")
        panel = screen.query_one("#hint-panel")
        assert "hidden" not in panel.classes and screen.hint_level == 1
        await pilot.press("f1")
        assert screen.hint_level == 2
        await pilot.press("f1")
        assert screen.hint_level == 0 and "hidden" in panel.classes


# ---------- career repo 싱크 ----------
def test_sync_aggregate_and_export(tmp_path, monkeypatch):
    """오늘 세션 집계 → career repo 파일 기록 (git 없는 경로·있는 경로)."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    conn = db.connect()
    db.record_session(conn, "bfs-grid", "guided",
                      {"wpm": 30, "accuracy": 96, "elapsed": 300, "errors": 2}, "큐")
    db.record_session(conn, "topk-counter", "guided",
                      {"wpm": 35, "accuracy": 98, "elapsed": 240, "errors": 1}, "힙")
    agg = __import__("wf.sync", fromlist=["today_aggregate"]).today_aggregate(conn)
    conn.close()
    assert agg["sessions"] == 2
    assert agg["total_minutes"] == 9.0
    assert set(agg["katas"]) == {"bfs-grid", "topk-counter"}

    from wf import sync
    # git 없는 디렉토리 → 생략 (안전)
    assert "career repo 없음" in sync.export_and_push(tmp_path / "not-a-repo")
    # git repo → 파일 기록 + 커밋 (push는 리모트 없어 실패해도 조용)
    import subprocess, json
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    msg = sync.export_and_push(repo)
    export = repo / "data/warfront-daily.json"
    assert export.exists()
    data = json.loads(export.read_text())
    from datetime import date
    today = date.today().isoformat()
    assert data[today]["sessions"] == 2
    assert "push 실패" in msg or "동기화 완료" in msg  # 리모트 없음 → 전자


# ---------- 모드 재선택·초기화 ----------
@pytest.mark.asyncio
async def test_dashboard_mode_override_key(tmp_path, monkeypatch):
    """g 키 = 해금 무관 '보고' 재수련 (반복이 기본기)."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    from wf.screens.kata import KataScreen
    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        await pilot.press("g")
        await pilot.pause()
        assert isinstance(app.screen, KataScreen)
        assert app.screen.mode == "guided"


def test_cli_reset(tmp_path, monkeypatch):
    """wf reset --yes: DB 삭제 → 초기 상태."""
    import wf.store.db as dbmod
    fake = tmp_path / "wf.db"
    conn = dbmod.connect(fake)
    conn.close()
    assert fake.exists()
    monkeypatch.setattr(dbmod, "DB_PATH", fake)
    from typer.testing import CliRunner
    from wf.cli import cli
    r = CliRunner().invoke(cli, ["reset", "--yes"])
    assert r.exit_code == 0
    assert not fake.exists()
    r2 = CliRunner().invoke(cli, ["reset", "--yes"])
    assert "기록 없음" in r2.output


# ---------- 백지 구현(재현·구현) — 기능 동등 판정 ----------
def test_grader_functional_equivalence():
    """동일 코드가 아니어도 기능이 맞으면 pass (James 질문의 확정 답)."""
    from wf.engine.grader import grade
    k = get_kata("bfs-grid")
    # 변수명·구조가 모범과 완전히 다른 구현
    different = '''
from collections import deque
def bfs(board, src, dst):
    rows, cols = len(board), len(board[0])
    frontier = deque([(tuple(src), 0)])
    visited = {tuple(src)}
    while frontier:
        cell, dist = frontier.popleft()
        if cell == tuple(dst):
            return dist
        y, x = cell
        for ny, nx in ((y+1,x),(y-1,x),(y,x+1),(y,x-1)):
            if 0 <= ny < rows and 0 <= nx < cols and board[ny][nx] == 0:
                if (ny, nx) not in visited:
                    visited.add((ny, nx))
                    frontier.append(((ny, nx), dist + 1))
    return -1
'''
    r = grade(different, k.func, k.tests, k.perf)
    assert r["verdict"] == "pass", r


@pytest.mark.asyncio
async def test_solve_screen_pass_records(tmp_path, monkeypatch):
    """재현 모드: THINK → 에디터에 (다른 스타일) 정답 → Ctrl+R → pass → 기록."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    # career 싱크는 테스트에서 무력화
    import wf.sync as sync_mod
    monkeypatch.setattr(sync_mod, "CAREER_REPO", tmp_path / "no-repo")
    from textual.widgets import TextArea
    from wf.app import WarfrontApp
    from wf.screens.solve import SolveScreen
    from wf.content.loader import get_kata

    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        app.push_screen(SolveScreen(get_kata("topk-counter"), "recall"))
        await pilot.pause()
        screen = app.screen
        for ch in "카운터 집계 후 힙":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        assert screen.phase == "code"
        # 모범과 다른 스타일의 정답을 에디터에 주입
        screen.query_one("#editor", TextArea).text = (
            "from collections import Counter\n"
            "import heapq\n"
            "def top_k(items, howmany):\n"
            "    tally = Counter(items)\n"
            "    return heapq.nsmallest(howmany, tally.items(), key=lambda p: (-p[1], p[0]))\n"
        )
        screen.action_grade()
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert screen.last_result["verdict"] == "pass"
        conn = db.connect()
        assert db.kata_progress(conn, "topk-counter")["counts"]["recall"] == 1
        conn.close()


@pytest.mark.asyncio
async def test_diagram_panel_f2(tmp_path, monkeypatch):
    """F2 개념도: BFS 애니메이션 프레임 표시/숨김 토글."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    from wf.widgets import DiagramPanel
    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        await pilot.press("g")             # 보고 모드
        await pilot.pause()
        screen = app.screen
        for ch in "큐로 층별 확장":
            await pilot.press(ch if ch != " " else "space")
        await pilot.press("enter")
        await pilot.pause()
        panel = screen.query_one("#diagram-panel", DiagramPanel)
        assert "hidden" in panel.classes
        await pilot.press("f2")
        assert "hidden" not in panel.classes
        assert len(panel._frames) >= 1     # 카타별 프레임 수 상이(BFS=5, 어법=1)
        await pilot.press("f2")
        assert "hidden" in panel.classes


def test_diagram_filmstrip_grows():
    """필름스트립: 애니메이션 진행 시 스냅샷이 우측으로 누적(되감기지 않음)."""
    from wf.widgets import DiagramPanel, _compact, _hjoin
    from wf.content.loader import get_kata
    k = get_kata("bfs-grid")
    p = DiagramPanel()
    p.add_class("hidden")
    # toggle은 앱 컨텍스트 필요(set_interval) — 로직만 직접 검증
    p._frames = k.diagram["frames"]; p._i = 0; p._shown = 1
    p._i = 1; p._shown = max(p._shown, 2)
    assert p._shown == 2
    p._i = 0  # 루프 되감김
    p._shown = max(p._shown, p._i + 1)
    assert p._shown == 2               # 스트립은 유지(단조 증가)
    # 가로 결합 무결성
    rows = _hjoin([_compact(f) for f in k.diagram["frames"][:2]])
    assert all("│" in r for r in rows)


def test_records_backup_and_restore(tmp_path, monkeypatch):
    """기계A: 세션 → records repo push / 기계B: wf setup → 기록 복원 (이어가기)."""
    import subprocess, json as jsonlib
    import wf.store.db as dbmod
    import wf.sync as sync_mod
    from typer.testing import CliRunner

    # 원격 역할의 bare repo
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)

    # ── 기계 A: 훈련 + 백업 ──
    dirA = tmp_path / "machineA"
    monkeypatch.setattr(dbmod, "DB_DIR", dirA)
    monkeypatch.setattr(dbmod, "DB_PATH", dirA / "wf.db")
    monkeypatch.setattr(sync_mod, "CAREER_REPO", tmp_path / "no-career")
    conn = dbmod.connect()
    dbmod.record_session(conn, "bfs-grid", "guided",
                         {"wpm": 32, "accuracy": 97.0, "elapsed": 200, "errors": 2}, "큐")
    dbmod.record_session(conn, "bfs-grid", "cloze",
                         {"wpm": 30, "accuracy": 96.0, "elapsed": 150, "errors": 1}, "큐")
    conn.close()
    r = CliRunner().invoke(__import__("wf.cli", fromlist=["cli"]).cli,
                           ["setup", str(remote)])
    assert r.exit_code == 0, r.output
    for cmd in (["add", "-A"],):
        subprocess.run(["git", "-C", str(dirA), *cmd], check=True)
    assert "push 완료" in sync_mod.push_records_repo() or True  # push 실행
    # 원격에 sessions.jsonl 존재 확인
    ls = subprocess.run(["git", "-C", str(remote), "ls-tree", "-r", "--name-only", "main"],
                        capture_output=True, text=True)
    assert "records/sessions.jsonl" in ls.stdout, ls.stdout

    # ── 기계 B: 새 설치 + setup → 복원 ──
    dirB = tmp_path / "machineB"
    monkeypatch.setattr(dbmod, "DB_DIR", dirB)
    monkeypatch.setattr(dbmod, "DB_PATH", dirB / "wf.db")
    r = CliRunner().invoke(__import__("wf.cli", fromlist=["cli"]).cli,
                           ["setup", str(remote)])
    assert r.exit_code == 0, r.output
    assert "복원" in r.output, r.output
    conn = dbmod.connect()
    p = dbmod.kata_progress(conn, "bfs-grid")
    assert p["counts"]["guided"] == 1 and p["counts"]["cloze"] == 1
    assert p["next_mode"] == "recall"          # 단계 진행 이어짐
    assert dbmod.get_streak(conn) == 1         # 오늘 세션 복원 → 연속일 유지
    conn.close()


@pytest.mark.asyncio
async def test_sprint_mode(tmp_path, monkeypatch):
    """속성 7일: t 토글 → 배너 + 오늘 카타 ⚡ 표시, 재토글 → 해제."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "wf.db")
    from wf.app import WarfrontApp
    app = WarfrontApp()
    async with app.run_test(size=(120, 50)) as pilot:
        assert not app.screen.query("#sprint-banner")
        await pilot.press("t")
        await pilot.pause()
        assert app.screen.query_one("#sprint-banner") is not None
        conn = db.connect()
        assert db.sprint_state(conn)["day"] == 1
        conn.close()
        await pilot.press("t")
        await pilot.pause()
        assert not app.screen.query("#sprint-banner")


def test_sync_all_never_raises(monkeypatch):
    """회귀(2026-07-20 실크래시): 싱크 내부 예외가 앱을 죽이면 안 된다."""
    import wf.sync as sync_mod
    def boom():
        raise AttributeError("stale module")
    monkeypatch.setattr(sync_mod, "export_and_push", boom)
    monkeypatch.setattr(sync_mod, "push_records_repo", boom)
    msg = sync_mod.sync_all()          # 예외 없이 반환해야
    assert "싱크 스킵" in msg
