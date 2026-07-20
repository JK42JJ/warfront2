"""WARFRONT 2 — Textual 앱 루트."""
from __future__ import annotations

from textual.app import App

from wf.screens.home import HomeScreen


class WarfrontApp(App):
    TITLE = "WARFRONT 2"

    CSS = """
    Screen { align: center middle; }

    /* ---- 홈 ---- */
    #home { align: center middle; width: 100%; height: 100%; }
    #banner { width: auto; color: $accent; text-style: bold; margin: 1 0; content-align: center middle; width: 100%; }
    #tagline { text-align: center; color: $text-muted; margin-bottom: 2; width: 100%; }
    #streak-digits { color: $warning; }
    #streak-label { text-align: center; width: 100%; margin-top: 1; }
    #menu { text-align: center; width: 100%; margin-top: 2; color: $text; }
    #spacer { height: 1; }

    /* ---- 카타 ----
       주의: Vertical/Horizontal 기본 height는 1fr(화면 채움) — auto로 강제하지
       않으면 빈 박스가 화면 전체를 먹고 다른 위젯을 화면 밖으로 밀어낸다
       (2026-07-20 화면깨짐 버그의 원인). */
    #kata { padding: 1 4; height: auto; }
    #kata-title { margin-bottom: 1; color: $accent; height: auto; }
    #think-box { height: auto; border: tall $warning; padding: 1 2; margin: 1 0; }
    #think-prompt { height: auto; margin-bottom: 1; }
    #type-box { height: auto; margin-top: 1; }
    #code-display { height: auto; border: tall $primary; padding: 1 2; }
    #stats { height: auto; margin-top: 1; align-horizontal: center; }
    #stats Digits { width: auto; margin: 0 1; }
    #stats .stat-label { width: auto; height: 3; content-align: left middle;
                         color: $text-muted; margin: 0 4 0 0; }
    .hidden { display: none; }

    /* ---- 결과 ---- */
    #result { padding: 1 4; height: auto; }
    #result-title { text-align: center; width: 100%; height: auto; margin-bottom: 1; }
    #result-stats { height: auto; width: 100%; align-horizontal: center; margin: 1 0; }
    .stat-block { width: auto; height: auto; margin: 0 4; }
    .stat-block Digits { width: auto; }
    .stat-block .stat-label { width: 100%; height: 1; text-align: center;
                              color: $text-muted; margin-top: 1; }
    #think-compare { height: auto; border: tall $warning; padding: 1 2; margin: 1 0; }
    #resources { height: auto; color: $text-muted; margin: 1 0; }
    #result-menu { text-align: center; width: 100%; height: auto; margin-top: 1; }
    """

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def run() -> None:
    WarfrontApp().run()
