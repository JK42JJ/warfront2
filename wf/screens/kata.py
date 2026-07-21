"""카타 화면 — THINK 게이트(생각 먼저) → 타이핑 (보고/빈칸/재현 모드).

Think-First: 접근을 한 줄로 선언해야 코드 타이핑이 열린다.
타건감: 키 입력마다 글자 단위 즉시 색 판정 + WPM/정확도 실시간 대형 표시.
모드(faded worked examples — 리서치 근거):
  guided 보고 따라치기 — 전체 코드 보임
  cloze  빈칸 채우기   — 서브골 한 블록만 가림(세션마다 로테이션), 나머지는 주어짐
  recall 안 보고 재현  — 전체 가림(줄 구조만 보임)
힌트(F1 키, 2단계): 1=서브골 블록 라벨(전이 효과 실증) → 2=+현재 줄 자연어 설명(최후 수단)
"""
from __future__ import annotations

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Digits, Footer, Input, Static

from wf.content.loader import Kata
from wf.engine.typing_engine import TypingSession
from wf.widgets import DiagramPanel, statement_text
from wf.store import db

# 글자 상태 색 (타건감의 시각 언어)
C_DONE = "bold white"
C_ERROR_MARK = "bold red"
C_CURSOR = "black on yellow"
C_PENDING = "grey42"
C_GIVEN = "grey58"        # 빈칸 모드에서 '주어진' 코드
MASK = "·"                 # 가려진 글자


class KataScreen(Screen):
    BINDINGS = [
        ("escape", "back", "홈으로"),
        ("f1", "hint", "힌트(단계)"),
        ("f2", "diagram", "개념도"),
    ]

    def __init__(self, kata: Kata, mode: str = "guided") -> None:
        super().__init__()
        self.kata = kata
        self.mode = mode
        self.hint_level = 0
        self.hints_used = 0
        active = self._active_ranges()
        self.session = TypingSession(target=kata.code, active_ranges=active)
        self.phase = "think"  # think → type
        self.think_answer = ""

    def _active_ranges(self) -> list[tuple[int, int]] | None:
        """모드별 타이핑 대상 구간. guided/recall=전체, cloze=서브골 1블록(로테이션)."""
        if self.mode != "cloze" or not self.kata.subgoals:
            return None
        conn = db.connect()
        done = db.kata_progress(conn, self.kata.id)["counts"]["cloze"]
        conn.close()
        idx = done % len(self.kata.subgoals)
        self.cloze_idx = idx
        return [self.kata.subgoal_char_range(idx)]

    # ---------- 레이아웃 ----------
    def compose(self) -> ComposeResult:
        title = Text()
        title.append(self.kata.title, style="bold")
        mode_ko = {"guided": "보고 따라치기", "cloze": "빈칸 채우기", "recall": "안 보고 재현"}
        title.append(f"  ·  {self.kata.belt} 벨트  ·  {mode_ko.get(self.mode, self.mode)}")
        if self.kata.expected_complexity:
            title.append(f"  ·  기대 복잡도 {self.kata.expected_complexity}", style="cyan")
        prompt = Text()
        prompt.append("🧠 THINK — ", style="bold yellow")
        prompt.append(self.kata.think_prompt)
        stmt = Static(statement_text(self.kata), id="stmt-panel")
        stmt.border_title = "문제" if self.kata.statement_lang != "en" else "Problem"
        with Vertical(id="kata"):
            yield Static(title, id="kata-title")
            with Horizontal(id="twocol"):
                yield stmt
                with Vertical(id="right-col"):
                    with Vertical(id="think-box"):
                        yield Static(prompt, id="think-prompt")
                        yield Input(placeholder="지문을 읽고 내 접근을 한 줄로 선언 후 Enter (연필로 그렸다면 요점만)", id="think-input")
                    with Vertical(id="type-box", classes="hidden"):
                        yield Static(id="code-display")
                        yield Static(id="hint-panel", classes="hidden")
                        yield DiagramPanel(id="diagram-panel", classes="hidden")
                        with Horizontal(id="stats"):
                            yield Digits("0", id="wpm-digits")
                            yield Static("타속 WPM", classes="stat-label")
                            yield Digits("100", id="acc-digits")
                            yield Static("정확도 %", classes="stat-label")
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
        self.phase = "type"
        self.query_one("#think-box").add_class("hidden")
        self.query_one("#type-box").remove_class("hidden")
        self._render_code()
        self.set_interval(0.5, self._refresh_stats)
        self.set_focus(None)  # 키 이벤트를 화면이 직접 받는다

    # ---------- 힌트 (F1 — 2단계) ----------
    def action_hint(self) -> None:
        if self.phase != "type":
            return
        self.hint_level = (self.hint_level + 1) % 3
        if self.hint_level > 0:
            self.hints_used += 1
        panel = self.query_one("#hint-panel", Static)
        if self.hint_level == 0:
            panel.add_class("hidden")
            return
        panel.remove_class("hidden")
        text = Text()
        if self.hint_level >= 1:
            text.append("💡 서브골 (구조 힌트)\n", style="bold yellow")
            for i, sg in enumerate(self.kata.subgoals):
                cur = self._current_line()
                lo, hi = sg["lines"]
                marker = "▶ " if lo <= cur <= hi else "  "
                style = "bold" if lo <= cur <= hi else "dim"
                text.append(f"{marker}{sg['label']}\n", style=style)
        if self.hint_level == 2:
            cur = self._current_line()
            note = self.kata.line_notes.get(str(cur))
            text.append("\n📝 현재 줄: ", style="bold cyan")
            text.append(note if note else "(이 줄 설명 없음)")
        panel.update(text)

    def action_diagram(self) -> None:
        if self.phase not in ("type", "code"):
            return
        self.query_one("#diagram-panel", DiagramPanel).toggle(self.kata.diagram)

    def _current_line(self) -> int:
        return self.kata.code[: self.session.pos].count("\n")

    # ---------- 타이핑 ----------
    def on_key(self, event: events.Key) -> None:
        if self.phase != "type":
            return
        s = self.session
        if event.key == "enter":
            result = s.feed("\n")
        elif event.is_printable and event.character:
            result = s.feed(event.character)
        else:
            return
        event.stop()
        self._render_code()
        if self.hint_level == 2:
            self.action_hint_refresh()
        if result == "done":
            self._finish()

    def action_hint_refresh(self) -> None:
        """레벨2 힌트는 커서 줄 이동 시 갱신."""
        level = self.hint_level
        self.hint_level = level - 1  # action_hint가 +1 하므로 보정
        self.hints_used -= 1         # 갱신은 사용 횟수에 안 셈
        self.action_hint()

    def _render_code(self) -> None:
        s = self.session
        text = Text()
        for i, ch in enumerate(self.kata.code):
            newline = ch == "\n"
            typed = i < s.pos
            active = s.is_active(i)
            if typed:
                visible = "⏎\n" if newline else ch
                style = C_ERROR_MARK if i in s.error_positions else (C_DONE if active else C_GIVEN)
            elif i == s.pos:
                visible = "⏎\n" if newline else (ch if self.mode == "guided" else MASK)
                style = C_CURSOR
            else:
                if self.mode == "guided" or not active:
                    visible = "⏎\n" if newline else ch
                    style = C_PENDING if active else C_GIVEN
                else:  # cloze 활성 블록·recall 전체: 가림 (줄 구조만 노출)
                    visible = "\n" if newline else MASK
                    style = C_PENDING
            text.append(visible, style=style)
        self.query_one("#code-display", Static).update(text)

    def _refresh_stats(self) -> None:
        s = self.session
        self.query_one("#wpm-digits", Digits).update(str(int(s.wpm)))
        self.query_one("#acc-digits", Digits).update(str(int(s.accuracy)))

    def _finish(self) -> None:
        from wf.screens.result import ResultScreen
        summary = self.session.summary()
        summary["hints_used"] = self.hints_used
        self.app.switch_screen(
            ResultScreen(self.kata, self.mode, summary, self.think_answer)
        )

    def action_back(self) -> None:
        self.app.pop_screen()
