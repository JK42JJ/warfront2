# 기여 가이드

가장 필요한 기여는 **문제 추가**입니다. 코드 기여도 환영합니다.

## 문제 기여 (가장 쉽고 가장 가치 있음)

1. 형식: [.claude/skills/wf-add-problem/SKILL.md](.claude/skills/wf-add-problem/SKILL.md)의
   스키마를 따릅니다. AI 에이전트(Claude Code, Codex 등)를 쓰면 이 절차가
   자동 적용됩니다 — 저장소를 열고 "문제 추가해줘"라고 하면 됩니다.
2. 규칙 두 가지:
   - 지문은 직접 작성 (기출 원문 복제 금지 — 요지 재서술)
   - 출처 명시 (검증된 기출 목록은 [docs/SOURCES.md](docs/SOURCES.md))
3. 검증: 모범답안이 채점기를 통과해야 합니다.
   ```bash
   python3 -m pytest tests/
   ```
4. PR을 보냅니다. 어느 시험(기업·연도)에서 본 유형인지 적어주면 가장 좋습니다.

## 코드 기여

1. `pip install -e ".[dev]"` 후 `python3 -m pytest tests/`가 기준선입니다.
2. 화면(UI) 변경은 헤드리스 테스트를 함께 추가해주세요
   (tests/test_core.py의 `run_test()` 패턴 참고).
3. 아키텍처와 결정 배경은 [AGENTS.md](AGENTS.md)와 [docs/DESIGN.md](docs/DESIGN.md)에 있습니다.

## 버그 신고

이슈에 다음을 적어주세요: 실행 환경(OS·터미널·Python), 재현 절차, 화면에 뜬 오류.
