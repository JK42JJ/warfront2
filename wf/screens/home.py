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
        ("q", "quit_app", "종료"),
    ]

    def compose(self) -> ComposeResult:
        conn = db.connect()
        day = db.course_day(conn)
        streak = db.get_streak(conn)
        self._progress = {k.id: db.kata_progress(conn, k.id) for k in load_katas()}
        conn.close()

        with Vertical(id="dash"):
            head = Text()
            head.append("⚔ WARFRONT 2", style="bold cyan")
            head.append("   생각 먼저, 구현은 그 다음. 50일 코테 합격 훈련", style="dim")
            yield Static(head, id="dash-head")
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
                table.add_row(
                    kata.title, kata.desc or kata.belt,
                    str(c["guided"]), str(c["cloze"]), str(c["recall"]),
                    ("✅" if c["solve"] else "—"),
                    MODE_KO[p["next_mode"]],
                    key=kata.id,
                )
            yield table
            yield Static("⏎ 선택한 카타 시작(다음 단계 자동)  ·  힌트는 훈련 중 F1  ·  q 종료",
                         id="dash-help")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        kata_id = event.row_key.value
        from wf.content.loader import get_kata
        from wf.screens.kata import KataScreen
        kata = get_kata(kata_id)
        next_mode = self._progress[kata_id]["next_mode"]
        if next_mode == "solve":
            self.notify("구현 모드는 다음 업데이트(M2b: 채점 엔진)에서 열립니다 — 재현 반복 추천",
                        severity="information")
            next_mode = "recall"
        self.app.push_screen(KataScreen(kata, next_mode))

    def action_quit_app(self) -> None:
        self.app.exit()
