"""인식 스피드 드릴 — 지문만 보고 유형 판별 (코드 없음, 문제당 1분 목표).

"암기한 문제가 달라 보인다" 문제의 직접 처방: 챕터 제목 없는 상태에서
유형 판별 자체를 반복·채점한다. 전 문항이 검증 기출 앵커(recognition.json).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from wf.store import db

BANK_PATH = Path(__file__).parent.parent / "content/recognition.json"


class RecognitionScreen(Screen):
    BINDINGS = [("escape", "back", "대시보드로")]

    def __init__(self, n_items: int = 10) -> None:
        super().__init__()
        bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
        self.types = bank["types"]
        pool = list(bank["items"])
        # 개인 인식 문항 병합 (~/.warfront2/custom/recognition/*.json — items 배열)
        custom_dir = Path.home() / ".warfront2/custom/recognition"
        if custom_dir.exists():
            for f in sorted(custom_dir.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    pool += [i for i in data.get("items", [])
                             if i.get("answer") in self.types]
                except Exception:
                    continue          # 깨진 개인 파일은 조용히 무시
        self.items = random.sample(pool, min(n_items, len(pool)))
        self.idx = 0
        self.correct_count = 0
        self.wrong: list[dict] = []
        self.phase = "question"          # question → feedback → summary
        self.current_choices: list[str] = []

    # ---------- 레이아웃 ----------
    def compose(self) -> ComposeResult:
        with Vertical(id="drill"):
            yield Static(id="drill-progress")
            yield Static(id="drill-question")
            yield Static(id="drill-choices")
            yield Static(id="drill-feedback", classes="hidden")
        yield Footer()

    def on_mount(self) -> None:
        self._show_question()

    def _build_choices(self, item: dict) -> list[str]:
        others = [t for t in self.types
                  if t not in (item["answer"], item["trap"], *item["also_ok"])]
        choices = [item["answer"], item["trap"], *random.sample(others, 2)]
        random.shuffle(choices)
        return choices

    def _show_question(self) -> None:
        item = self.items[self.idx]
        self.current_choices = self._build_choices(item)
        self.phase = "question"
        prog = Text()
        prog.append(f"인식 드릴  {self.idx + 1}/{len(self.items)}", style="bold cyan")
        prog.append("   지문만 보고 유형을 판별하라 — 1분 안에", style="dim")
        self.query_one("#drill-progress", Static).update(prog)
        q = Text()
        q.append(item["text"], style="bold")
        self.query_one("#drill-question", Static).update(q)
        ch = Text()
        for i, c in enumerate(self.current_choices, 1):
            ch.append(f"  {i}. {self.types[c]}\n")
        self.query_one("#drill-choices", Static).update(ch)
        self.query_one("#drill-feedback").add_class("hidden")

    # ---------- 입력 ----------
    def on_key(self, event: events.Key) -> None:
        if self.phase == "question" and event.key in "1234":
            event.stop()
            self._judge(self.current_choices[int(event.key) - 1])
        elif self.phase == "feedback":
            event.stop()
            self.idx += 1
            if self.idx >= len(self.items):
                self._summary()
            else:
                self._show_question()

    def _judge(self, chosen: str) -> None:
        item = self.items[self.idx]
        ok = chosen == item["answer"] or chosen in item["also_ok"]
        conn = db.connect()
        db.record_recognition(conn, item["id"], item["answer"], chosen, ok)
        conn.close()
        if ok:
            self.correct_count += 1
        else:
            self.wrong.append(item)
        fb = Text()
        if ok:
            fb.append("✓ 정답 — ", style="bold green")
        else:
            fb.append(f"✗ 오답 (선택: {self.types[chosen]}) — ", style="bold red")
        fb.append(f"{self.types[item['answer']]}\n", style="bold")
        fb.append(f"신호: {item['signals']}\n", style="yellow")
        fb.append(f"출처: {item['source']['name']}\n", style="dim")
        fb.append("아무 키 → 다음", style="dim")
        panel = self.query_one("#drill-feedback", Static)
        panel.update(fb)
        panel.remove_class("hidden")
        self.phase = "feedback"

    def _summary(self) -> None:
        self.phase = "summary"
        n = len(self.items)
        rate = round(100 * self.correct_count / n)
        s = Text()
        s.append(f"드릴 완료 — {self.correct_count}/{n} ({rate}%)\n\n", style="bold green" if rate >= 90 else "bold yellow")
        if self.wrong:
            s.append("틀린 유형 (신호를 다시 보라):\n", style="bold red")
            for it in self.wrong:
                s.append(f"  · {self.types[it['answer']]} — {it['signals']}\n")
        else:
            s.append("전부 정답. 식별 기준 90%를 넘겼다면 다음 단계로.\n")
        conn = db.connect()
        stats = db.recognition_stats(conn)
        conn.close()
        s.append(f"\n누적 인식률: {stats['rate']}% (n={stats['total']})", style="cyan")
        s.append("\nESC → 대시보드", style="dim")
        self.query_one("#drill-question", Static).update(s)
        self.query_one("#drill-choices", Static).update("")
        self.query_one("#drill-feedback").add_class("hidden")

    def action_back(self) -> None:
        from wf.screens.home import HomeScreen
        self.app.switch_screen(HomeScreen())
