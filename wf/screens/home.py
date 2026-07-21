"""홈 = 대시보드 — 50일 진행 + 카타별 단계 현황(보고/빈칸/재현/구현 횟수).

James 설계(2026-07-20): 앱을 열면 대시보드. 사실 기반 카운트.
단계: 보고 따라치기 → 빈칸 채우기 → 안 보고 재현 → 스스로 구현 (리서치: faded worked examples)
성장 캐릭터(2026-07-21 James): 스트릭 5일마다 진화하는 레트로 도트 캐릭터 — 보상·동기유발.
"""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from wf import character
from wf.content.loader import load_katas
from wf.store import db

MODE_KO = {"guided": "보고", "cloze": "빈칸", "recall": "재현", "solve": "구현"}
MODES_ORDER = ("guided", "cloze", "recall", "solve")
STAGE_KO = ("보", "빈", "재", "구")
STAGE_COLOR = ("cyan", "magenta", "orange1", "green")   # 단계 고유색 4가지 (2026-07-21 James)
STAGE_EMOJI = ("👀", "🧩", "🧠", "⚔")                    # 아이콘은 헤더 범례 1곳에만 (절제 원칙)


class HomeScreen(Screen):
    BINDINGS = [
        ("g", "open_mode('guided')", "보고"),
        ("b", "open_mode('cloze')", "빈칸"),
        ("r", "open_mode('recall')", "재현"),
        ("s", "open_mode('solve')", "구현"),
        ("i", "drill", "인식 드릴"),
        ("t", "toggle_sprint", "속성 7일"),
        ("q", "quit_app", "종료"),
    ]

    def compose(self) -> ComposeResult:
        import json as _json
        from pathlib import Path as _Path
        conn = db.connect()
        day = db.course_day(conn)
        streak = db.get_streak(conn)
        self._progress = {k.id: db.kata_progress(conn, k.id) for k in load_katas()}
        sprint = db.sprint_state(conn)
        self._recog = db.recognition_stats(conn)
        conn.close()
        self._sprint_plan = _json.loads(
            (_Path(__file__).parent.parent / "content/sprint.json").read_text(encoding="utf-8"))
        self._sprint = sprint
        sprint_new, sprint_review = [], []
        if sprint:
            d = str(min(sprint["day"], 7))
            day_plan = self._sprint_plan["plan"][d]
            sprint_new = day_plan.get("new", [])
            sprint_review = day_plan.get("review", [])

        with Vertical(id="dash"):
            # ── 헤더 한 줄: 제목 · 일차 · 스트릭 (색은 여기서 절제 — 표의 4단계색이 주인공)
            head = Text()
            head.append("⚔ WARFRONT 2", style="bold")
            head.append("  ·  50일 코딩테스트 훈련", style="dim")
            head.append(f"      D{day}", style="bold")
            head.append("/50", style="dim")
            head.append(f"   연속 {streak}일", style="bold" if streak else "dim")
            yield Static(head, id="dash-head")
            if self._sprint:
                sd = self._sprint["day"]
                sp = Text()
                if sd <= 7:
                    sp.append(f"⚡ 속성 D{sd}/7 — {self._sprint_plan['plan'][str(sd)]['focus']}",
                              style="yellow")
                    sp.append("  (t 해제)", style="dim")
                else:
                    sp.append("⚡ 속성 7일 완료 — 실전 응시 단계 (t 해제)", style="yellow")
                yield Static(sp, id="sprint-banner")
            with Horizontal(id="main-cols"):
                # ── 좌: 카타 테이블 (핵심 작업 영역)
                with Vertical(id="left-col"):
                    table = DataTable(id="kata-table", cursor_type="row")
                    prog_head = Text()
                    for i, ko in enumerate(("보고", "빈칸", "재현", "구현")):
                        prog_head.append(ko, style=f"bold {STAGE_COLOR[i]}")
                        if i < 3:
                            prog_head.append("·", style="dim")
                    table.add_columns("카타", "설명", prog_head, "다음")
                    for kata in load_katas():
                        p = self._progress[kata.id]
                        marker = ""
                        if self._sprint:
                            if kata.id in sprint_new:
                                marker = "⚡ "
                            elif kata.id in sprint_review:
                                marker = "🔁 "
                        table.add_row(
                            marker + kata.title,
                            Text((kata.desc or kata.belt)[:26], style="grey50"),
                            self._progress_cells(p),
                            self._next_badge(p),
                            key=kata.id,
                        )
                    yield table
                    yield Static("", id="row-detail")
                # ── 우: 관측 패널 (캐릭터 · 과정 진행 · 인식률)
                with Vertical(id="side-col"):
                    yield Static(id="char-panel")
                    yield Static("", id="char-label")
                    yield Static(self._course_bar(), id="course-progress")
                    recog = Text()
                    if self._recog["rate"] is not None:
                        ok = self._recog["rate"] >= 90
                        recog.append("유형 인식률  ", style="dim")
                        recog.append(f"{self._recog['rate']}%", style="bold green" if ok else "bold yellow")
                        recog.append(f"  (n={self._recog['total']} · 목표 90%)", style="dim")
                    else:
                        recog.append("유형 인식률  — ", style="dim")
                        recog.append(" i 로 첫 드릴", style="yellow")
                    yield Static(recog, id="recog-line")
        yield Footer()

    # ---------- 도트풍 진행 표시 (2026-07-21 James: 매일 보는 화면 — 진행이 한눈에) ----------
    def _stage_state(self, p: dict) -> tuple[int, bool]:
        """(다음 단계 인덱스, 전단계 완료 여부). 구현(solve)은 pass 시에만 기록되므로 counts>0=완료."""
        return MODES_ORDER.index(p["next_mode"]), p["counts"]["solve"] > 0

    def _progress_cells(self, p: dict) -> Text:
        """카타 한 줄의 4단계 도트 진행: ▰완료(초록) ▶현재(노랑) ▱잠김(회색) + 횟수."""
        ni, solved = self._stage_state(p)
        t = Text()
        for i, m in enumerate(MODES_ORDER):
            col = STAGE_COLOR[i]
            if (i < ni) or (m == "solve" and solved):
                t.append("▰", style=f"bold {col}")
            elif i == ni and not solved:
                t.append("▶", style=f"bold {col}")
            else:
                t.append("▱", style="grey35")
            t.append(" ")
        return t

    def _next_badge(self, p: dict) -> Text:
        ni, solved = self._stage_state(p)
        if solved:
            return Text("완료", style="bold green")
        return Text(f"▶ {MODE_KO[MODES_ORDER[ni]]}", style=f"bold {STAGE_COLOR[ni]}")

    def _course_bar(self) -> Text:
        """과정 전체 진행 — 완료 단계 수 / (카타 수 × 4단계) 픽셀 바."""
        done = 0
        for p in self._progress.values():
            ni, solved = self._stage_state(p)
            done += 4 if solved else ni
        total = 4 * max(len(self._progress), 1)
        width = 26
        filled = round(width * done / total)
        t = Text()
        t.append("과정 진행  ", style="dim")
        t.append(f"{done}/{total} 단계", style="bold")
        t.append(f"  ({round(100 * done / total)}%)\n", style="dim")
        t.append("▰" * filled, style="bold green")
        t.append("▱" * (width - filled), style="grey35")
        return t

    def _update_row_detail(self, kata_id: str) -> None:
        """커서가 놓인 카타의 상세 — 표에서 걷어낸 횟수·최고 정확도는 여기서 보존."""
        from wf.content.loader import get_kata
        p = self._progress.get(kata_id)
        if not p:
            return
        k = get_kata(kata_id)
        t = Text()
        t.append(f"{k.title}", style="bold")
        t.append("   ")
        for i, m in enumerate(MODES_ORDER):
            cnt, acc = p["counts"][m], p["best_acc"][m]
            t.append(MODE_KO[m], style=f"bold {STAGE_COLOR[i]}")
            if cnt:
                t.append(f" {cnt}회", style="")
                t.append(f"({int(acc)}%)" if m != "solve" else "", style="dim")
            else:
                t.append(" —", style="grey42")
            if i < 3:
                t.append("  ·  ", style="grey35")
        t.append("      ⏎ 다음 단계 시작", style="dim")
        self.query_one("#row-detail", Static).update(t)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is not None and event.row_key.value:
            self._update_row_detail(event.row_key.value)

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()
        self._char_init()

    # ---------- 성장 캐릭터 (스트릭 5일마다 진화 — 보상·동기유발) ----------
    def _char_init(self) -> None:
        conn = db.connect()
        self._streak = db.get_streak(conn)
        self._stage = character.stage_for(self._streak)
        seen_raw = db.get_meta(conn, "char_stage_seen")
        if seen_raw is None:
            # 최초 실행/업그레이드: 조용히 현재 단계로 동기화 (설치 직후 축하 방지)
            db.set_meta(conn, "char_stage_seen", str(self._stage))
            seen = self._stage
        else:
            seen = int(seen_raw)
        self._tick = 0
        self._evo_frames: list[str] = []
        if self._stage > seen:
            self._evo_frames = character.evolution_frames(self._stage)
            db.set_meta(conn, "char_stage_seen", str(self._stage))
            name, lore = character.stage_info(self._stage)
            self.notify(f"🎉 진화! Lv{self._stage} {name} — {lore}", timeout=6)
        conn.close()
        self._char_render()
        self.set_interval(0.5, self._char_tick)

    def _char_tick(self) -> None:
        self._tick += 1
        self._char_render()
        if getattr(self, "_levelup_shot_due", False):
            self._levelup_shot_due = False
            try:
                svg = self.app.export_screenshot()
                stage, (name, _) = self._stage, character.stage_info(self._stage)
                def _push() -> None:
                    try:
                        from wf import sync
                        msg = sync.save_levelup_screenshot(svg, stage, name)
                        if "push 완료" in msg:
                            self.app.call_from_thread(
                                self.notify, "레벨업 스크린샷을 기록 repo에 올렸습니다", timeout=4)
                    except Exception:
                        pass   # 기록 실패가 훈련을 방해하지 않는다
                self.run_worker(_push, thread=True)
            except Exception:
                pass

    def _char_render(self) -> None:
        name, _ = character.stage_info(self._stage)
        if self._evo_frames:
            art = self._evo_frames.pop(0) if len(self._evo_frames) > 1 else self._evo_frames[0]
            if len(self._evo_frames) == 1:
                # 마지막(새 모습) 프레임에 도달 — 다음 틱부터 idle로 전환
                self._evo_frames = []
                self._levelup_shot_due = True   # 새 모습이 그려진 뒤 스크린샷 → 기록 repo
            style = "bold yellow"
        else:
            art = character.idle_frame(self._stage, self._tick)
            style = f"bold {character.stage_color(self._stage)}"
        panel = Text()
        for line in art.split("\n"):
            panel.append(line + "\n", style=style)
        self.query_one("#char-panel", Static).update(panel)
        nxt = character.days_to_next(self._streak)
        label = f"Lv{self._stage} {name}" + (f" · 진화 D-{nxt}" if nxt is not None else " · 최종")
        self.query_one("#char-label", Static).update(label)

    def _open(self, kata_id: str, mode: str) -> None:
        from wf.content.loader import get_kata, variant_for
        kata = get_kata(kata_id)
        if mode in ("recall", "solve"):     # 백지 구현 — 기능 동등 판정
            from wf.screens.solve import SolveScreen
            if mode == "solve":
                variant = variant_for(kata)
                if variant is not None:     # 구현 = 같은 유형의 변형 문제 (낯선 표면)
                    self.app.push_screen(SolveScreen(variant, "solve",
                                                     record_as=kata.id,
                                                     origin_title=kata.title))
                    return
            self.app.push_screen(SolveScreen(kata, mode))
        else:                                # 타이핑 카타 — 보고/빈칸
            from wf.screens.kata import KataScreen
            self.app.push_screen(KataScreen(kata, mode))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        kata_id = event.row_key.value
        self._open(kata_id, self._progress[kata_id]["next_mode"])

    def action_open_mode(self, mode: str) -> None:
        """선택된 카타를 지정 모드로 — 해금과 무관하게 언제든 재수련(반복이 기본기)."""
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self._open(row_key.value, mode)

    def action_drill(self) -> None:
        from wf.screens.drill import RecognitionScreen
        self.app.push_screen(RecognitionScreen())

    def action_toggle_sprint(self) -> None:
        conn = db.connect()
        on = db.sprint_toggle(conn)
        conn.close()
        self.notify("⚡ 속성 7일 시작 — 오늘 카타에 ⚡ 표시" if on else "속성 모드 해제 — 50일 일정으로 복귀")
        self.app.switch_screen(HomeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
