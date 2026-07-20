"""타이핑 엔진 — 키스트로크 판정·WPM·정확도 (순수 로직, UI 무관).

제1 원칙 "타건감"의 코어: 글자 단위 즉시 판정. 오타는 전진하지 않는다(무결점 전진
= ttyper 방식) — 정확한 키만 몸에 새긴다.

규칙:
- 대상 문자와 일치하는 키만 pos 전진. 불일치 = error 카운트(전진 안 함).
- 줄바꿈은 Enter로 침. 줄바꿈 통과 시 다음 줄 들여쓰기(선행 공백)는 자동 스킵
  (들여쓰기 타이핑은 훈련 가치가 없고 흐름만 깬다).
- 공백 유연화(2026-07-20, James): 문법이 아닌 띄어쓰기까지 동일할 필요는 없다.
  · 대상의 '선택적 공백'(줄 중간, 문자열 밖)은 다음 글자를 바로 쳐도 자동 통과
  · 대상에 없는 자리에서 공백을 쳐도 오타로 세지 않음(무시)
  · 단, 문자열 리터럴 안의 공백은 의미가 있으므로 엄격 일치
- WPM = (진행 문자수/5) / 경과분. 정확도 = 정타 / 총 키입력.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TypingSession:
    target: str
    active_ranges: list[tuple[int, int]] | None = None  # None=전체 타이핑, 지정 시 구간 밖 자동 통과(빈칸 모드)
    pos: int = 0
    errors: int = 0
    keystrokes: int = 0
    started_at: float | None = None
    finished_at: float | None = None
    error_positions: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        self._auto_advance()  # 시작 지점이 비활성 구간이면 활성 구간까지 자동 이동

    def is_active(self, i: int) -> bool:
        if self.active_ranges is None:
            return True
        return any(lo <= i < hi for lo, hi in self.active_ranges)

    def _auto_advance(self) -> None:
        """비활성 구간(주어진 코드)은 타이핑 없이 통과."""
        while self.pos < len(self.target) and not self.is_active(self.pos):
            self.pos += 1

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

    # ---- 공백 유연화 도우미 ----
    def _in_string(self, i: int) -> bool:
        """위치 i가 문자열 리터럴 안인가 — 현재 줄의 따옴표 짝으로 판정."""
        line_start = self.target.rfind("\n", 0, i) + 1
        sq = dq = 0
        j = line_start
        while j < i:
            ch = self.target[j]
            if ch == "\\":
                j += 2
                continue
            if ch == "'" and dq % 2 == 0:
                sq += 1
            elif ch == '"' and sq % 2 == 0:
                dq += 1
            j += 1
        return sq % 2 == 1 or dq % 2 == 1

    def _optional_space(self, i: int) -> bool:
        """대상 위치 i의 공백이 '스타일 공백'인가 (줄 중간 + 문자열 밖)."""
        if self.target[i] != " ":
            return False
        line_start = self.target.rfind("\n", 0, i) + 1
        if set(self.target[line_start:i]) <= {" ", "\t"}:
            return False          # 들여쓰기(선행 공백)는 별도 자동 스킵 대상
        return not self._in_string(i)

    # ---- 입력 처리 ----
    def feed(self, char: str) -> str:
        """한 키 입력 판정. 반환: 'ok' | 'err' | 'done' | 'noop'."""
        if self.done:
            return "noop"
        if self.started_at is None:
            self.started_at = time.monotonic()

        expected = self.target[self.pos]

        # 여분 공백: 대상에 없는 자리의 스페이스는 무시 (오타 아님, 카운트 없음)
        if char == " " and expected not in (" ",) and not self._in_string(self.pos):
            return "noop"

        # 선택적 공백 건너뛰기: 다음 실제 글자를 바로 친 경우
        if char != " " and self._optional_space(self.pos):
            skip = self.pos
            while skip < len(self.target) and self.target[skip] == " " and self._optional_space(skip):
                skip += 1
            if skip < len(self.target) and (
                self.target[skip] == char
                or (self.target[skip] == "\n" and char in ("\n", "\r"))
            ):
                self.pos = skip   # 공백들 통과 후 아래 정상 판정으로

        expected = self.target[self.pos]
        self.keystrokes += 1

        if char == expected or (expected == "\n" and char in ("\n", "\r")):
            self.pos += 1
            self._skip_indent_after_newline(expected)
            self._auto_advance()
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
