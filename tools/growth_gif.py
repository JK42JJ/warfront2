#!/usr/bin/env python3
"""성장 캐릭터 GIF 생성 — wf/character.py STAGES를 그대로 렌더해 '점차 자란다'를 표현.

파이프라인: 전 프레임을 세로로 쌓은 HTML 1장 → 헤드리스 Chrome 스크린샷(2x) → PIL 슬라이스 → GIF.
합성 아님: 아트·색·서사 모두 실제 앱 코드(wf/character.py)에서 읽는다.

사용: python3 tools/growth_gif.py   # → docs/img/growth.gif
"""
from __future__ import annotations

import html
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from wf.character import STAGES  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "docs/img/growth.gif"
W, H = 460, 340          # 프레임 논리 크기 (2x 렌더)
SCALE = 2

# rich 색 이름 → hex (Catppuccin Mocha 배경과 어울리게)
COLOR = {"grey70": "#b0b0b0", "bright_yellow": "#ffd75f", "yellow1": "#ffe74c",
         "chartreuse3": "#87d700", "dark_orange3": "#e8873a", "bright_white": "#eeeeee",
         "gold1": "#ffd700", "deep_sky_blue1": "#38b6ff", "red1": "#ff5f5f",
         "medium_purple1": "#af87ff"}
BG, INK, MUTED, BAR = "#1e1e2e", "#cdd6f4", "#7f849c", "#313244"


def frame_html(stage_i: int, frame: str) -> str:
    name, story, color, frames = STAGES[stage_i]
    art = html.escape(frames[frame == "B"] if isinstance(frame, str) else frames[frame])
    day = stage_i * 5
    pct = round(stage_i / (len(STAGES) - 1) * 100)
    c = COLOR.get(color, "#ffffff")
    return f'''<div class="fr">
  <div class="hd"><span class="day">DAY {day:02d}</span><span class="nm" style="color:{c}">{html.escape(name)}</span></div>
  <div class="art-wrap"><pre class="art" style="color:{c}">{art}</pre></div>
  <div class="story">{html.escape(story)}</div>
  <div class="bar"><div class="fill" style="width:{pct}%;background:{c}"></div></div>
</div>'''


def page_wrap(frames_html: str) -> str:
    return f'''<!doctype html><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ background:{BG}; width:{W}px }}
.fr {{ width:{W}px; height:{H}px; padding:22px 26px 18px; display:flex; flex-direction:column;
      font-family:"JetBrains Mono","Apple SD Gothic Neo",monospace }}
.hd {{ display:flex; justify-content:space-between; align-items:baseline }}
.day {{ color:{MUTED}; font-size:13px; letter-spacing:.14em }}
.nm {{ font-size:17px; font-weight:700 }}
.art-wrap {{ flex:1; display:flex; align-items:flex-end; justify-content:center; padding-bottom:10px }}
.art {{ font-size:20px; line-height:1.12; text-align:left }}
.story {{ color:{INK}; font-size:13px; text-align:center; margin-bottom:14px }}
.bar {{ height:5px; background:{BAR}; border-radius:3px; overflow:hidden }}
.fill {{ height:100% }}
</style><body>{frames_html}</body>'''


def main() -> None:
    # 프레임 시퀀스: 단계마다 idle A→B→A→B (성장 서사가 읽히는 속도)
    seq: list[tuple[int, int]] = []
    for i in range(len(STAGES)):
        seq += [(i, 0), (i, 1), (i, 0), (i, 1)]

    # 시트를 단계별(4프레임)로 쪼개 렌더 — 한 장짜리 초대형 시트(2x에서 16,384px 초과)는
    # Chrome 서피스 한계로 행업한다 (2026-07-22 실측 함정)
    from PIL import Image
    imgs: list[Image.Image] = []
    fw, fh = W * SCALE, H * SCALE
    with tempfile.TemporaryDirectory() as td:
        for i in range(len(STAGES)):
            chunk = seq[i * 4:(i + 1) * 4]
            src = Path(td) / f"s{i}.html"
            src.write_text(page_wrap("".join(frame_html(a, b) for a, b in chunk)),
                           encoding="utf-8")
            shot = Path(td) / f"s{i}.png"
            # Chrome은 파일을 쓰고도 프로세스가 안 죽는 경우가 있다(맥 실측) —
            # 파일 생성을 폴링해 확인하고 우리가 직접 종료한다
            proc = subprocess.Popen(
                [CHROME, "--headless", "--disable-gpu", "--no-first-run",
                 f"--user-data-dir={td}/p{i}", "--hide-scrollbars",
                 f"--force-device-scale-factor={SCALE}",
                 f"--window-size={W},{H * len(chunk)}",
                 f"--screenshot={shot}", str(src)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            for _ in range(120):
                if shot.exists() and shot.stat().st_size > 0:
                    time.sleep(0.4)          # 쓰기 마무리 여유
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
                raise RuntimeError(f"스크린샷 실패: stage {i}")
            sheet = Image.open(shot)
            imgs += [sheet.crop((0, k * fh, fw, (k + 1) * fh))
                          .convert("P", palette=Image.ADAPTIVE, colors=128)
                     for k in range(len(chunk))]

    # 타이밍: idle 420ms, 각 단계 마지막 프레임은 잠깐 여운, 최종 단계는 길게
    durs = []
    for k, (i, _f) in enumerate(seq):
        d = 420
        if k % 4 == 3:
            d = 700 if i < len(STAGES) - 1 else 2200
        durs.append(d)
    imgs[0].save(OUT, save_all=True, append_images=imgs[1:], duration=durs, loop=0,
                 optimize=True, disposal=2)
    print(f"{OUT} ({OUT.stat().st_size // 1024}KB, {len(seq)}프레임)")


if __name__ == "__main__":
    main()
