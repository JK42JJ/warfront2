"""카타 화면 — THINK 게이트(생각 먼저) → 타이핑(따라치기).

Think-First: 접근을 한 줄로 선언해야 코드 타이핑이 열린다.
타건감: 키 입력마다 글자 단위 즉시 색 판정 + WPM/정확도 실시간 대형 표시.
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

# 글자 상태 색 (타건감의 시각 언어)
C_DONE = "bold white"
C_ERROR_MARK = "bold red"
C_CURSOR = "black on yellow"
C_PENDING = "grey42"


class KataScreen(Screen):
    BINDINGS = [("escape", "back", "홈으로")]

    def __init__(self, kata: Kata, mode: str = "guided") -> None:
        super().__init__()
        self.kata = kata
        self.mode = mode
        self.session = TypingSession(target=kata.code)
        self.phase = "think"  # think → type
        self.think_answer = ""

    # ---------- 레이아웃 ----------
    def compose(self) -> ComposeResult:
        with Vertical(id="kata"):
            yield Static(f"[b]{self.kata.title}[/b]  ·  {self.kata.belt} 벨트  ·  {self.mode}", id="kata-title")
            # THINK 게이트
            with Vertical(id="think-box"):
                yield Static(f"🧠 [b]THINK[/b] — {self.kata.think_prompt}", id="think-prompt")
                yield Input(placeholder="내 접근을 한 줄로 선언하고 Enter (연필로 그렸다면 요점만)", id="think-input")
            # 타이핑 영역 (THINK 통과 후 표시)
            with Vertical(id="type-box", classes="hidden"):
                yield Static(id="code-display")
                with Horizontal(id="stats"):
                    yield Digits("0", id="wpm-digits")
                    yield Static("WPM", classes="stat-label")
                    yield Digits("100", id="acc-digits")
                    yield Static("ACC%", classes="stat-label")
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
        if result == "done":
            self._finish()

    def _render_code(self) -> None:
        s = self.session
        text = Text()
        for i, ch in enumerate(self.kata.code):
            visible = "⏎\n" if ch == "\n" else ch
            if i < s.pos:
                style = C_ERROR_MARK if i in s.error_positions else C_DONE
            elif i == s.pos:
                style = C_CURSOR
            else:
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
        self.app.switch_screen(
            ResultScreen(self.kata, self.mode, summary, self.think_answer)
        )

    def action_back(self) -> None:
        self.app.pop_screen()
