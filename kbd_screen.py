#!/usr/bin/env python3
"""Screen-region color helpers (slurp + grim). Run directly with a slurp geometry
("x,y wxh") to keep the keyboard on that region's dominant color, live."""
import math
import os
import re
import resource
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import kbd_led

MAX_LOAD = 0.35  # CPU budget for capturing (fraction of one core): big regions are captured less often
TAU = 0.08  # seconds for the shown color to close ~63% of the gap to the target (lower = snappier)
FRAME = 0.005  # idle pause between LED updates (each write takes ~13ms)
PERSIST_EVERY = 2.0
STICKY = 0.7  # previous color stays unless a rival bucket has >1/0.7 times its pixels
SAMPLES = 64  # sample grid per axis


def dominant_color(ppm, prev=None):
    """Most common color of a binary PPM: bucket sampled pixels (8 levels/channel) and return the
    mean of the biggest bucket. With `prev`, keep its bucket unless another one clearly beats it."""
    m = re.match(rb"P6\s+(\d+)\s+(\d+)\s+255\s", ppm)
    w, h = int(m[1]), int(m[2])
    step_x, step_y = max(1, w // SAMPLES), max(1, h // SAMPLES)
    buckets = {}  # (r>>5, g>>5, b>>5) -> [count, sum_r, sum_g, sum_b]
    for y in range(0, h, step_y):
        row = m.end() + y * w * 3
        for r, g, b in zip(ppm[row:row + w * 3:3 * step_x],
                           ppm[row + 1:row + w * 3:3 * step_x],
                           ppm[row + 2:row + w * 3:3 * step_x]):
            acc = buckets.setdefault((r >> 5, g >> 5, b >> 5), [0, 0, 0, 0])
            acc[0] += 1
            acc[1] += r
            acc[2] += g
            acc[3] += b
    best = max(buckets.values(), key=lambda a: a[0])
    keep = buckets.get(tuple(c >> 5 for c in prev)) if prev else None
    count, sr, sg, sb = keep if keep and keep[0] >= STICKY * best[0] else best
    return round(sr / count), round(sg / count), round(sb / count)


def select_region():
    """Geometry picked with slurp, or None if cancelled. FileNotFoundError if slurp is missing."""
    res = subprocess.run(["slurp"], capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else None


def capture(geometry):
    """PPM bytes of a screen region. FileNotFoundError / CalledProcessError if grim is missing/fails."""
    return subprocess.run(["grim", "-g", geometry, "-t", "ppm", "-"],
                          capture_output=True, check=True).stdout


def _cpu_seconds():
    """CPU time used so far by this process and its children (grim)."""
    own, kids = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime


def _track(geometry, target):
    """Capture thread: keep target[0] at the region's current dominant color. Runs at the
    configured rate (kbd_led.screen_fps) without using more than MAX_LOAD of a core (cost grows with region size)."""
    while True:
        wall0, cpu0 = time.monotonic(), _cpu_seconds()
        try:
            target[0] = dominant_color(capture(geometry), prev=target[0])
        except (OSError, subprocess.CalledProcessError, TypeError, ValueError):
            pass  # transient (screen locked, output change): keep the last color
        period = max(1 / kbd_led.screen_fps(), (_cpu_seconds() - cpu0) / MAX_LOAD)
        time.sleep(max(0.0, period - (time.monotonic() - wall0)))


def main(geometry):
    target = [None]
    threading.Thread(target=_track, args=(geometry, target), daemon=True).start()
    shown = None  # float rgb currently on the LED
    last_rgb, last_persist, last_tick = None, 0.0, time.monotonic()
    while True:
        now = time.monotonic()
        dt, last_tick = now - last_tick, now
        if target[0]:
            if shown is None:
                shown = [float(c) for c in target[0]]
            else:  # time-based easing: same feel whatever the frame rate
                alpha = 1 - math.exp(-dt / TAU)
                for i, want in enumerate(target[0]):
                    step = (want - shown[i]) * alpha
                    shown[i] += step if abs(step) >= 0.5 else (want > shown[i]) - (want < shown[i])
            rgb = tuple(round(c) for c in shown)
            if rgb != last_rgb:
                persist = now - last_persist > PERSIST_EVERY  # avoid a disk write per frame
                kbd_led.write_led(*rgb, kbd_led.current()[3], persist=persist)  # slider's brightness
                last_rgb = rgb
                if persist:
                    last_persist = now
        time.sleep(FRAME)


if __name__ == "__main__":
    main(sys.argv[1])
