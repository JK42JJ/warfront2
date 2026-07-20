"""홈 — 오늘의 훈련. 마찰 제로: Enter 한 번으로 시작."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Digits, Footer, Static

from wf.content.loader import load_katas
from wf.store import db

BANNER = """\
██╗    ██╗ █████╗ ██████╗ ███████╗██████╗  ██████╗ ███╗   ██╗████████╗
██║    ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔═══██╗████╗  ██║╚══██╔══╝
██║ █╗ ██║███████║██████╔╝█████╗  ██████╔╝██║   ██║██╔██╗ ██║   ██║
██║███╗██║██╔══██║██╔══██╗██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║   ██║
╚███╔███╔╝██║  ██║██║  ██║██║     ██║  ██║╚██████╔╝██║ ╚████║   ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝  2"""


class HomeScreen(Screen):
    BINDINGS = [
        ("enter", "start", "오늘의 카타 시작"),
        ("q", "quit_app", "종료"),
    ]

    def compose(self) -> ComposeResult:
        conn = db.connect()
        streak = db.get_streak(conn)
        today_n = db.today_session_count(conn)
        conn.close()

        with Vertical(id="home"):
            yield Static(BANNER, id="banner")
            yield Static("생각 먼저. 구현은 그 다음. — 50일 코테 합격 훈련", id="tagline")
            with Center():
                yield Digits(str(streak), id="streak-digits")
            yield Static(f"🔥 연속 훈련 [b]{streak}일[/b]  ·  오늘 세션 [b]{today_n}[/b]회", id="streak-label")
            yield Static("", id="spacer")
            yield Static("[b]⏎ Enter[/b] — 오늘의 카타 시작      [b]q[/b] — 종료", id="menu")
        yield Footer()

    def action_start(self) -> None:
        katas = load_katas()
        if not katas:
            self.notify("카타 콘텐츠가 없습니다", severity="error")
            return
        # M1: 첫 카타부터. (M3에서 FSRS 스케줄러가 '오늘의 카드' 선정)
        from wf.screens.kata import KataScreen
        self.app.push_screen(KataScreen(katas[0]))

    def action_quit_app(self) -> None:
        self.app.exit()
