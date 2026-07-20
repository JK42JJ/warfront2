# ⚔ WARFRONT 2

**50일 코딩테스트 합격 CLI 훈련기.** 생각 먼저(Think-First), 구현은 그 다음 — 그 흐름을 타건으로 반복해 근육에 새긴다.

- 🧠 **THINK 게이트**: 접근을 선언(또는 ✏️연필 설계)해야 에디터가 열린다
- ⌨️ **4단계 카타**: 보고 따라치기 → 빈칸 → 안 보고 재현 → 스스로 구현(히든 테스트+효율성 판정)
- 📊 **대시보드**: 50일 진행 · 카타별 단계 횟수 · 연속일
- 🖼 **F1 힌트**(서브골→라인 설명) · **F2 개념도**(애니메이션+단계 타임라인)
- 🔁 콘텐츠 15종 = 30일 커리큘럼 전 유형(구현·해시·그리디·스택·힙·백트래킹·BFS·DFS·문자열·DP×2·이분탐색·투포인터·다익스트라)

## 설치 (macOS / Windows)

전제: **Python 3.10+** 와 **git**.

```bash
# 1) (선택) GitHub에서 Fork 후 본인 fork를 clone — 또는 원본을 바로 clone
git clone https://github.com/JK42JJ/warfront2.git
cd warfront2

# 2) 설치
pip install -e .

# 3) 실행
wf
```

- **macOS**: 기본 터미널/iTerm2/Ghostty 모두 OK.
- **Windows**: [Windows Terminal](https://aka.ms/terminal) + `py -m pip install -e .` 권장. (`wf`가 PATH에 없으면 `py -m wf.cli`)

## 명령

| 명령 | 설명 |
|---|---|
| `wf` | 훈련 시작 (대시보드) |
| `wf update` | **메인 repo에서 최신 문제/기능 받기** (git pull) |
| `wf version` | 앱·콘텐츠 버전 + 카타 수 |
| `wf setup <내 repo URL>` | **훈련 기록을 내 GitHub repo로 자동 push** (아래) |
| `wf reset` | 기록 전체 초기화 |

## 훈련 기록을 GitHub에서 관리하기

1. GitHub에서 **빈 private repo** 생성 (예: `my-warfront-records`)
2. `wf setup https://github.com/<나>/my-warfront-records.git`
3. 이후 **세션이 끝날 때마다** `~/.warfront2/records/날짜.json`(세션수·분·카타·정확도)이 자동 커밋·push — 스트릭·이력이 GitHub에 쌓인다. (DB 원본은 로컬 전용, push 실패는 조용히 재시도)

## 키 (훈련 중)

`⏎` 다음 단계 자동 · `g/b/r/s` 모드 선택 · `F1` 힌트 · `F2` 개념도 · `Ctrl+R` 채점(구현) · `ESC` 홈

설계·근거: [docs/DESIGN.md](docs/DESIGN.md) — 코테 출제 메타·교육학 리서치 기반.
