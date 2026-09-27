#!/bin/bash

LED_PATH="/sys/class/leds/rgb:kbd_backlight"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

i18n() { python3 "$SCRIPT_DIR/kbd_i18n.py" "$1"; }
[ -d "$LED_PATH" ] || { notify-send "$(i18n title)" "$(i18n err_no_led): $LED_PATH"; exit 1; }

exec python3 "$SCRIPT_DIR/kbd-panel.py"
