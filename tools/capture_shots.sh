#!/bin/bash
# warfront2 Ghostty 실창 캡처 3종(대시보드/따라치기/인식드릴) — README용.
# 실행 조건: 화면 기록 권한이 있는 터미널(새 cmux 등)에서:  bash tools/capture_shots.sh
# 실행 중 약 25초간 키보드·마우스를 건드리지 마세요.
#
# 함정 기록(2026-07-22, 2회 실패로 확립):
# ① AppleScript keystroke는 'tell process'와 무관하게 **맨 앞 앱**으로 간다 —
#    창 생성/명령 실행을 키 입력으로 하지 말 것 → Ghostty CLI --command로 직접 실행.
# ② Ghostty 인스턴스/창이 여러 개면 activate 대상이 모호해진다 → 시작 시 전부 종료.
# ③ 한글 keystroke는 IME를 안 타서 무시된다 → 접근 선언은 ASCII.
# ④ 캡처 직전 activate 안 하면 다른 앱 창이 겹쳐 찍힌다.
set -e
OUT=~/cursor/warfront2/docs/img/shots
mkdir -p "$OUT"

echo "▶ 기존 Ghostty 종료 후 wf 전용 창 실행..."
pkill -x ghostty 2>/dev/null || true
sleep 1.5
open -na Ghostty --args --command="/bin/zsh -lc 'cd ~/cursor/warfront2 && exec wf'"
sleep 4

osascript <<'EOS'
tell application "Ghostty" to activate
delay 0.6
tell application "System Events" to tell process "Ghostty"
  set position of front window to {80, 60}
  set size of front window to {1180, 780}
end tell
EOS
sleep 1.5

BOUNDS=$(osascript -e 'tell application "System Events" to tell process "Ghostty" to get {position, size} of front window' | tr -d ' ')
X=$(echo "$BOUNDS" | cut -d, -f1); Y=$(echo "$BOUNDS" | cut -d, -f2)
W=$(echo "$BOUNDS" | cut -d, -f3); H=$(echo "$BOUNDS" | cut -d, -f4)
echo "  창 영역: $X,$Y ${W}x${H}"

snap() {  # 캡처 직전 Ghostty를 최전면으로 — 겹침 방지
  osascript -e 'tell application "Ghostty" to activate' >/dev/null
  sleep 0.8
  screencapture -x -R"$X,$Y,$W,$H" "$OUT/$1" && echo "  ✓ $1"
}

echo "▶ 대시보드 캡처"
snap dashboard.png

echo "▶ 보고 치기(g) → 접근 선언(ASCII) → 타이핑 화면"
osascript <<'EOS'
tell application "Ghostty" to activate
delay 0.5
tell application "System Events"
  keystroke "g"
  delay 1.8
  keystroke "split -> token[1] = level, dict.get(level, 0) + 1"
  delay 0.4
  key code 36
end tell
EOS
sleep 2
snap kata.png

echo "▶ 홈 복귀(Esc) → 인식 드릴(i)"
osascript <<'EOS'
tell application "Ghostty" to activate
delay 0.5
tell application "System Events"
  key code 53
  delay 1.5
  keystroke "i"
end tell
EOS
sleep 2.5
snap drill.png

osascript -e 'tell application "System Events" to key code 53' >/dev/null
echo "✅ 완료 → $OUT (wf 창은 홈으로 남김)"
