"""공용 위젯 — 개념도 패널(유니코드 다이어그램, 프레임 애니메이션 지원)."""
from __future__ import annotations

from rich.text import Text
from textual.widgets import Static


class DiagramPanel(Static):
    """F2 개념도 — frames가 여러 장이면 fps로 순환(BFS 파도 등)."""

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frames: list[str] = []
        self._caption = ""
        self._i = 0
        self._timer = None

    def toggle(self, diagram: dict | None) -> bool:
        """표시 토글. 반환: 표시 여부."""
        if self.has_class("hidden"):
            if not diagram or not diagram.get("frames"):
                return False
            self._frames = diagram["frames"]
            self._caption = diagram.get("caption", "")
            self._i = 0
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
        self._render_frame()

    def _render_frame(self) -> None:
        text = Text()
        text.append("🖼 개념도 — ", style="bold cyan")
        text.append(self._caption, style="cyan")
        if len(self._frames) > 1:
            text.append(f"   [{self._i + 1}/{len(self._frames)}]", style="dim")
        text.append("\n\n")
        text.append(self._frames[self._i])
        self.update(text)
