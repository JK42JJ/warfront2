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

    /* ---- 카타 ---- */
    #kata { padding: 1 4; }
    #kata-title { margin-bottom: 1; color: $accent; }
    #think-box { border: tall $warning; padding: 1 2; margin: 1 0; }
    #think-prompt { margin-bottom: 1; }
    #type-box { margin-top: 1; }
    #code-display { border: tall $primary; padding: 1 2; }
    #stats { height: auto; margin-top: 1; align: center middle; }
    #stats Digits { width: auto; margin: 0 1; }
    .stat-label { color: $text-muted; margin: 0 3 0 0; content-align: left bottom; height: 100%; }
    .hidden { display: none; }

    /* ---- 결과 ---- */
    #result { padding: 1 4; align: center middle; }
    #result-title { text-align: center; width: 100%; margin-bottom: 1; color: $success; text-style: bold; }
    #result-stats { height: auto; align: center middle; margin: 1 0; }
    .stat-block { width: auto; margin: 0 3; align: center middle; }
    .stat-block Digits { width: auto; }
    #think-compare { border: tall $warning; padding: 1 2; margin: 1 0; }
    #resources { color: $text-muted; margin: 1 0; }
    #result-menu { text-align: center; width: 100%; margin-top: 1; }
    """

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def run() -> None:
    WarfrontApp().run()
