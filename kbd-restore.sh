#!/bin/bash

LED_PATH="/sys/class/leds/rgb:kbd_backlight"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
STATE_FILE="$SCRIPT_DIR/kbd-state.txt"

[ -d "$LED_PATH" ] || exit 0

# Battery/effect mode enabled: hand over to the daemon (service is Type=simple, so it stays alive)
[ -f "$SCRIPT_DIR/kbd-battery.enabled" ] && exec python3 "$SCRIPT_DIR/kbd-battery.py"
[ -f "$SCRIPT_DIR/kbd-effect.txt" ] && exec python3 "$SCRIPT_DIR/kbd-effects.py"

[ -f "$STATE_FILE" ] || exit 0

IFS='|' read -r COLOR BRIGHTNESS < "$STATE_FILE"
echo "$COLOR" > "$LED_PATH/multi_intensity"
echo "$BRIGHTNESS" > "$LED_PATH/brightness"
