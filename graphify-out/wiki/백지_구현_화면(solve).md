# 백지 구현 화면(solve)

> 24 nodes · cohesion 0.12

## Key Concepts

- **DiagramPanel** (41 connections) — `wf/widgets.py`
- **필름스트립: 애니메이션 진행 시 스냅샷이 우측으로 누적(되감기지 않음).** (8 connections) — `tests/test_core.py`
- **Static** (6 connections)
- **test_diagram_filmstrip_grows()** (6 connections) — `tests/test_core.py`
- **._render_frame()** (5 connections) — `wf/widgets.py`
- **백지 구현 화면 — 재현(recall)·구현(solve) 모드.  판정 철학(James + 리서치, 2026-07-20): 재현은 축자 암기가** (4 connections) — `wf/screens/solve.py`
- **모범코드에서 시그니처(def 줄)만 추출 — 백지 + 빈 함수 뼈대.** (4 connections) — `wf/screens/solve.py`
- **.compose()** (4 connections) — `wf/screens/solve.py`
- **_compact()** (4 connections) — `wf/widgets.py`
- **_hjoin()** (4 connections) — `wf/widgets.py`
- **widgets.py** (4 connections) — `wf/widgets.py`
- **.compose()** (3 connections) — `wf/screens/home.py`
- **.compose()** (3 connections) — `wf/screens/kata.py`
- **starter_code()** (3 connections) — `wf/screens/solve.py`
- **solve.py** (3 connections) — `wf/screens/solve.py`
- **.compose()** (2 connections) — `wf/screens/drill.py`
- **.compose()** (2 connections) — `wf/screens/result.py`
- **._advance()** (2 connections) — `wf/widgets.py`
- **.toggle()** (2 connections) — `wf/widgets.py`
- **.__init__()** (1 connections) — `wf/widgets.py`
- **공용 위젯 — 개념도 패널(유니코드 다이어그램, 프레임 애니메이션 + 필름스트립).  James(2026-07-20): 애니메이션은 그대로 두고** (1 connections) — `wf/widgets.py`
- **스냅샷용 축약 — 첫 빈 줄 전(격자 부분)만.** (1 connections) — `wf/widgets.py`
- **블록들을 가로로 이어붙임(높이·폭 패딩).** (1 connections) — `wf/widgets.py`
- **F2 개념도 — 상단: 현재 프레임(애니메이션) / 하단: 단계 필름스트립(우측 증가).** (1 connections) — `wf/widgets.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `tests/test_core.py`
- `wf/screens/drill.py`
- `wf/screens/home.py`
- `wf/screens/kata.py`
- `wf/screens/result.py`
- `wf/screens/solve.py`
- `wf/widgets.py`

## Audit Trail

- EXTRACTED: 49 (43%)
- INFERRED: 66 (57%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*