# 설계 계보·UX 참조

> 8 nodes · cohesion 0.25

## Key Concepts

- **wf/app.py — Textual 앱 루트 + 전체 CSS** (2 connections) — `wf/app.py`
- **중독 루프 (즉시 피드백 UX)** (2 connections) — `docs/DESIGN.md`
- **유형별 벨트 승급 (무술 단급제)** (2 connections) — `docs/DESIGN.md`
- **고스트 대결 (과거 기록 재생)** (2 connections) — `docs/DESIGN.md`
- **smassh — MonkeyType TUI 클론 (2k★)** (2 connections) — `docs/DESIGN.md`
- **Textual 8.x (TUI 프레임워크)** (2 connections) — `docs/DESIGN.md`
- **warfront v1 프로토타입 (tmux 4-pane 전술 시뮬레이터)** (2 connections) — `docs/DESIGN.md`
- **불변식: 콘텐츠 문자열 Rich 마크업 보간 금지** (1 connections) — `AGENTS.md`

## Relationships

- No strong cross-community connections detected

## Source Files

- `AGENTS.md`
- `docs/DESIGN.md`
- `wf/app.py`

## Audit Trail

- EXTRACTED: 13 (87%)
- INFERRED: 2 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*