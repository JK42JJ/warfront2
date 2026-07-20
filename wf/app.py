"""WARFRONT 2 — Textual 앱 루트."""
from __future__ import annotations

from textual.app import App

from wf.screens.home import HomeScreen


class WarfrontApp(App):
    TITLE = "WARFRONT 2"

    CSS = """
    Screen { align: center middle; }

    /* ---- 대시보드(홈) ---- */
    #dash { padding: 1 3; height: auto; width: 100%; }
    #dash-head { height: auto; margin-bottom: 1; }
    #dash-top { height: auto; align-horizontal: center; margin-bottom: 1; }
    .dash-metric { width: auto; height: auto; margin: 0 4; }
    .dash-metric Digits { width: auto; color: $warning; }
    .dash-metric .stat-label { width: 100%; height: 1; text-align: center;
                               color: $text-muted; margin-top: 1; }
    #kata-table { height: auto; max-height: 20; margin-bottom: 1; }
    #dash-help { height: auto; color: $text-muted; text-align: center; width: 100%; }
    #hint-panel { height: auto; border: tall $success; padding: 1 2; margin-top: 1; }
    #diagram-panel { height: auto; border: tall $accent; padding: 1 2; margin-top: 1; }

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

    /* ---- 구현(solve) ---- */
    #solve { padding: 1 4; height: auto; }
    #solve-box { height: auto; }
    #solve-desc { height: auto; margin-bottom: 1; }
    #editor { height: 18; border: tall $primary; }
    #grade-panel { height: auto; border: tall $accent; padding: 1 2; margin-top: 1; }

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
