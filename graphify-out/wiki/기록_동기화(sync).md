# 기록 동기화(sync)

> 9 nodes · cohesion 0.28

## Key Concepts

- **sync.py** (5 connections) — `wf/sync.py`
- **export_and_push()** (3 connections) — `wf/sync.py`
- **push_records_repo()** (3 connections) — `wf/sync.py`
- **today_aggregate()** (3 connections) — `wf/sync.py`
- **sync_all()** (2 connections) — `wf/sync.py`
- **career repo 싱크 — 오늘의 warfront 연습을 일일 루틴 관측에 반영.  James(2026-07-20): "warfront로 연** (1 connections) — `wf/sync.py`
- **세션 종료 시 호출 — career repo(James) + 개인 기록 repo(wf setup) 모두 best-effort.      ★어떤** (1 connections) — `wf/sync.py`
- **wf setup으로 설정한 개인 기록 repo(~/.warfront2)에 오늘 기록 push.** (1 connections) — `wf/sync.py`
- **오늘 집계를 career repo에 기록하고 best-effort push. 반환: 상태 문자열.** (1 connections) — `wf/sync.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `wf/sync.py`

## Audit Trail

- EXTRACTED: 20 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*