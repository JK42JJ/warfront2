"""채점 엔진 — 사용자 코드를 격리 프로세스에서 실행해 기능·효율 판정.

판정 철학(리서치 확정, 2026-07-20):
- 기능: 히든 테스트케이스 통과 = pass (변수명·구현 방식 자유 — 기능 동등이면 인정)
- 효율: 대형 입력 + 시간제한(타임아웃 게이트, HackerRank/프로그래머스 방식).
  복잡도 '실측'은 판정 권위로 쓰지 않는다(오판 실증됨) — 기대 복잡도는 표기만.

구현: 사용자 코드 + 테스트를 임시 러너 스크립트로 만들어 subprocess 실행(타임아웃),
결과는 JSON 한 줄로 회수. 로컬 자기학습 도구 = 무거운 샌드박스 불요(설계서 §5).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

RUNNER_TEMPLATE = '''
import json, time, sys, ast

# ---- 사용자 코드 ----
{user_code}

# ---- 채점 ----
_results = []
_tests = json.loads({tests_json!r})
def _norm(v):
    """튜플/리스트 차이 무시 — JSON 왕복으로 정규화(기능 동등 판정)."""
    try:
        return json.loads(json.dumps(v))
    except (TypeError, ValueError):
        return v

for _t in _tests:
    try:
        _args = ast.literal_eval(_t["args_repr"]) if "args_repr" in _t else _t["args"]
        _got = {func}(*_args)
        _ok = _norm(_got) == _norm(_t["expected"])
        _results.append({{"ok": _ok, "got": repr(_got), "expected": repr(_t["expected"])}})
    except Exception as _e:
        _results.append({{"ok": False, "error": f"{{type(_e).__name__}}: {{_e}}"}})

_perf = None
_perf_spec = {perf_json!r}
if _perf_spec != "null":
    _p = json.loads(_perf_spec)
    _g = {{}}
    exec(_p["gen"], _g)          # 대형 입력 생성 (콘텐츠 제공 코드)
    _args = _g["make_args"]()
    _t0 = time.perf_counter()
    try:
        {func}(*_args)
        _elapsed = time.perf_counter() - _t0
        _perf = {{"elapsed": round(_elapsed, 3), "limit": _p["time_limit"],
                  "ok": _elapsed <= _p["time_limit"]}}
    except Exception as _e:
        _perf = {{"elapsed": None, "limit": _p["time_limit"], "ok": False,
                  "error": f"{{type(_e).__name__}}: {{_e}}"}}

print(json.dumps({{"cases": _results, "perf": _perf}}))
'''


def grade(user_code: str, func: str, tests: list[dict],
          perf: dict | None = None, hard_timeout: float = 15.0) -> dict:
    """사용자 코드 채점. 반환:
    {passed, total, cases[], perf{}, verdict: 'pass'|'fail'|'timeout'|'crash'}"""
    script = RUNNER_TEMPLATE.format(
        user_code=user_code,
        func=func,
        tests_json=json.dumps(tests, ensure_ascii=False),
        perf_json=json.dumps(perf, ensure_ascii=False) if perf else "null",
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as f:
        f.write(script)
        path = f.name
    try:
        proc = subprocess.run([sys.executable, path], capture_output=True,
                              text=True, timeout=hard_timeout)
    except subprocess.TimeoutExpired:
        return {"passed": 0, "total": len(tests), "cases": [],
                "perf": None, "verdict": "timeout",
                "detail": f"전체 실행이 {hard_timeout}초 초과 (무한루프?)"}
    finally:
        Path(path).unlink(missing_ok=True)

    if proc.returncode != 0 or not proc.stdout.strip():
        err = (proc.stderr or "").strip().splitlines()
        return {"passed": 0, "total": len(tests), "cases": [],
                "perf": None, "verdict": "crash",
                "detail": err[-1] if err else "실행 실패"}

    data = json.loads(proc.stdout.strip().splitlines()[-1])
    cases = data["cases"]
    passed = sum(1 for c in cases if c.get("ok"))
    perf_res = data.get("perf")
    func_ok = passed == len(cases)
    perf_ok = (perf_res is None) or perf_res.get("ok", False)
    return {
        "passed": passed, "total": len(cases), "cases": cases,
        "perf": perf_res,
        "verdict": "pass" if (func_ok and perf_ok) else "fail",
    }
