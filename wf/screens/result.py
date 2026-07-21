"""결과 — 즉시 요약(대형 숫자) + 설계 선언 vs 모범 접근 비교 + 개인최고.

주의: 콘텐츠 유래 문자열(제목·URL·사용자 입력)은 마크업 보간 금지 —
Rich Text 객체로 구성한다. (2026-07-20 MarkupError 크래시: [link=URL]에
'https://'가 들어가 파서가 죽음 — 회귀 테스트로 고정)
"""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Digits, Footer, Static

from wf.content.loader import Kata
from wf.store import db


class ResultScreen(Screen):
    BINDINGS = [
        ("enter", "home", "홈으로"),
        ("r", "retry", "다시"),
    ]

    def __init__(self, kata: Kata, mode: str, summary: dict, think_answer: str) -> None:
        super().__init__()
        self.kata = kata
        self.mode = mode
        self.summary = summary
        self.think_answer = think_answer
        conn = db.connect()
        self.best = db.record_session(conn, kata.id, mode, summary, think_answer)
        self.streak = db.get_streak(conn)
        conn.close()

    def compose(self) -> ComposeResult:
        s = self.summary
        with Vertical(id="result"):
            title = Text()
            title.append("🏆 개인최고 갱신!  " if self.best["new_best"] else "세션 완료  ",
                         style="bold green")
            title.append(self.kata.title, style="bold")
            yield Static(title, id="result-title")

            with Horizontal(id="result-stats"):
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["wpm"])), classes="big-stat")
                    yield Static("타속 WPM", classes="stat-label")
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["accuracy"])), classes="big-stat")
                    yield Static("정확도 %", classes="stat-label")
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["elapsed"])), classes="big-stat")
                    yield Static("걸린 시간(초)", classes="stat-label")

            # Think-First 피드백: 내 선언 vs 모범 접근 (Text로 안전 구성)
            compare = Text()
            compare.append("🧠 내 설계 선언: ", style="bold yellow")
            compare.append(self.think_answer)
            compare.append("\n📗 모범 접근: ", style="bold green")
            compare.append(self.kata.think_model)
            yield Static(compare, id="think-compare")

            # 보조학습 링크 (백준·HackerRank) — URL은 평문(터미널이 자동 링크화)
            res = Text()
            res.append("📚 실전 링크 (직접 제출):\n", style="bold")
            for r in self.kata.resources:
                res.append(f"  · {r['name']} — ")
                res.append(r["url"], style="underline cyan")
                res.append("\n")
            yield Static(res, id="resources")

            menu = Text()
            menu.append(f"🔥 연속 {self.streak}일", style="bold")
            hints = self.summary.get("hints_used", 0)
            if hints:
                menu.append(f"   💡 힌트 {hints}회", style="yellow")
            menu.append("   ⏎ 홈(대시보드 반영)    r 다시", style="dim")
            yield Static(menu, id="result-menu")
        yield Footer()

    def on_mount(self) -> None:
        # 일일 루틴 반영: career repo에 오늘 연습 요약 push (백그라운드, 실패 무시)
        self.run_worker(self._sync_career, thread=True, exclusive=True)

    def _sync_career(self) -> None:
        try:
            from wf import sync
            msg = sync.sync_all()
            if "동기화 완료" in msg or "push 완료" in msg:
                self.app.call_from_thread(
                    self.notify, f"📊 일일 루틴 반영 — {msg}", timeout=4)
        except Exception:
            pass  # 싱크는 어떤 경우에도 훈련을 방해하지 않는다

    def action_home(self) -> None:
        from wf.screens.home import HomeScreen
        self.app.switch_screen(HomeScreen(focus_kata=self.kata.id))

    def action_retry(self) -> None:
        from wf.screens.kata import KataScreen
        self.app.switch_screen(KataScreen(self.kata, self.mode))
