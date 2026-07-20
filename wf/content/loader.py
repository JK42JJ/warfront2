"""카타 콘텐츠 로더."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

KATA_DIR = Path(__file__).parent / "katas"
PROBLEM_DIR = Path(__file__).parent / "problems"
# 개인 콘텐츠 — 설치형과 분리 (wf update 영향 없음, 기록 repo로 백업됨)
CUSTOM_DIR = Path.home() / ".warfront2/custom"


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


def _load_dir(d: Path) -> list[Kata]:
    out = []
    if d.exists():
        for p in sorted(d.glob("*.json")):
            out.append(Kata(**json.loads(p.read_text(encoding="utf-8"))))
    return out


def load_katas() -> list[Kata]:
    """설치형 카타 + 개인 카타(~/.warfront2/custom/katas)."""
    return _load_dir(KATA_DIR) + _load_dir(CUSTOM_DIR / "katas")


def get_kata(kata_id: str) -> Kata:
    for k in load_katas():
        if k.id == kata_id:
            return k
    raise KeyError(kata_id)


def load_problems() -> list[Kata]:
    """변형 문제 은행 (설치형 + 개인)."""
    return _load_dir(PROBLEM_DIR) + _load_dir(CUSTOM_DIR / "problems")


def get_any(item_id: str) -> Kata:
    """카타·변형문제 통합 조회."""
    for k in load_katas() + load_problems():
        if k.id == item_id:
            return k
    raise KeyError(item_id)
