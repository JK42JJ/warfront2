"""WARFRONT 2 — Textual 앱 루트."""
from __future__ import annotations

from textual.app import App

from wf.screens.home import HomeScreen


class WarfrontApp(App):
    TITLE = "WARFRONT 2"

    CSS = """
    Screen { align: center middle; }
    HomeScreen { align: center top; }   /* 매일 보는 화면 — 위 정렬로 여백 산만함 제거 */
    #course-progress { height: auto; margin-bottom: 1; }

    /* ---- 대시보드(홈): 좌 작업(테이블) / 우 관측(캐릭터·진행) 콕핏 ---- */
    #dash { padding: 1 2; height: auto; width: 100%; }
    #dash-head { height: 1; margin-bottom: 1; }
    #sprint-banner { height: 1; margin-bottom: 1; }
    #main-cols { height: auto; }
    #left-col { width: 1fr; height: auto; }
    #side-col { width: 36; height: auto; padding: 1 0 0 3; }
    #kata-table { height: auto; max-height: 22; }
    #row-detail { height: auto; margin-top: 1; }
    #char-panel { height: auto; width: 100%; padding-left: 6; }
    #char-label { height: auto; width: 100%; color: $text-muted; margin: 1 0; }
    #recog-line { height: auto; margin-top: 1; }
    #hint-panel { height: auto; border: tall $success; padding: 1 2; margin-top: 1; }
    #diagram-panel { height: auto; border: tall $accent; padding: 1 2; margin-top: 1; }

    /* ---- 카타 ----
       주의: Vertical/Horizontal 기본 height는 1fr(화면 채움) — auto로 강제하지
       않으면 빈 박스가 화면 전체를 먹고 다른 위젯을 화면 밖으로 밀어낸다
       (2026-07-20 화면깨짐 버그의 원인). */
    #kata { padding: 1 4; height: auto; width: 100%; }
    #kata-title { margin-bottom: 1; color: $accent; height: auto; }
    /* 2컬럼: 좌 문제 지문 / 우 코드 — 실전 플랫폼과 동일한 배치 (2026-07-21 James) */
    #twocol { height: auto; }
    #stmt-panel { width: 46; height: auto; border: tall $secondary;
                  border-title-color: $warning; padding: 1 2; margin-right: 2; }
    #right-col { width: 1fr; height: auto; }
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
    #solve { padding: 1 4; height: auto; width: 100%; }
    #solve-box { height: auto; }
    #solve-desc { height: auto; margin-bottom: 1; }
    #editor { height: 18; border: tall $primary; }
    #grade-panel { height: auto; border: tall $accent; padding: 1 2; margin-top: 1; }

    /* ---- 인식 드릴 ---- */
    #drill { padding: 2 6; height: auto; }
    #drill-progress { height: auto; margin-bottom: 1; }
    #drill-question { height: auto; border: tall $primary; padding: 1 2; margin-bottom: 1; }
    #drill-choices { height: auto; margin-bottom: 1; }
    #drill-feedback { height: auto; border: tall $warning; padding: 1 2; }

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
