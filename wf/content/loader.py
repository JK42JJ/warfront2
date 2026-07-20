"""카타 콘텐츠 로더."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

KATA_DIR = Path(__file__).parent / "katas"


@dataclass
class Kata:
    id: str
    type: str
    title: str
    belt: str
    think_prompt: str
    think_model: str
    code: str
    resources: list[dict] = field(default_factory=list)


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
