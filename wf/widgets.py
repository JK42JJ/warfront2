"""공용 위젯 — 개념도 패널(유니코드 다이어그램, 프레임 애니메이션 + 필름스트립).

James(2026-07-20): 애니메이션은 그대로 두고, 하단에 각 단계 스냅샷이
오른쪽으로 늘어나며 쌓이게 — 전 단계를 한눈에 비교(타임라인).
"""
from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"


def _compact(frame: str) -> list[str]:
    """스냅샷용 축약 — 첫 빈 줄 전(격자 부분)만."""
    lines = []
    for line in frame.splitlines():
        if not line.strip():
            break
        lines.append(line)
    return lines or frame.splitlines()[:3]


def _hjoin(blocks: list[list[str]], sep: str = "  │  ") -> list[str]:
    """블록들을 가로로 이어붙임(높이·폭 패딩)."""
    if not blocks:
        return []
    height = max(len(b) for b in blocks)
    widths = [max((len(l) for l in b), default=0) for b in blocks]
    rows = []
    for r in range(height):
        cells = []
        for b, w in zip(blocks, widths):
            cell = b[r] if r < len(b) else ""
            cells.append(cell.ljust(w))
        rows.append(sep.join(cells))
    return rows


class DiagramPanel(Static):
    """F2 개념도 — 상단: 현재 프레임(애니메이션) / 하단: 단계 필름스트립(우측 증가)."""

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frames: list[str] = []
        self._caption = ""
        self._i = 0
        self._shown = 0          # 필름스트립에 쌓인 단계 수(단조 증가 — 되감기지 않음)
        self._timer = None

    def toggle(self, diagram: dict | None) -> bool:
        """표시 토글. 반환: 표시 여부."""
        if self.has_class("hidden"):
            if not diagram or not diagram.get("frames"):
                return False
            self._frames = diagram["frames"]
            self._caption = diagram.get("caption", "")
            self._i = 0
            self._shown = 1
            self.remove_class("hidden")
            self._render_frame()
            fps = diagram.get("fps") or 0
            if len(self._frames) > 1 and fps > 0:
                self._timer = self.set_interval(1.0 / fps, self._advance)
            return True
        self.add_class("hidden")
        if self._timer:
            self._timer.stop()
            self._timer = None
        return False

    def _advance(self) -> None:
        self._i = (self._i + 1) % len(self._frames)
        self._shown = max(self._shown, self._i + 1)
        self._render_frame()

    def _render_frame(self) -> None:
        text = Text()
        text.append("🖼 개념도 — ", style="bold cyan")
        text.append(self._caption, style="cyan")
        if len(self._frames) > 1:
            text.append(f"   [{self._i + 1}/{len(self._frames)}]", style="dim")
        text.append("\n\n")
        text.append(self._frames[self._i])

        # 하단 필름스트립: 지나간 단계가 우측으로 쌓임 (다중 프레임일 때만)
        if len(self._frames) > 1:
            blocks = [_compact(f) for f in self._frames[: self._shown]]
            labels = [CIRCLED[i] if i < len(CIRCLED) else str(i + 1)
                      for i in range(self._shown)]
            widths = [max((len(l) for l in b), default=0) for b in blocks]
            label_row = "  │  ".join(lab.center(w) for lab, w in zip(labels, widths))
            text.append("\n\n")
            text.append("─ 단계 타임라인 " + "─" * 30 + "\n", style="dim")
            text.append(label_row + "\n", style="bold yellow")
            for row in _hjoin(blocks):
                text.append(row + "\n", style="grey66")
        self.update(text)


# ---- 문제 지문 렌더 (2컬럼 좌측 패널 — 실전과 동일하게 지문을 읽고 푼다) ----
_STMT_HEADERS = {
    "문제 설명", "제한사항", "입출력 예", "입출력 예 설명",
    "Problem", "Function Description", "Returns", "Constraints",
    "Sample Input", "Sample Output", "Explanation",
}


def statement_text(kata) -> Text:
    """지문을 섹션 헤더 강조와 함께 Rich Text로 렌더 (마크업 보간 금지 원칙 준수).

    하단에 출처(원형 기출) 표기 — 어느 플랫폼(백준/프로그래머스/HackerRank 등)의
    어떤 문제를 원형으로 한 자작 지문인지 밝힌다 (2026-07-21 James).
    """
    text = Text()
    body = kata.statement or (kata.desc or kata.title)
    for line in body.split("\n"):
        if line.strip() in _STMT_HEADERS:
            text.append(line + "\n", style="bold yellow")
        else:
            text.append(line + "\n")
    if kata.resources:
        en = getattr(kata, "statement_lang", "ko") == "en"
        text.append("\n" + ("Source (original problems)" if en else "출처 (원형 기출)") + "\n",
                    style="bold yellow")
        for r in kata.resources:
            text.append("· ", style="dim")
            text.append(str(r.get("name", "")) + "\n", style="cyan")
        text.append("Statement rewritten for this trainer; links in the result screen.\n"
                    if en else "지문은 자작 재구성 — 원문 링크는 결과 화면에 표시됩니다.\n",
                    style="dim")
    return text
