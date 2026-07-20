# SQLite 기록 저장소

> 22 nodes · cohesion 0.10

## Key Concepts

- **db.py** (13 connections) — `wf/store/db.py`
- **sprint_state()** (3 connections) — `wf/store/db.py`
- **sprint_toggle()** (3 connections) — `wf/store/db.py`
- **course_day()** (2 connections) — `wf/store/db.py`
- **dump_sessions()** (2 connections) — `wf/store/db.py`
- **import_sessions()** (2 connections) — `wf/store/db.py`
- **kata_progress()** (2 connections) — `wf/store/db.py`
- **recognition_stats()** (2 connections) — `wf/store/db.py`
- **record_session()** (2 connections) — `wf/store/db.py`
- **connect()** (1 connections) — `wf/store/db.py`
- **get_streak()** (1 connections) — `wf/store/db.py`
- **SQLite 저장소 — 세션·개인최고·스트릭. 단일 파일 ~/.warfront2/wf.db.** (1 connections) — `wf/store/db.py`
- **전체 세션을 복원 가능한 형태로 덤프 (records repo 백업용).** (1 connections) — `wf/store/db.py`
- **백업 세션을 DB로 복원 — bests 재계산, 시작일은 최초 세션일로.** (1 connections) — `wf/store/db.py`
- **속성 모드 상태 — {'day': n, 'start': date} 또는 None.** (1 connections) — `wf/store/db.py`
- **속성 모드 켜기/끄기. 반환: 켜졌는지.** (1 connections) — `wf/store/db.py`
- **유형 인식률 — 전체·유형별 (식별력 지표).** (1 connections) — `wf/store/db.py`
- **50일 과정 일차 — 최초 실행일을 시작일로 기록.** (1 connections) — `wf/store/db.py`
- **카타별 모드 수행 횟수·최고 정확도·다음 단계.** (1 connections) — `wf/store/db.py`
- **세션 저장 + 개인최고 갱신 여부 반환.** (1 connections) — `wf/store/db.py`
- **record_recognition()** (1 connections) — `wf/store/db.py`
- **today_session_count()** (1 connections) — `wf/store/db.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `wf/store/db.py`

## Audit Trail

- EXTRACTED: 44 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*