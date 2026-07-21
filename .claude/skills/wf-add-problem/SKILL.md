---
name: wf-add-problem
description: warfront2에 문제(카타/변형문제/인식문항)를 추가하는 절차. James가 "문제 추가해줘"라고 하면 이 절차대로 — 스키마 준수, 채점기 자가검증 필수, 개인/설치형 배치 구분, 인식문항은 출처 앵커 필수.
---

# warfront2 문제 추가 절차

## 0. 먼저 물을 것 (또는 맥락에서 판별)
1. **어떤 종류인가** — 카타(타이핑 4단계용 패턴 원형) / 변형 문제(solve 전용) / 인식 문항(지문+유형 판별)
2. **개인용인가 기본 콘텐츠인가**
   - 개인(실전에서 만난 문제, 회사 특화): `~/.warfront2/custom/{katas,problems,recognition}/` — wf update 영향 없음, 기록 repo로 자동 백업
   - 기본(모두에게 배포): `wf/content/{katas,problems}/` 또는 recognition.json — 커밋·push 필요
3. **소재의 출처** — James 실전 경험이면 최고의 1차 소스(경험 그대로 기록). 그 외에는 검증된 기출(docs/SOURCES.md의 소스)에서만. **추측으로 유형·문제를 창작 금지.**

## 1. 스키마

### 카타 / 변형 문제 (동일 스키마 — Kata dataclass, wf/content/loader.py)
```json
{
  "id": "kebab-case-id",
  "type": "bfs|dfs|dp|hash|greedy|stack|heap|backtracking|implementation|binary_search|two_pointer|dijkstra",
  "title": "유형 — 제목", "belt": "탐색|해시|그리디|스택큐|구현|DP|이분탐색|기초",
  "desc": "한 줄 설명 (초보자가 이해되게 — 사전지식 전제 금지)",
  "statement": "실전형 문제 지문 ★필수 (2026-07-21 James: 실제 출제 수준과 동일하게) — ko는 프로그래머스체(문제 설명/제한사항/입출력 예/입출력 예 설명), en은 HackerRank체(Problem/Function Description/Returns/Constraints/Sample). 제한 수치는 perf.gen과 정합해야 하고, 예제는 tests에서 가져온다. 원문 복제 금지(자작 지문).",
  "statement_lang": "ko|en — 1순위 앵커 플랫폼 언어 (HackerRank/LeetCode 앵커면 en)",
  "expected_complexity": "O(N log N)",
  "think_prompt": "THINK 게이트 질문 — 자료구조·이유를 생각하게",
  "think_model": "모범 접근 한 문단",
  "code": "모범답안 전체 (마지막 개행 포함)",
  "subgoals": [{"label": "① 단계 설명", "lines": [시작줄, 끝줄]}],
  "line_notes": {"줄번호문자열": "그 줄의 자연어 설명"},
  "func": "채점 대상 함수명",
  "tests": [{"args": [...], "expected": ...}],
  "perf": {"gen": "def make_args():\n    return (대형입력,)", "time_limit": 3.0},
  "diagram": {"caption": "...", "fps": 0, "frames": ["유니코드 다이어그램"]},
  "resources": [{"name": "플랫폼 문제명 (난이도)", "url": "https://..."}]
}
```
주의:
- **튜플 인자는 `args` 대신 `"args_repr": "([[0,0]], (0,0))"`** (JSON은 튜플 표현 불가 — BFS 좌표 사고 전례)
- subgoals의 lines는 0-index, 트레일링 빈 줄 제외 (오프바이원 전례)
- perf.gen은 결정적으로(랜덤 금지) `make_args()` 정의
- 변형 문제는 subgoals/line_notes/diagram 생략 가능(solve 전용), 반드시 **원형과 다른 스토리 도메인**으로
- resources 링크: 프로그래머스/HackerRank 우선 (백준은 서비스 중단 중 — 문제명 앵커로만)

### 인식 문항 (custom은 `~/.warfront2/custom/recognition/아무이름.json`)
```json
{"items": [{
  "id": "c001", "text": "지문 (기출 요지 재서술 — 원문 복제 금지)",
  "answer": "유형", "trap": "헷갈리는 인접 유형(오답 보기)",
  "also_ok": ["복수 정답 유형"], "signals": "판별 신호 설명",
  "source": {"name": "출처 문제명", "url": "https://..."}
}]}
```
- **source 필수** — 기출 또는 "James 실전 경험(회사·시기)"도 유효한 출처
- trap은 반드시 경계가 헷갈리는 유형으로 (bfs↔dijkstra, greedy↔dp, dfs↔bfs)

## 2. 품질 게이트 (필수 — 통과 못 하면 추가 금지)
카타/변형 문제는 모범답안이 채점기를 통과해야 한다:
```bash
cd ~/cursor/warfront2 && python3 -c "
from wf.content.loader import get_any
from wf.engine.grader import grade
k = get_any('새-문제-id')
r = grade(k.code, k.func, k.tests, k.perf, hard_timeout=20)
print(r['verdict'], r['passed'], '/', r['total'], r.get('perf'))
assert r['verdict'] == 'pass'"
```
추가로: 오답 구현 1개가 fail하는지도 확인(테스트가 실제로 변별하는지).
기본 콘텐츠로 넣을 땐 `python3 -m pytest tests/` 전체 통과 후 커밋.

## 3. 배치 후 확인
- 개인: `wf` 재시작 → 대시보드에 나타남 (custom 카타는 목록 뒤에 붙음)
- 인식 문항: `i` 드릴 풀에 자동 병합
- 개인 콘텐츠는 다음 세션 종료 시 기록 repo로 자동 백업됨
