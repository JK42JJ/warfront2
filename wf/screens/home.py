"""홈 = 대시보드 — 50일 진행 + 카타별 단계 현황(보고/빈칸/재현/구현 횟수).

James 설계(2026-07-20): 앱을 열면 대시보드. 사실 기반 카운트(게임화 배제).
단계: 보고 따라치기 → 빈칸 채우기 → 안 보고 재현 → 스스로 구현 (리서치: faded worked examples)
"""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Digits, Footer, Static

from wf.content.loader import load_katas
from wf.store import db

MODE_KO = {"guided": "보고", "cloze": "빈칸", "recall": "재현", "solve": "구현"}


class HomeScreen(Screen):
    BINDINGS = [
        ("g", "open_mode('guided')", "보고"),
        ("b", "open_mode('cloze')", "빈칸"),
        ("r", "open_mode('recall')", "재현"),
        ("s", "open_mode('solve')", "구현"),
        ("t", "toggle_sprint", "속성 7일"),
        ("q", "quit_app", "종료"),
    ]

    def compose(self) -> ComposeResult:
        import json as _json
        from pathlib import Path as _Path
        conn = db.connect()
        day = db.course_day(conn)
        streak = db.get_streak(conn)
        self._progress = {k.id: db.kata_progress(conn, k.id) for k in load_katas()}
        sprint = db.sprint_state(conn)
        conn.close()
        self._sprint_plan = _json.loads(
            (_Path(__file__).parent.parent / "content/sprint.json").read_text(encoding="utf-8"))
        self._sprint = sprint
        sprint_new, sprint_review = [], []
        if sprint:
            d = str(min(sprint["day"], 7))
            day_plan = self._sprint_plan["plan"][d]
            sprint_new = day_plan.get("new", [])
            sprint_review = day_plan.get("review", [])

        with Vertical(id="dash"):
            head = Text()
            head.append("⚔ WARFRONT 2", style="bold cyan")
            head.append("   50일 코딩테스트 훈련", style="dim")
            yield Static(head, id="dash-head")
            if self._sprint:
                sd = self._sprint["day"]
                sp = Text()
                if sd <= 7:
                    d = str(sd)
                    sp.append(f"⚡ 속성 모드 D{sd}/7", style="bold yellow")
                    sp.append(f" — 오늘: {self._sprint_plan['plan'][d]['focus']}", style="yellow")
                    sp.append("   (t로 해제)", style="dim")
                else:
                    sp.append("⚡ 속성 7일 완료 — 실전 응시 단계. t로 해제", style="bold yellow")
                yield Static(sp, id="sprint-banner")
            with Horizontal(id="dash-top"):
                with Vertical(classes="dash-metric"):
                    yield Digits(f"{day}", id="day-digits")
                    yield Static(f"일차 / 50일", classes="stat-label")
                with Vertical(classes="dash-metric"):
                    yield Digits(f"{streak}", id="streak-digits")
                    yield Static("연속 훈련일", classes="stat-label")
            table = DataTable(id="kata-table", cursor_type="row")
            table.add_columns("카타", "설명", "보고", "빈칸", "재현", "구현", "다음 단계")
            for kata in load_katas():
                p = self._progress[kata.id]
                c = p["counts"]
                marker = ""
                if self._sprint:
                    if kata.id in sprint_new:
                        marker = "⚡ "
                    elif kata.id in sprint_review:
                        marker = "🔁 "
                table.add_row(
                    marker + kata.title, kata.desc or kata.belt,
                    str(c["guided"]), str(c["cloze"]), str(c["recall"]),
                    ("✅" if c["solve"] else "—"),
                    MODE_KO[p["next_mode"]],
                    key=kata.id,
                )
            yield table
            yield Static("⏎ 다음 단계 자동  ·  g 보고 / b 빈칸 / r 재현 / s 구현 (언제든 재수련)  ·  훈련 중 F1 힌트  ·  q 종료",
                         id="dash-help")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()

    def _open(self, kata_id: str, mode: str) -> None:
        from wf.content.loader import get_kata
        kata = get_kata(kata_id)
        if mode in ("recall", "solve"):     # 백지 구현 — 기능 동등 판정
            from wf.screens.solve import SolveScreen
            self.app.push_screen(SolveScreen(kata, mode))
        else:                                # 타이핑 카타 — 보고/빈칸
            from wf.screens.kata import KataScreen
            self.app.push_screen(KataScreen(kata, mode))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        kata_id = event.row_key.value
        self._open(kata_id, self._progress[kata_id]["next_mode"])

    def action_open_mode(self, mode: str) -> None:
        """선택된 카타를 지정 모드로 — 해금과 무관하게 언제든 재수련(반복이 기본기)."""
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self._open(row_key.value, mode)

    def action_toggle_sprint(self) -> None:
        conn = db.connect()
        on = db.sprint_toggle(conn)
        conn.close()
        self.notify("⚡ 속성 7일 시작 — 오늘 카타에 ⚡ 표시" if on else "속성 모드 해제 — 50일 일정으로 복귀")
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
