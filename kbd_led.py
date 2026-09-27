import os
import signal
import subprocess
import sys
import time

VERSION = "1.0"
LED_PATH = "/sys/class/leds/rgb:kbd_backlight"
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FAVORITES_FILE = os.path.join(_SCRIPT_DIR, "kbd-favorites.txt")
STATE_FILE = os.path.join(_SCRIPT_DIR, "kbd-state.txt")
BATTERY_FLAG = os.path.join(_SCRIPT_DIR, "kbd-battery.enabled")  # exists = battery mode survives reboot

STANDARD_COLORS = [
    ("Blanco", (255, 255, 255), None),
    ("Rojo", (255, 0, 0), None),
    ("Verde", (0, 255, 0), None),
    ("Azul", (0, 0, 255), None),
    ("Morado", (180, 0, 255), None),
    ("Cian", (0, 255, 255), None),
    ("Apagado", (0, 0, 0), 0),
]

# background modes -> script that runs them
SCREEN_FPS_FILE = os.path.join(_SCRIPT_DIR, "kbd-rate.txt")
SCREEN_FPS_CHOICES = (10, 15, 20, 30)  # grim needs ~30ms per capture, so 30 is about the ceiling
EFFECT_FILE = os.path.join(_SCRIPT_DIR, "kbd-effect.txt")  # exists = effect mode on (and survives reboot)

EFFECTS = ("respiracion", "arcoiris", "onda", "pulsacion", "fuego", "latido")  # texts live in kbd_i18n

_MODES = {"battery": "kbd-battery.py", "screen": "kbd_screen.py", "effect": "kbd-effects.py"}


def max_brightness():
    with open(f"{LED_PATH}/max_brightness") as f:
        return int(f.read().strip())


def current():
    with open(f"{LED_PATH}/multi_intensity") as f:
        r, g, b = (int(x) for x in f.read().split())
    with open(f"{LED_PATH}/brightness") as f:
        brightness = int(f.read().strip())
    return r, g, b, brightness


def write_led(r, g, b, brightness, persist=True):
    """Set color and brightness, writing only what differs: every sysfs write costs ~13ms
    (two firmware calls). A color write also re-applies the current brightness in the driver."""
    try:
        cur_r, cur_g, cur_b, cur_brightness = current()
        if (cur_r, cur_g, cur_b) != (r, g, b):
            with open(f"{LED_PATH}/multi_intensity", "w") as f:
                f.write(f"{r} {g} {b}")
        if cur_brightness != brightness:
            with open(f"{LED_PATH}/brightness", "w") as f:
                f.write(str(brightness))
    except OSError:
        return
    if persist:
        with open(STATE_FILE, "w") as f:
            f.write(f"{r} {g} {b}|{brightness}\n")


# ---------- background modes (battery / live screen) ----------

def _pids(mode=None):
    """PIDs of running mode processes, found by scanning /proc (no pid files to go stale)."""
    scripts = [_MODES[mode]] if mode else list(_MODES.values())
    pids = []
    for entry in os.listdir("/proc"):
        if entry.isdigit():
            try:
                with open(f"/proc/{entry}/cmdline") as f:
                    argv = f.read().split("\0")
            except OSError:
                continue
            if any(os.path.basename(a) in scripts for a in argv[1:2]):
                pids.append(int(entry))
    return pids


def mode_running(mode=None):
    """Is the given mode ("battery"/"screen"), or with no argument any mode, running?"""
    return bool(_pids(mode))


def stop_modes():
    """Stop every background mode and disable its persistence across reboots."""
    for path in (BATTERY_FLAG, EFFECT_FILE):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    for pid in _pids():
        os.kill(pid, signal.SIGTERM)
    for _ in range(50):  # wait (<=0.5s) so nothing writes to the LED after we return
        if not _pids():
            break
        time.sleep(0.01)


def _spawn(*args):
    subprocess.Popen([sys.executable, *args], start_new_session=True)


def start_battery():
    open(BATTERY_FLAG, "w").close()
    if not mode_running("battery"):
        _spawn(os.path.join(_SCRIPT_DIR, "kbd-battery.py"))


def start_screen(geometry):
    _spawn(os.path.join(_SCRIPT_DIR, "kbd_screen.py"), geometry)


def read_effect():
    """(name, speed 1-10, (r, g, b), brightness) from the effect config, or None."""
    try:
        with open(EFFECT_FILE) as f:
            name, speed, rgb, level = f.read().strip().split("|")
        return name, int(speed), tuple(int(c) for c in rgb.split()), int(level)
    except (OSError, ValueError):
        return None


def write_effect(name, speed, rgb, level):
    tmp = EFFECT_FILE + ".tmp"  # replace atomically: the daemon re-reads this file constantly
    with open(tmp, "w") as f:
        f.write(f"{name}|{speed}|{rgb[0]} {rgb[1]} {rgb[2]}|{level}\n")
    os.replace(tmp, EFFECT_FILE)


def start_effect(name, speed, rgb, level):
    """rgb is the base color; a black base (LED off) becomes white."""
    write_effect(name, speed, rgb if any(rgb) else (255, 255, 255), level)
    if not mode_running("effect"):
        _spawn(os.path.join(_SCRIPT_DIR, "kbd-effects.py"))


def screen_fps():
    """Captures per second for live-screen mode (user setting, re-read while the mode runs)."""
    try:
        with open(SCREEN_FPS_FILE) as f:
            fps = int(f.read())
        return fps if fps in SCREEN_FPS_CHOICES else SCREEN_FPS_CHOICES[-1]
    except (OSError, ValueError):
        return SCREEN_FPS_CHOICES[-1]


def set_screen_fps(fps):
    with open(SCREEN_FPS_FILE, "w") as f:
        f.write(str(fps))
