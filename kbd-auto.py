#!/usr/bin/env python3
"""Automatic backlight (hours from kbd-auto.txt if set): off in daylight, on (saved color/brightness) from sunset until sunrise."""
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import kbd_led

LAT, LON = 4.71, -74.07  # Bogota; ponytail: hardcoded, make it a setting if the laptop travels
INTERVAL = 30


def sun_times(now):
    """(sunrise, sunset) as UTC datetimes for now's UTC date (NOAA approximation, ~1 min).
    ponytail: UTC date, wrong only for longitudes far from the Americas."""
    g = 2 * math.pi / 365 * (now.timetuple().tm_yday - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    lat = math.radians(LAT)
    cos_ha = math.cos(math.radians(90.833)) / (math.cos(lat) * math.cos(decl)) - math.tan(lat) * math.tan(decl)
    ha = math.degrees(math.acos(max(-1, min(1, cos_ha))))
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight + timedelta(minutes=720 - 4 * (LON + ha) - eqtime),
            midnight + timedelta(minutes=720 - 4 * (LON - ha) - eqtime))


def is_night(now):
    hours = kbd_led.read_auto_hours()  # user-chosen (on, off) in local time, else the sun
    if hours:
        on, off = hours
        m = now.astimezone().hour * 60 + now.astimezone().minute
        return (on <= m < off) if on < off else (m >= on or m < off)
    rise, sset = sun_times(now)
    return now < rise or now >= sset


def apply(night):
    """Night: restore the saved static color. Day: brightness 0 (not saved, so the color survives)."""
    try:
        with open(kbd_led.STATE_FILE) as f:
            color, level = f.read().strip().split("|")
        r, g, b = (int(c) for c in color.split())
        level = int(level)
    except (OSError, ValueError):
        r = g = b = 255
        level = 0
    if not any((r, g, b)):  # saved state was "off": a black night color would show nothing
        r = g = b = 255
    if night:
        kbd_led.write_led(r, g, b, level or kbd_led.max_brightness(), persist=False)
    else:
        kbd_led.write_led(r, g, b, 0, persist=False)


def demo():
    day = datetime(2026, 10, 25, tzinfo=timezone.utc)
    rise, sset = sun_times(day)
    assert 10.5 < rise.hour + rise.minute / 60 < 11.5, rise  # ~06:00 Bogota
    assert 22.5 < sset.hour + sset.minute / 60 < 23.5, sset  # ~18:00 Bogota
    assert is_night(day.replace(hour=2)) and not is_night(day.replace(hour=17))
    assert kbd_led.parse_hours("18:00-06:30") == (1080, 390) and not kbd_led.parse_hours("25:00-1:00")
    print("ok", rise, sset)


if __name__ == "__main__":
    if "--test" in sys.argv:
        demo()
        sys.exit()
    last = None
    while True:
        night = is_night(datetime.now(timezone.utc))
        if night != last:  # only on transitions, so slider changes in between are respected
            apply(night)
            last = night
        time.sleep(INTERVAL)
