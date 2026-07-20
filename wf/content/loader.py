"""카타 콘텐츠 로더."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

KATA_DIR = Path(__file__).parent / "katas"
PROBLEM_DIR = Path(__file__).parent / "problems"


@dataclass
class Kata:
    id: str
    type: str
    title: str
    belt: str
    think_prompt: str
    think_model: str
    code: str
    desc: str = ""
    expected_complexity: str = ""
    subgoals: list[dict] = field(default_factory=list)
    line_notes: dict = field(default_factory=dict)
    resources: list[dict] = field(default_factory=list)
    func: str = ""
    tests: list[dict] = field(default_factory=list)
    perf: dict | None = None
    diagram: dict | None = None

    def subgoal_char_range(self, idx: int) -> tuple[int, int]:
        """서브골 idx의 (시작, 끝+1) 문자 오프셋 — cloze 활성 구간 계산용."""
        lines = self.code.split("\n")
        lo, hi = self.subgoals[idx]["lines"]
        start = sum(len(l) + 1 for l in lines[:lo])
        end = sum(len(l) + 1 for l in lines[:hi + 1])
        return start, min(end, len(self.code))


def load_katas() -> list[Kata]:
    katas = []
    for p in sorted(KATA_DIR.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        katas.append(Kata(**data))
    return katas


def get_kata(kata_id: str) -> Kata:
    for k in load_katas():
        if k.id == kata_id:
            return k
    raise KeyError(kata_id)


def load_problems() -> list[Kata]:
    """변형 문제 은행 — 같은 유형, 다른 문제 (solve 전용)."""
    out = []
    for p in sorted(PROBLEM_DIR.glob("*.json")):
        out.append(Kata(**json.loads(p.read_text(encoding="utf-8"))))
    return out


def get_any(item_id: str) -> Kata:
    """카타·변형문제 통합 조회."""
    for k in load_katas() + load_problems():
        if k.id == item_id:
            return k
    raise KeyError(item_id)
