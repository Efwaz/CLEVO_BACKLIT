#!/usr/bin/env python3
"""Animated effects for the single-zone keyboard LED, driven by kbd-effect.txt
("name|speed|r g b|brightness", re-read every 0.5s so the panel can change speed live)."""
import colorsys
import math
import os
import random
import re
import select
import struct
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import kbd_led

FRAME = 0.02  # pause between frames; each LED write takes ~20ms, so ~20-25 fps overall
EVENT = struct.Struct("llHHi")  # struct input_event on 64-bit Linux
EV_REP_AND_LED = (1 << 20) | (1 << 17)  # real keyboards report both; buttons/switches don't


def hsv(h, s=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, 1.0)
    return round(r * 255), round(g * 255), round(b * 255)


# Each effect: (t seconds, rate = speed/5, base rgb) -> (rgb, fraction of the slider brightness)

def breathing(t, rate, base):
    return base, 0.05 + 0.95 * (0.5 - 0.5 * math.cos(2 * math.pi * t * rate / 5))


def rainbow(t, rate, base):
    return hsv(t * rate / 10), 1.0


def wave(t, rate, base):
    """Hue swings ~±40deg around the base color while brightness ripples."""
    h, s, _ = colorsys.rgb_to_hsv(*(c / 255 for c in base))
    h = h if s > 0.1 else 0.55  # white/grey has no hue: swing around light blue
    phase = 2 * math.pi * t * rate / 6
    return hsv(h + 0.11 * math.sin(phase)), 0.65 + 0.35 * math.sin(phase + math.pi / 2)


def heartbeat(t, rate, base):
    p = (t * rate / 1.6) % 1.0
    bump = lambda center: math.exp(-(((p - center) / 0.07) ** 2))
    return base, 0.08 + 0.92 * max(bump(0.05), 0.7 * bump(0.27))


class Fire:
    """Warm flicker; ignores the base color."""
    def __init__(self):
        self.v = self.target = 0.6
        self.next = 0.0

    def __call__(self, t, rate, base):
        if t >= self.next:
            self.target = random.random()
            self.next = t + random.uniform(0.05, 0.2) / rate
        self.v += (self.target - self.v) * 0.3
        return hsv(0.01 + 0.07 * self.v), 0.35 + 0.65 * self.v


class Reactive:
    """Dim at rest; every key press flashes to full and fades out. Only press times are used."""
    def __init__(self):
        self.last = -1e9
        threading.Thread(target=self._watch, daemon=True).start()

    def _watch(self):
        try:
            with open("/proc/bus/input/devices") as f:
                blocks = f.read().split("\n\n")
            events = [m[1] for b in blocks
                      if (m := re.search(r"Handlers=.*\b(event\d+)", b)) and " kbd" in b
                      and (e := re.search(r"B: EV=([0-9a-f]+)", b))
                      and int(e[1], 16) & EV_REP_AND_LED == EV_REP_AND_LED]
            fds = [os.open(f"/dev/input/{ev}", os.O_RDONLY) for ev in events]
        except OSError as e:
            print(f"kbd-effects: cannot read keyboards: {e}", file=sys.stderr)
            return
        while True:
            for fd in select.select(fds, [], [])[0]:
                data = os.read(fd, EVENT.size * 16)
                for i in range(0, len(data) - EVENT.size + 1, EVENT.size):
                    _, _, etype, _, value = EVENT.unpack_from(data, i)
                    if etype == 1 and value == 1:  # EV_KEY, key down
                        self.last = time.monotonic()

    def __call__(self, t, rate, base):
        return base, 0.2 + 0.8 * math.exp(-(time.monotonic() - self.last) * rate / 0.4)


EFFECTS = {"respiracion": lambda: breathing, "arcoiris": lambda: rainbow, "onda": lambda: wave,
           "latido": lambda: heartbeat, "fuego": Fire, "pulsacion": Reactive}


def main():
    name = fx = None
    level = last = last_out = None
    t0, next_cfg = time.monotonic(), 0.0
    while True:
        now = time.monotonic()
        if now >= next_cfg:
            cfg = kbd_led.read_effect()
            if not cfg or cfg[0] not in EFFECTS:
                return  # config removed (mode stopped) or unknown effect
            next_cfg = now + 0.5
            if cfg[0] != name:
                name, fx = cfg[0], EFFECTS[cfg[0]]()
            if level is None:
                level = cfg[3]  # not the LED's leftover brightness from a previous effect
        _, speed, base, _ = cfg
        rgb, factor = fx(now - t0, speed / 5, base)
        cur = kbd_led.current()[3]
        if last is not None and cur != last:  # brightness we didn't write = the user moved the slider
            level = cur
            kbd_led.write_effect(name, speed, base, level)  # so it survives a reboot
        brightness = round(level * factor)
        if (rgb, brightness) != last_out:
            kbd_led.write_led(*rgb, brightness, persist=False)
            last_out, last = (rgb, brightness), brightness
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
