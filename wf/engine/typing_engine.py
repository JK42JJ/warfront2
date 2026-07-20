"""타이핑 엔진 — 키스트로크 판정·WPM·정확도 (순수 로직, UI 무관).

제1 원칙 "타건감"의 코어: 글자 단위 즉시 판정. 오타는 전진하지 않는다(무결점 전진
= ttyper 방식) — 정확한 키만 몸에 새긴다.

규칙:
- 대상 문자와 일치하는 키만 pos 전진. 불일치 = error 카운트(전진 안 함).
- 줄바꿈은 Enter로 침. 줄바꿈 통과 시 다음 줄 들여쓰기(선행 공백)는 자동 스킵
  (들여쓰기 타이핑은 훈련 가치가 없고 흐름만 깬다).
- WPM = (진행 문자수/5) / 경과분. 정확도 = 정타 / 총 키입력.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TypingSession:
    target: str
    pos: int = 0
    errors: int = 0
    keystrokes: int = 0
    started_at: float | None = None
    finished_at: float | None = None
    error_positions: set[int] = field(default_factory=set)

    # ---- 상태 조회 ----
    @property
    def done(self) -> bool:
        return self.pos >= len(self.target)

    @property
    def elapsed(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.finished_at if self.finished_at is not None else time.monotonic()
        return end - self.started_at

    @property
    def wpm(self) -> float:
        minutes = self.elapsed / 60
        if minutes <= 0:
            return 0.0
        return (self.pos / 5) / minutes

    @property
    def accuracy(self) -> float:
        if self.keystrokes == 0:
            return 100.0
        return max(0.0, 100.0 * (self.keystrokes - self.errors) / self.keystrokes)

    # ---- 입력 처리 ----
    def feed(self, char: str) -> str:
        """한 키 입력 판정. 반환: 'ok' | 'err' | 'done' | 'noop'."""
        if self.done:
            return "noop"
        if self.started_at is None:
            self.started_at = time.monotonic()

        expected = self.target[self.pos]
        self.keystrokes += 1

        if char == expected or (expected == "\n" and char in ("\n", "\r")):
            self.pos += 1
            self._skip_indent_after_newline(expected)
            if self.done:
                self.finished_at = time.monotonic()
                return "done"
            return "ok"

        self.errors += 1
        self.error_positions.add(self.pos)
        return "err"

    def _skip_indent_after_newline(self, consumed: str) -> None:
        """줄바꿈 직후 선행 공백 자동 통과."""
        if consumed != "\n":
            return
        while self.pos < len(self.target) and self.target[self.pos] in (" ", "\t"):
            self.pos += 1

    def summary(self) -> dict:
        return {
            "wpm": round(self.wpm, 1),
            "accuracy": round(self.accuracy, 1),
            "elapsed": round(self.elapsed, 1),
            "errors": self.errors,
            "chars": self.pos,
        }
