#!/usr/bin/env python3
"""README 히어로 로고 생성 — 터미널 프롬프트 모티프 + 실제 앱의 최종 단계 캐릭터.

디자인 언어: Catppuccin Mocha(앱 기본 테마) 위에 JetBrains Mono 워드마크.
왼쪽 `❯ wf` 프롬프트(커서 블록)가 정체성, 오른쪽 전설의 검성(10단계 아트)이 성장 서사.
합성 아님 — 캐릭터 아트는 wf/character.py에서 그대로 읽는다.

사용: python3 tools/logo.py   # → docs/img/logo.png
"""
from __future__ import annotations

import html
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from wf.character import STAGES  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "docs/img/logo.png"
W, H, SCALE = 880, 230, 2

BG, INK, MUTED = "#1e1e2e", "#cdd6f4", "#7f849c"
ACCENT, GOLD, PURPLE = "#a6e3a1", "#f9e2af", "#af87ff"

ART = STAGES[-1][3][0]  # 전설의 검성 프레임 A


def main() -> None:
    art = html.escape(ART)
    page = f'''<!doctype html><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ width:{W}px; height:{H}px; background:{BG};
       font-family:"JetBrains Mono","Apple SD Gothic Neo",monospace;
       display:flex; align-items:center; justify-content:space-between;
       padding:0 54px 0 58px; overflow:hidden }}
.left {{ display:flex; flex-direction:column; gap:14px }}
.prompt {{ font-size:54px; font-weight:800; color:{INK}; letter-spacing:-.01em }}
.prompt .chev {{ color:{ACCENT} }}
.prompt .cursor {{ display:inline-block; width:.55em; height:1.02em; background:{GOLD};
                   vertical-align:-.14em; margin-left:.12em }}
.tag {{ font-size:17px; color:{INK} }}
.tag b {{ color:{GOLD}; font-weight:700 }}
.sub {{ font-size:13px; color:{MUTED}; letter-spacing:.05em }}
.art {{ font-size:15px; line-height:1.1; color:{PURPLE}; text-align:left }}
.scan {{ position:fixed; inset:0; pointer-events:none;
        background:repeating-linear-gradient(0deg, transparent 0 3px, rgba(0,0,0,.10) 3px 4px) }}
</style><body>
<div class="left">
  <div class="prompt"><span class="chev">❯</span> wf<span class="cursor"></span></div>
  <div class="tag">터미널에서 크는 <b>파이썬 코딩테스트</b> 훈련</div>
  <div class="sub">warfront2 — 하루 30분 · 4단계 반복 · 유형 인식 드릴</div>
</div>
<pre class="art">{art}</pre>
<div class="scan"></div>
</body>'''
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "logo.html"
        src.write_text(page, encoding="utf-8")
        shot = Path(td) / "logo.png"
        proc = subprocess.Popen(
            [CHROME, "--headless", "--disable-gpu", "--no-first-run",
             f"--user-data-dir={td}/p", "--hide-scrollbars",
             f"--force-device-scale-factor={SCALE}", f"--window-size={W},{H}",
             f"--screenshot={shot}", str(src)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):
            if shot.exists() and shot.stat().st_size > 0:
                time.sleep(0.4)
                break
            if proc.poll() is not None:
                break
            time.sleep(0.25)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if not shot.exists():
            raise RuntimeError("로고 스크린샷 실패")
        from PIL import Image
        Image.open(shot).save(OUT, optimize=True)
    print(f"{OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
