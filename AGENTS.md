# AGENTS.md — 에이전트 작업 가이드

터미널 코딩테스트 훈련 도구. Python 3.10+ / Textual TUI / SQLite.
이 파일 하나로 맥락을 잡고 작업을 시작할 수 있다.

## 명령

```bash
pip install -e ".[dev]"        # 설치
python3 -m pytest tests/       # 테스트 (전부 통과가 작업 전 기준선)
wf                             # 앱 실행 (TUI — 에이전트는 헤드리스 테스트로 검증)
```

TUI는 직접 실행해 볼 수 없으므로 검증은 항상 `run_test()` 헤드리스 테스트로 한다.
tests/test_core.py에 화면 플로우 테스트 패턴이 다 있다 — 따라 쓰면 된다.

## 지도 (파일 → 역할)

```
wf/app.py                Textual 앱 루트 + 전체 CSS
wf/cli.py                wf / update / setup / sprint / reset 명령
wf/screens/home.py       대시보드(진입 화면): 카타 테이블, 단계 해금, 스프린트, 키 바인딩
wf/screens/kata.py       타이핑 훈련 (보고 guided / 빈칸 cloze) + THINK 게이트 + F1 힌트 + F2 개념도
wf/screens/solve.py      백지 구현 (재현 recall / 구현 solve) — 에디터 + Ctrl+R 채점
wf/screens/drill.py      인식 드릴 — 지문만 보고 유형 판별, 인식률 기록
wf/screens/result.py     타이핑 세션 결과
wf/engine/typing_engine.py  키 판정·WPM·정확도 (공백 유연화 규칙 포함, 순수 로직)
wf/engine/grader.py      격리 subprocess 채점 — 히든 테스트 + 대형입력 타임아웃(효율성)
wf/store/db.py           SQLite (~/.warfront2/wf.db): 세션·개인최고·해금·스프린트·인식
wf/sync.py               기록 백업 — career repo(작성자용) + 개인 기록 repo(wf setup)
wf/content/katas/        설치형 카타 15종 (번호 prefix = 커리큘럼 순서)
wf/content/problems/     변형 문제 (solve 전용)
wf/content/recognition.json  인식 문항 50 (전부 기출 출처 앵커)
wf/content/curriculum.yaml   50일 배치 / sprint.json 7일 속성 배치
~/.warfront2/custom/     사용자 개인 콘텐츠 (로더가 자동 병합 — repo 밖)
docs/DESIGN.md           설계 근거(리서치 기반) / docs/SOURCES.md 콘텐츠 출처 원장
```

## 불변식 (어기면 안 되는 것)

1. **콘텐츠는 출처 필수.** 문제 유형·인식 문항을 추측으로 창작하지 않는다.
   검증된 기출(docs/SOURCES.md) 또는 사용자의 실전 경험만. 인식 문항의
   source 누락은 테스트가 커밋을 막는다.
2. **새 문제는 채점기 자가검증 통과가 조건.** 모범답안 pass + 오답 fail 확인.
   절차: .claude/skills/wf-add-problem/SKILL.md
3. **sync는 어떤 예외에도 앱을 죽이면 안 된다.** 훈련 흐름 최우선.
4. **콘텐츠 유래 문자열(제목·URL·사용자 입력)을 Rich 마크업에 보간하지 않는다.**
   Text 객체로 구성한다. (URL이 마크업 파서를 죽인 실사고)
5. 재현·구현 판정은 **기능 동등**(테스트 통과) — 글자 비교 아님.
6. 사용자 문서(README)는 초보자 기준: 사전지식 전제 금지, 내부 과정 서사 금지.

## 함정 (실제로 밟은 것들)

- Textual 컨테이너 기본 height는 1fr(화면 채움) — auto 미지정 시 레이아웃 붕괴
- 타이핑 키 바인딩은 인쇄 가능 문자와 충돌 (h 힌트 사고 → F1로)
- JSON 테스트에 튜플 인자 불가 → `args_repr` 필드 사용
- subgoals lines는 0-index, 트레일링 빈 줄 제외 (오프바이원 사고)
- perf.gen은 결정적으로 (랜덤 금지)
- 백준(acmicpc.net)은 2026-04부터 서비스 중단 — 링크는 프로그래머스/HackerRank 우선
- 편집 설치(pip -e)라 실행 중인 wf는 코드 수정을 모른다 — 사용자에게 재시작 안내

## 스타일

- 한국어 UI·주석. 커밋 메시지도 한국어.
- 사용자 대면 문구: 게임화·치어리딩 금지, 사실 기반. 이모지 남발 금지.
- 테스트 없는 기능 추가 금지 — 화면 플로우까지 헤드리스로 검증한다.
