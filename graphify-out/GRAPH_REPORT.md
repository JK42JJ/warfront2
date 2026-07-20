# Graph Report - /Users/jeonhokim/cursor/warfront2  (2026-07-20)

## Corpus Check
- Corpus is ~24,108 words - fits in a single context window. You may not need a graph.

## Summary
- 326 nodes · 642 edges · 18 communities detected
- Extraction: 53% EXTRACTED · 47% INFERRED · 1% AMBIGUOUS · INFERRED: 299 edges (avg confidence: 0.59)
- Token cost: 63,500 input · 14,800 output

## Community Hubs (Navigation)
- [[_COMMUNITY_앱 코어·결과 화면|앱 코어·결과 화면]]
- [[_COMMUNITY_온보딩 문서·운영 체계|온보딩 문서·운영 체계]]
- [[_COMMUNITY_인식 드릴 화면|인식 드릴 화면]]
- [[_COMMUNITY_백지 구현 화면(solve)|백지 구현 화면(solve)]]
- [[_COMMUNITY_SQLite 기록 저장소|SQLite 기록 저장소]]
- [[_COMMUNITY_카타 타이핑 화면|카타 타이핑 화면]]
- [[_COMMUNITY_CLI 진입점·속성 모드|CLI 진입점·속성 모드]]
- [[_COMMUNITY_훈련 설계 원칙(4단계)|훈련 설계 원칙(4단계)]]
- [[_COMMUNITY_콘텐츠 로더|콘텐츠 로더]]
- [[_COMMUNITY_스크린샷 따라치기|스크린샷: 따라치기]]
- [[_COMMUNITY_스크린샷 인식 드릴|스크린샷: 인식 드릴]]
- [[_COMMUNITY_스크린샷 대시보드|스크린샷: 대시보드]]
- [[_COMMUNITY_타이핑 판정 로직|타이핑 판정 로직]]
- [[_COMMUNITY_기록 동기화(sync)|기록 동기화(sync)]]
- [[_COMMUNITY_채점 엔진|채점 엔진]]
- [[_COMMUNITY_설계 계보·UX 참조|설계 계보·UX 참조]]
- [[_COMMUNITY_타이핑 지표(WPM·정확도)|타이핑 지표(WPM·정확도)]]
- [[_COMMUNITY_패키지 메타|패키지 메타]]

## God Nodes (most connected - your core abstractions)
1. `KataScreen` - 50 edges
2. `TypingSession` - 47 edges
3. `SolveScreen` - 44 edges
4. `DiagramPanel` - 41 edges
5. `ResultScreen` - 39 edges
6. `RecognitionScreen` - 39 edges
7. `WarfrontApp` - 38 edges
8. `HomeScreen` - 24 edges
9. `Kata` - 12 edges
10. `warfront2 — 터미널 코딩테스트 훈련기` - 9 edges

## Surprising Connections (you probably didn't know these)
- `wf/screens/home.py — 대시보드 (카타 테이블·단계 해금·스프린트)` --implements--> `FSRS 간격반복 스케줄러 (py-fsrs 6.x)`  [AMBIGUOUS]
  wf/screens/home.py → docs/DESIGN.md
- `wf/screens/home.py — 대시보드 (카타 테이블·단계 해금·스프린트)` --implements--> `정확도 95% 진급 게이트`  [INFERRED]
  wf/screens/home.py → docs/DESIGN.md
- `wf/screens/kata.py — 타이핑 훈련 (guided/cloze) + THINK 게이트 + F1/F2` --implements--> `타건감 제1원칙 (키보드를 치는 맛)`  [INFERRED]
  wf/screens/kata.py → docs/DESIGN.md
- `기여 가이드` --references--> `run_test() 헤드리스 화면 테스트 패턴`  [EXTRACTED]
  CONTRIBUTING.md → tests/test_core.py
- `AGENTS.md — 에이전트 작업 가이드` --references--> `run_test() 헤드리스 화면 테스트 패턴`  [EXTRACTED]
  AGENTS.md → tests/test_core.py

## Hyperedges (group relationships)
- **훈련 데이터 흐름: curriculum → FSRS 스케줄 → 화면(kata/solve) → 채점·계측 → DB → 즉시 피드백** — curriculum_50day_curriculum, design_fsrs, kata_typing_kata, solve_blank_implementation, grader_subprocess_grader, typing_engine_typing_engine, db_sqlite_store, result_session_result [EXTRACTED 1.00]
- **4단계 카타 진급 (보고→빈칸→재현→구현, 95% 게이트)** — design_guided_mode, design_cloze_mode, design_recall_mode, design_solve_mode, design_accuracy_gate_95 [EXTRACTED 1.00]
- **유형 인식 훈련 체계 (인식→적용→구현 3단 합격 논리)** — design_think_gate, design_signal_dictionary, design_recognition_drill, design_surface_variation_principle, recognition_recognition_items [EXTRACTED 1.00]

## Communities

### Community 0 - "앱 코어·결과 화면"
Cohesion: 0.07
Nodes (51): App, TypingSession, ResultScreen, SolveScreen, M1 코어 검증 — 타이핑 엔진·DB·콘텐츠 로더·앱 스모크., 회귀: 2026-07-20 화면깨짐 — 컨테이너 1fr 확장으로 라벨·비교·링크가     화면 밖으로 밀림. 핵심 위젯 전부가 뷰포트(120x5, 빈칸 모드: 비활성(주어진) 구간은 타이핑 없이 자동 통과., 보고(95%+) 통과해야 빈칸 해금, 그 다음 재현·구현. (+43 more)

### Community 1 - "온보딩 문서·운영 체계"
Cohesion: 0.09
Nodes (34): AGENTS.md — 에이전트 작업 가이드, CLAUDE.md — Claude 특화 가이드, wf/cli.py — wf/update/setup/sprint/reset 명령, 기여 가이드, wf/content/curriculum.yaml — 50일 커리큘럼 배치, ~/.warfront2/custom/ — 사용자 개인 콘텐츠, wf/store/db.py — SQLite 저장소 (세션·개인최고·해금·스프린트·인식), 정확도 95% 진급 게이트 (+26 more)

### Community 2 - "인식 드릴 화면"
Cohesion: 0.12
Nodes (6): Screen, 인식 스피드 드릴 — 지문만 보고 유형 판별 (코드 없음, 문제당 1분 목표).  "암기한 문제가 달라 보인다" 문제의 직접 처방: 챕터 제목, RecognitionScreen, HomeScreen, 홈 = 대시보드 — 50일 진행 + 카타별 단계 현황(보고/빈칸/재현/구현 횟수).  James 설계(2026-07-20): 앱을 열면 대시보드, 선택된 카타를 지정 모드로 — 해금과 무관하게 언제든 재수련(반복이 기본기).

### Community 3 - "백지 구현 화면(solve)"
Cohesion: 0.12
Nodes (13): 백지 구현 화면 — 재현(recall)·구현(solve) 모드.  판정 철학(James + 리서치, 2026-07-20): 재현은 축자 암기가, 모범코드에서 시그니처(def 줄)만 추출 — 백지 + 빈 함수 뼈대., starter_code(), Static, 필름스트립: 애니메이션 진행 시 스냅샷이 우측으로 누적(되감기지 않음)., test_diagram_filmstrip_grows(), _compact(), DiagramPanel (+5 more)

### Community 4 - "SQLite 기록 저장소"
Cohesion: 0.1
Nodes (17): course_day(), dump_sessions(), import_sessions(), kata_progress(), SQLite 저장소 — 세션·개인최고·스트릭. 단일 파일 ~/.warfront2/wf.db., 전체 세션을 복원 가능한 형태로 덤프 (records repo 백업용)., 백업 세션을 DB로 복원 — bests 재계산, 시작일은 최초 세션일로., 속성 모드 상태 — {'day': n, 'start': date} 또는 None. (+9 more)

### Community 5 - "카타 타이핑 화면"
Cohesion: 0.16
Nodes (4): KataScreen, 카타 화면 — THINK 게이트(생각 먼저) → 타이핑 (보고/빈칸/재현 모드).  Think-First: 접근을 한 줄로 선언해야 코드 타이핑, 레벨2 힌트는 커서 줄 이동 시 갱신., 모드별 타이핑 대상 구간. guided/recall=전체, cloze=서브골 1블록(로테이션).

### Community 6 - "CLI 진입점·속성 모드"
Cohesion: 0.13
Nodes (14): WARFRONT 2 — Textual 앱 루트., run(), _default(), 진입점: wf=훈련 · wf update=콘텐츠 최신화 · wf setup=기록 GitHub 연동 · wf reset., 속성 7일 모드 — 갑자기 코테가 잡혔을 때 최빈출 압축 과정 (하루 60~90분)., 메인 repo에서 최신 문제·기능 받기 (git clone 설치 기준)., 훈련 기록을 내 GitHub repo로 자동 push하도록 설정., 모든 훈련 기록 초기화 (세션·개인최고·스트릭·50일 일차 전부 삭제). (+6 more)

### Community 7 - "훈련 설계 원칙(4단계)"
Cohesion: 0.14
Nodes (17): ② 빈칸 채우기 (cloze), exercism python-test-runner, 기능 동등 판정 (글자 비교 아님), ① 보고 치기 (guided), ③ 안 보고 재현 (recall), ④ 스스로 구현 (solve), 표면 변형 원칙 (콘텐츠 규칙), Think-First 설계원칙 (제0원칙) (+9 more)

### Community 8 - "콘텐츠 로더"
Cohesion: 0.22
Nodes (11): get_any(), get_kata(), Kata, _load_dir(), load_katas(), load_problems(), 서브골 idx의 (시작, 끝+1) 문자 오프셋 — cloze 활성 구간 계산용., 설치형 카타 + 개인 카타(~/.warfront2/custom/katas). (+3 more)

### Community 9 - "스크린샷: 따라치기"
Cohesion: 0.19
Nodes (14): BFS 격자 최단거리 Kata, BFS Reference Implementation (Python), Follow-Along Code Panel, collections.deque, Concept Map (F2 개념도), Footer Key Bindings Bar, Kata Header Bar, Home Screen (+6 more)

### Community 10 - "스크린샷: 인식 드릴"
Cohesion: 0.21
Nodes (13): Algorithm Pattern Recognition Training, Answer Options: 1 이분탐색 / 2 완전탐색·백트래킹 / 3 DP / 4 스택, Dark Terminal Theme (#121212 bg, #0178d4 accent, macOS chrome, Fira Code), Dashboard Screen (esc target), Footer Key Bar (esc 대시보드로 / ^p palette), Intended Answer: 완전탐색/백트래킹 (N≤20 signal), Progress Counter (1/10), Question Panel (blue-bordered problem statement) (+5 more)

### Community 11 - "스크린샷: 대시보드"
Cohesion: 0.26
Nodes (12): Warfront2 Dashboard Screen (대시보드), Footer Key Bar (g 보고 · b 빈칸 · r 재현 · s 구현 · i 인식 드릴 · t 속성 7일 · q 종료 · ^p palette), Kata List Table (카타/설명 — 15 canonical kata patterns: 구현·해시·그리디·스택·힙·완전탐색·BFS·DFS·DP·이분탐색·투포인터·다익스트라), Daily/Streak Mini Charts (일/연 sparkline panels), Training Mode Ladder g/b/r/s (보고→빈칸→재현→구현, ⏎ auto-advance scaffolding), Progress Bar (partially filled horizontal gauge below kata table), 인식 드릴 Pattern Recognition Drill (key i), 유형 인식률 Stat (75% n=4 — 목표 90%+) (+4 more)

### Community 12 - "타이핑 판정 로직"
Cohesion: 0.2
Nodes (4): 한 키 입력 판정. 반환: 'ok' | 'err' | 'done' | 'noop'., 비활성 구간(주어진 코드)은 타이핑 없이 통과., 위치 i가 문자열 리터럴 안인가 — 현재 줄의 따옴표 짝으로 판정., 대상 위치 i의 공백이 '스타일 공백'인가 (줄 중간 + 문자열 밖).

### Community 13 - "기록 동기화(sync)"
Cohesion: 0.28
Nodes (8): export_and_push(), push_records_repo(), career repo 싱크 — 오늘의 warfront 연습을 일일 루틴 관측에 반영.  James(2026-07-20): "warfront로 연, 세션 종료 시 호출 — career repo(James) + 개인 기록 repo(wf setup) 모두 best-effort.      ★어떤, wf setup으로 설정한 개인 기록 repo(~/.warfront2)에 오늘 기록 push., 오늘 집계를 career repo에 기록하고 best-effort push. 반환: 상태 문자열., sync_all(), today_aggregate()

### Community 14 - "채점 엔진"
Cohesion: 0.22
Nodes (7): grade(), 채점 엔진 — 사용자 코드를 격리 프로세스에서 실행해 기능·효율 판정.  판정 철학(리서치 확정, 2026-07-20): - 기능: 히든 테스트, 사용자 코드 채점. 반환:     {passed, total, cases[], perf{}, verdict: 'pass'|'fail'|'time, 동일 코드가 아니어도 기능이 맞으면 pass (James 질문의 확정 답)., 개인 문제(~/.warfront2/custom)가 설치형과 병합 로드된다., test_custom_content_merge(), test_grader_functional_equivalence()

### Community 15 - "설계 계보·UX 참조"
Cohesion: 0.25
Nodes (8): 불변식: 콘텐츠 문자열 Rich 마크업 보간 금지, wf/app.py — Textual 앱 루트 + 전체 CSS, 중독 루프 (즉시 피드백 UX), 유형별 벨트 승급 (무술 단급제), 고스트 대결 (과거 기록 재생), smassh — MonkeyType TUI 클론 (2k★), Textual 8.x (TUI 프레임워크), warfront v1 프로토타입 (tmux 4-pane 전술 시뮬레이터)

### Community 16 - "타이핑 지표(WPM·정확도)"
Cohesion: 0.33
Nodes (1): 타이핑 엔진 — 키스트로크 판정·WPM·정확도 (순수 로직, UI 무관).  제1 원칙 "타건감"의 코어: 글자 단위 즉시 판정. 오타는 전진하

### Community 17 - "패키지 메타"
Cohesion: 1.0
Nodes (1): WARFRONT 2 — 50일 코테 합격 CLI 훈련기.

## Ambiguous Edges - Review These
- `wf/screens/home.py — 대시보드 (카타 테이블·단계 해금·스프린트)` → `FSRS 간격반복 스케줄러 (py-fsrs 6.x)`  [AMBIGUOUS]
  docs/DESIGN.md · relation: implements
- `속성 모드 Sprint Mode Banner (D1/7 — today: 어법+구현+해시, toggle t)` → `Progress Bar (partially filled horizontal gauge below kata table)`  [AMBIGUOUS]
  docs/img/dashboard.svg · relation: shares_data_with
- `Daily/Streak Mini Charts (일/연 sparkline panels)` → `유형 인식률 Stat (75% n=4 — 목표 90%+)`  [AMBIGUOUS]
  docs/img/dashboard.svg · relation: shares_data_with
- `BFS Reference Implementation (Python)` → `Staged Hints (F1 힌트(단계))`  [AMBIGUOUS]
  docs/img/kata.svg · relation: conceptually_related_to
- `Sample Question: Subset-Sum Count (N≤20 integers, sum S)` → `Intended Answer: 완전탐색/백트래킹 (N≤20 signal)`  [AMBIGUOUS]
  docs/img/drill.svg · relation: conceptually_related_to

## Knowledge Gaps
- **55 isolated node(s):** `career repo 싱크 — 오늘의 warfront 연습을 일일 루틴 관측에 반영.  James(2026-07-20): "warfront로 연`, `wf setup으로 설정한 개인 기록 repo(~/.warfront2)에 오늘 기록 push.`, `오늘 집계를 career repo에 기록하고 best-effort push. 반환: 상태 문자열.`, `세션 종료 시 호출 — career repo(James) + 개인 기록 repo(wf setup) 모두 best-effort.      ★어떤`, `WARFRONT 2 — 50일 코테 합격 CLI 훈련기.` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `타이핑 지표(WPM·정확도)`** (6 nodes): `accuracy()`, `done()`, `elapsed()`, `타이핑 엔진 — 키스트로크 판정·WPM·정확도 (순수 로직, UI 무관).  제1 원칙 "타건감"의 코어: 글자 단위 즉시 판정. 오타는 전진하`, `wpm()`, `typing_engine.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `패키지 메타`** (2 nodes): `__init__.py`, `WARFRONT 2 — 50일 코테 합격 CLI 훈련기.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `wf/screens/home.py — 대시보드 (카타 테이블·단계 해금·스프린트)` and `FSRS 간격반복 스케줄러 (py-fsrs 6.x)`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **What is the exact relationship between `속성 모드 Sprint Mode Banner (D1/7 — today: 어법+구현+해시, toggle t)` and `Progress Bar (partially filled horizontal gauge below kata table)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `Daily/Streak Mini Charts (일/연 sparkline panels)` and `유형 인식률 Stat (75% n=4 — 목표 90%+)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `BFS Reference Implementation (Python)` and `Staged Hints (F1 힌트(단계))`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Sample Question: Subset-Sum Count (N≤20 integers, sum S)` and `Intended Answer: 완전탐색/백트래킹 (N≤20 signal)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `TypingSession` connect `앱 코어·결과 화면` to `백지 구현 화면(solve)`, `카타 타이핑 화면`, `타이핑 판정 로직`, `채점 엔진`, `타이핑 지표(WPM·정확도)`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `KataScreen` connect `카타 타이핑 화면` to `앱 코어·결과 화면`, `인식 드릴 화면`, `백지 구현 화면(solve)`, `콘텐츠 로더`, `채점 엔진`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._