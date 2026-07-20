# CLAUDE.md

작업 전에 `AGENTS.md`를 읽어라 — 지도·명령·불변식·함정이 거기 있다.

Claude 특화:
- 문제 추가 요청이 오면 `.claude/skills/wf-add-problem/SKILL.md` 절차를 따른다
  (스키마·품질 게이트·개인/설치형 배치 구분).
- 화면 수정 후에는 반드시 `python3 -m pytest tests/`로 헤드리스 검증까지.
- 이 저장소 작성자(JK42JJ)의 훈련 기록은 career repo와 연동된다(wf/sync.py) —
  sync 로직 수정 시 절대 예외를 밖으로 던지지 않게 유지.
