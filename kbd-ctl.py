#!/usr/bin/env python3
"""Command line control, e.g. for keyboard shortcuts (texts come from kbd_i18n).
  kbd-ctl.py --color red|#FF8800|255,136,0
  kbd-ctl.py --brightness 40
  kbd-ctl.py --battery
  kbd-ctl.py --effect rainbow --speed 7
  kbd-ctl.py --off"""
import argparse
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import kbd_i18n
import kbd_led

t = kbd_i18n.t


def norm(text):
    """Lowercase letters only, accents stripped: "Arcoíris" -> "arcoiris"."""
    return "".join(ch for ch in unicodedata.normalize("NFD", text.lower()) if ch.isalpha())


# names are accepted in every language (and the internal Spanish/effect keys)
COLORS = {norm(name): rgb for name, rgb, _ in kbd_led.STANDARD_COLORS}
EFFECT_NAMES = {key: key for key in kbd_led.EFFECTS}
for strings in kbd_i18n.STRINGS.values():
    COLORS.update({norm(strings[f"color.{name}"]): rgb for name, rgb, _ in kbd_led.STANDARD_COLORS})
    EFFECT_NAMES.update({norm(strings[f"fx.{key}"]): key for key in kbd_led.EFFECTS})


def parse_color(text):
    if norm(text) in COLORS:
        return COLORS[norm(text)]
    if m := re.fullmatch(r"#?([0-9a-fA-F]{6})", text):
        return tuple(int(m[1][i:i + 2], 16) for i in (0, 2, 4))
    if m := re.fullmatch(r"(\d+)[, ]+(\d+)[, ]+(\d+)", text):
        rgb = tuple(int(x) for x in m.groups())
        if max(rgb) <= 255:
            return rgb
    sys.exit(t("cli_bad_color").format(text))


p = argparse.ArgumentParser(description=t("cli_desc"))
p.add_argument("--color", help=t("cli_color"))
p.add_argument("--brightness", type=int, choices=range(101), metavar="0-100", help=t("cli_brightness"))
p.add_argument("--battery", action="store_true", help=t("cli_battery"))
p.add_argument("--effect", metavar="NAME", help=f"{t('cli_effect')}: " + ", ".join(t(f"fx.{k}") for k in kbd_led.EFFECTS))
p.add_argument("--speed", type=int, choices=range(1, 11), metavar="1-10", help=t("cli_speed"))
p.add_argument("--off", action="store_true", help=t("cli_off"))
args = p.parse_args()
if not (args.color or args.brightness is not None or args.battery or args.off or args.effect):
    p.error(t("cli_need_arg"))

if args.battery:
    kbd_led.stop_modes()
    kbd_led.start_battery()
elif args.effect:
    key = EFFECT_NAMES.get(norm(args.effect))
    if not key:
        sys.exit(t("cli_bad_effect").format(args.effect))
    old, color = kbd_led.read_effect(), parse_color(args.color) if args.color else None
    r, g, b, brightness = kbd_led.current()
    if old:  # the LED shows a mid-animation frame: trust the config
        (r, g, b), brightness = old[2], old[3]
    kbd_led.stop_modes()
    kbd_led.start_effect(key, args.speed or (old[1] if old else 5), color or (r, g, b),
                         brightness or kbd_led.max_brightness())
elif args.off:
    kbd_led.stop_modes()
    kbd_led.write_led(0, 0, 0, 0)
else:
    color = parse_color(args.color) if args.color else None
    if color:
        kbd_led.stop_modes()
    r, g, b, brightness = kbd_led.current()
    if color:
        r, g, b = color
    if args.brightness is not None:
        brightness = round(kbd_led.max_brightness() * args.brightness / 100)
    elif color and brightness == 0:  # was off: a color should turn it on
        brightness = kbd_led.max_brightness()
    kbd_led.write_led(r, g, b, brightness)
