"""결과 — 즉시 요약(대형 숫자) + 설계 선언 vs 모범 접근 비교 + 개인최고."""
from __future__ import annotations

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
            title = "🏆 개인최고 갱신!" if self.best["new_best"] else "세션 완료"
            yield Static(f"[b]{title}[/b] — {self.kata.title}", id="result-title")
            with Horizontal(id="result-stats"):
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["wpm"])), classes="big-stat")
                    yield Static("WPM", classes="stat-label")
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["accuracy"])), classes="big-stat")
                    yield Static("정확도 %", classes="stat-label")
                with Vertical(classes="stat-block"):
                    yield Digits(str(int(s["elapsed"])), classes="big-stat")
                    yield Static("초", classes="stat-label")
            # Think-First 피드백: 내 선언 vs 모범 접근
            yield Static(
                f"🧠 [b]내 설계 선언[/b]: {self.think_answer}\n"
                f"📗 [b]모범 접근[/b]: {self.kata.think_model}",
                id="think-compare",
            )
            # 보조학습 링크 (백준·HackerRank)
            links = "\n".join(f"  · {r['name']} — [link={r['url']}]{r['url']}[/link]"
                              for r in self.kata.resources)
            yield Static(f"📚 [b]실전 링크[/b] (직접 제출):\n{links}", id="resources")
            yield Static(f"🔥 연속 {self.streak}일 · [b]⏎[/b] 홈  [b]r[/b] 다시", id="result-menu")
        yield Footer()

    def action_home(self) -> None:
        from wf.screens.home import HomeScreen
        self.app.switch_screen(HomeScreen())

    def action_retry(self) -> None:
        from wf.screens.kata import KataScreen
        self.app.switch_screen(KataScreen(self.kata, self.mode))
