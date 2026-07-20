# CLI 진입점·속성 모드

> 17 nodes · cohesion 0.13

## Key Concepts

- **cli.py** (9 connections) — `wf/cli.py`
- **_versions()** (4 connections) — `wf/cli.py`
- **app.py** (3 connections) — `wf/app.py`
- **run()** (3 connections) — `wf/app.py`
- **update()** (3 connections) — `wf/cli.py`
- **WARFRONT 2 — Textual 앱 루트.** (2 connections) — `wf/app.py`
- **_default()** (2 connections) — `wf/cli.py`
- **reset()** (2 connections) — `wf/cli.py`
- **setup()** (2 connections) — `wf/cli.py`
- **sprint()** (2 connections) — `wf/cli.py`
- **version()** (2 connections) — `wf/cli.py`
- **main()** (1 connections) — `wf/cli.py`
- **진입점: wf=훈련 · wf update=콘텐츠 최신화 · wf setup=기록 GitHub 연동 · wf reset.** (1 connections) — `wf/cli.py`
- **속성 7일 모드 — 갑자기 코테가 잡혔을 때 최빈출 압축 과정 (하루 60~90분).** (1 connections) — `wf/cli.py`
- **메인 repo에서 최신 문제·기능 받기 (git clone 설치 기준).** (1 connections) — `wf/cli.py`
- **훈련 기록을 내 GitHub repo로 자동 push하도록 설정.** (1 connections) — `wf/cli.py`
- **모든 훈련 기록 초기화 (세션·개인최고·스트릭·50일 일차 전부 삭제).** (1 connections) — `wf/cli.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `wf/app.py`
- `wf/cli.py`

## Audit Trail

- EXTRACTED: 36 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*