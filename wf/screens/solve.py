"""백지 구현 화면 — 재현(recall)·구현(solve) 모드.

판정 철학(James + 리서치, 2026-07-20): 재현은 축자 암기가 아니라 스키마 인출 —
**동일 코드가 아니어도 테스트를 통과(기능 동등)하면 pass.** 변수명·구조 자유.
효율성은 대형 입력 타임아웃 게이트(기대 복잡도는 표기만).

흐름: THINK 게이트 → 백지 에디터(시그니처만 제공) → Ctrl+R 채점 →
케이스별 ✅/❌ + 효율성 + verdict → pass면 기록·해금.
"""
from __future__ import annotations

import time

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, Static, TextArea

from wf.content.loader import Kata
from wf.store import db
from wf.widgets import DiagramPanel, statement_text

MODE_KO = {"recall": "안 보고 재현", "solve": "스스로 구현"}


def starter_code(kata: Kata) -> str:
    """모범코드에서 시그니처(def 줄)만 추출 — 백지 + 빈 함수 뼈대."""
    for line in kata.code.splitlines():
        if line.startswith("def "):
            return f"{line}\n    ...\n"
    return "# 함수를 작성하세요\n"


class SolveScreen(Screen):
    BINDINGS = [
        Binding("ctrl+r", "grade", "채점 실행", priority=True),
        Binding("f1", "hint", "힌트(서브골)", priority=True),
        Binding("f2", "diagram", "개념도", priority=True),
        Binding("escape", "back", "홈으로", priority=True),
    ]

    def __init__(self, kata: Kata, mode: str = "recall") -> None:
        super().__init__()
        self.kata = kata
        self.mode = mode
        self.phase = "think"
        self.think_answer = ""
        self.hint_level = 0
        self.hints_used = 0
        self.started_at: float | None = None
        self.last_result: dict | None = None
        self.recorded = False

    def compose(self) -> ComposeResult:
        title = Text()
        title.append(self.kata.title, style="bold")
        title.append(f"  ·  {MODE_KO.get(self.mode, self.mode)}")
        if self.kata.expected_complexity:
            title.append(f"  ·  기대 복잡도 {self.kata.expected_complexity}", style="cyan")
        prompt = Text()
        prompt.append("🧠 THINK — ", style="bold yellow")
        prompt.append(self.kata.think_prompt)
        desc = Text()
        desc.append("기능이 맞으면 pass — 변수명·구현 방식 자유. Ctrl+R 채점", style="dim")
        stmt = Static(statement_text(self.kata), id="stmt-panel")
        stmt.border_title = "문제" if self.kata.statement_lang != "en" else "Problem"
        with Vertical(id="solve"):
            yield Static(title, id="kata-title")
            with Horizontal(id="twocol"):
                yield stmt
                with Vertical(id="right-col"):
                    with Vertical(id="think-box"):
                        yield Static(prompt, id="think-prompt")
                        yield Input(placeholder="지문을 읽고 내 접근을 한 줄로 선언 후 Enter", id="think-input")
                    with Vertical(id="solve-box", classes="hidden"):
                        yield Static(desc, id="solve-desc")
                        yield TextArea.code_editor(starter_code(self.kata),
                                                   language="python", id="editor")
                        yield Static(id="hint-panel", classes="hidden")
                        yield DiagramPanel(id="diagram-panel", classes="hidden")
                        yield Static(id="grade-panel", classes="hidden")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#think-input", Input).focus()

    # ---------- THINK 게이트 ----------
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.phase != "think":
            return
        answer = event.value.strip()
        if len(answer) < 5:
            self.notify("접근을 먼저 생각해서 선언해야 열립니다 (5자 이상)", severity="warning")
            return
        self.think_answer = answer
        self.phase = "code"
        self.started_at = time.monotonic()
        self.query_one("#think-box").add_class("hidden")
        self.query_one("#solve-box").remove_class("hidden")
        self.query_one("#editor", TextArea).focus()

    # ---------- 힌트 (F1 — 서브골 구조만; 코드는 안 보여줌) ----------
    def action_hint(self) -> None:
        if self.phase != "code":
            return
        panel = self.query_one("#hint-panel", Static)
        if self.hint_level == 0:
            self.hint_level = 1
            self.hints_used += 1
            text = Text()
            text.append("💡 서브골 (구현 순서 힌트)\n", style="bold yellow")
            for sg in self.kata.subgoals:
                text.append(f"  {sg['label']}\n")
            panel.update(text)
            panel.remove_class("hidden")
        else:
            self.hint_level = 0
            panel.add_class("hidden")

    def action_diagram(self) -> None:
        if self.phase not in ("type", "code"):
            return
        self.query_one("#diagram-panel", DiagramPanel).toggle(self.kata.diagram)

    # ---------- 채점 (Ctrl+R) ----------
    def action_grade(self) -> None:
        if self.phase != "code":
            return
        self.query_one("#grade-panel", Static).update(Text("⏳ 채점 중… (히든 케이스 + 효율성)"))
        self.query_one("#grade-panel").remove_class("hidden")
        self.run_worker(self._grade_worker, thread=True, exclusive=True)

    def _grade_worker(self) -> None:
        from wf.engine.grader import grade
        code = self.query_one("#editor", TextArea).text
        result = grade(code, self.kata.func, self.kata.tests, self.kata.perf)
        self.last_result = result
        self.app.call_from_thread(self._show_result, result)

    def _show_result(self, r: dict) -> None:
        text = Text()
        if r["verdict"] == "pass":
            text.append(f"✅ PASS — {r['passed']}/{r['total']} 케이스 통과", style="bold green")
        elif r["verdict"] == "timeout":
            text.append(f"⏱ TIMEOUT — {r.get('detail','')}", style="bold red")
        elif r["verdict"] == "crash":
            text.append(f"💥 실행 실패 — {r.get('detail','')}", style="bold red")
        else:
            text.append(f"❌ FAIL — {r['passed']}/{r['total']} 케이스", style="bold red")
        for i, c in enumerate(r["cases"], 1):
            if c.get("ok"):
                text.append(f"\n  #{i} ✅")
            elif "error" in c:
                text.append(f"\n  #{i} ❌ {c['error']}", style="red")
            else:
                text.append(f"\n  #{i} ❌ 기대 {c['expected']} → 결과 {c['got']}", style="red")
        perf = r.get("perf")
        if perf:
            mark = "✅" if perf.get("ok") else "❌ 효율성 탈락(느림)"
            text.append(f"\n  ⚡ 효율성: {perf.get('elapsed','?')}s / 제한 {perf['limit']}s {mark}",
                        style="green" if perf.get("ok") else "red")
            text.append(f"  (기대 {self.kata.expected_complexity})", style="dim cyan")
        if r["verdict"] == "pass" and not self.recorded:
            self.recorded = True
            elapsed = time.monotonic() - (self.started_at or time.monotonic())
            summary = {"wpm": 0.0, "accuracy": 100.0 * r["passed"] / max(r["total"], 1),
                       "elapsed": round(elapsed, 1), "errors": r["total"] - r["passed"],
                       "hints_used": self.hints_used}
            conn = db.connect()
            db.record_session(conn, self.kata.id, self.mode, summary, self.think_answer)
            conn.close()
            self.run_worker(self._sync_career, thread=True)
            text.append("\n\n📗 모범 접근: ", style="bold green")
            text.append(self.kata.think_model)
            text.append("\n⏎ 계속 수련하거나 ESC로 대시보드 (기록 반영됨)", style="dim")
        self.query_one("#grade-panel", Static).update(text)

    def _sync_career(self) -> None:
        try:
            from wf import sync
            msg = sync.sync_all()
            if "동기화 완료" in msg or "push 완료" in msg:
                self.app.call_from_thread(
                    self.notify, f"📊 일일 루틴 반영 — {msg}", timeout=4)
        except Exception:
            pass  # 싱크는 어떤 경우에도 훈련을 방해하지 않는다

    def action_back(self) -> None:
        from wf.screens.home import HomeScreen
        self.app.switch_screen(HomeScreen())
