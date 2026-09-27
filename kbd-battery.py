#!/usr/bin/env python3
"""Keep the keyboard color tied to battery level: red (0%) -> yellow-green -> light blue (100%).
Pulses while charging, blinks below LOW_PERCENT while discharging, and blinks a few times
when charging stops at the (possibly custom) charge limit."""
import colorsys
import glob
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import kbd_led

INTERVAL = 5
HUE_AT_FULL = 0.55  # ~198deg, light blue
GAMMA = 1.4  # >1 stretches red/orange: 25% -> ~30deg orange, 50% -> ~75deg yellow-green
LOW_PERCENT = 10
PULSE_STEPS = 8  # frames per pulse cycle, 0.5s each
PULSE_MIN = 0.6  # dimmest pulse frame, as a fraction of the slider level
FULL_BLINKS = 5  # blinks when charging stops at the limit


def read_battery(name):
    with open(glob.glob(f"/sys/class/power_supply/BAT*/{name}")[0]) as f:
        return f.read().strip()


def battery_rgb(percent):
    r, g, b = colorsys.hsv_to_rgb(HUE_AT_FULL * (percent / 100) ** GAMMA, 1.0, 1.0)
    return round(r * 255), round(g * 255), round(b * 255)


def frame(level, percent, status, step):
    """(brightness, seconds until the next frame) for the current battery state."""
    if status == "Charging":
        pulse = PULSE_MIN + (1 - PULSE_MIN) * (1 + math.cos(2 * math.pi * step / PULSE_STEPS)) / 2
        return round(level * pulse), 0.5
    if status == "Discharging" and percent < LOW_PERCENT:
        return (level if step % 2 == 0 else 0), 1
    return level, INTERVAL


def blink_burst(rgb, level):
    """Blink the backlight FULL_BLINKS times (skipped if the slider is at 0)."""
    for _ in range(FULL_BLINKS if level else 0):
        kbd_led.write_led(*rgb, 0, persist=False)
        time.sleep(0.25)
        kbd_led.write_led(*rgb, level, persist=False)
        time.sleep(0.25)


if __name__ == "__main__":
    level = last = last_rgb = held_before = None
    step = 0
    while True:
        percent, status = int(read_battery("capacity")), read_battery("status")
        rgb = battery_rgb(percent)
        cur = kbd_led.current()[3]
        if cur != last:  # brightness we didn't write = the user moved the slider
            level = cur
        held = status in ("Full", "Not charging")  # plugged in, charging stopped (100% or the limit)
        if held and held_before is False:  # just got there (finished charging, or plugged in at the limit)
            blink_burst(rgb, level)
            last = None  # force a normal frame below
        held_before = held
        brightness, delay = frame(level, percent, status, step)
        if (rgb, brightness) != (last_rgb, last) or status == "Charging":  # skip identical writes (~20ms each)
            kbd_led.write_led(*rgb, brightness, persist=(brightness == level))
            last_rgb = rgb
        last, step = brightness, step + 1
        time.sleep(delay)
