---
type: "query"
date: "2026-07-20T09:03:29.518997+00:00"
question: "home.py와 FSRS 스케줄러의 정확한 관계는?"
contributor: "graphify"
source_nodes: ["wf/screens/home.py — 대시보드", "FSRS 간격반복 스케줄러 (py-fsrs 6.x)"]
---

# Q: home.py와 FSRS 스케줄러의 정확한 관계는?

## Answer

설계-구현 간극: pyproject.toml에 fsrs>=6.0 의존성 선언, curriculum.yaml 홀수일 규칙이 FSRS 복습 참조. 그러나 wf/ 코드에 fsrs import 없음(2026-07-20 grep 실측). home.py는 95% 진급 게이트만 구현. FSRS 스케줄러 본체는 M3 미구현 — D31~50 반복 구간이 의존하므로 D30(8월 중순) 전 구현 필요.

## Source Nodes

- wf/screens/home.py — 대시보드
- FSRS 간격반복 스케줄러 (py-fsrs 6.x)