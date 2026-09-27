#!/usr/bin/env python3
import colorsys
import math
import os
import re
import subprocess
import sys
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import kbd_i18n
import kbd_led
import kbd_screen

t = kbd_i18n.t

def load_favorites(max_brightness):
    favs = []
    if os.path.exists(kbd_led.FAVORITES_FILE):
        with open(kbd_led.FAVORITES_FILE) as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue
                name, rgb, brightness = raw.split("|")
                r, g, b = (int(x) for x in rgb.split())
                percent = round(int(brightness) * 100 / max_brightness) if max_brightness else 0
                favs.append((name, (r, g, b), percent, raw))
    return favs


GRID_SIZE = (270, 310)
CUSTOM_SIZE = GRID_SIZE
WHEEL_SIZE = 120


class ColorWheel(Gtk.DrawingArea):
    """Circular hue/saturation picker. Value is fixed at 1.0 —
    overall intensity is handled separately by the brightness slider."""

    def __init__(self, size=WHEEL_SIZE):
        super().__init__()
        self.size = size
        self.hue = 0.0
        self.sat = 0.0
        self.on_change = None
        self.set_size_request(size, size)
        self._surface = self._render_wheel()

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.connect("draw", self._on_draw)
        self.connect("button-press-event", self._on_pointer)
        self.connect("motion-notify-event", self._on_pointer)

    def _render_wheel(self):
        size = self.size
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        stride = surface.get_stride()
        buf = surface.get_data()
        cx = cy = size / 2
        radius = size / 2
        for py in range(size):
            row = py * stride
            dy = py - cy
            for px in range(size):
                dx = px - cx
                dist = math.hypot(dx, dy)
                off = row + px * 4
                if dist > radius:
                    buf[off:off + 4] = b"\x00\x00\x00\x00"
                    continue
                hue = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
                sat = min(dist / radius, 1.0)
                r, g, b = colorsys.hsv_to_rgb(hue, sat, 1.0)
                buf[off] = round(b * 255)
                buf[off + 1] = round(g * 255)
                buf[off + 2] = round(r * 255)
                buf[off + 3] = 255
        surface.mark_dirty()
        return surface

    def set_hue_sat(self, hue, sat):
        self.hue, self.sat = hue, sat
        self.queue_draw()

    def set_rgb(self, r, g, b):
        h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        self.set_hue_sat(h, s)

    def get_rgb(self):
        r, g, b = colorsys.hsv_to_rgb(self.hue, self.sat, 1.0)
        return round(r * 255), round(g * 255), round(b * 255)

    def _on_draw(self, _widget, ctx):
        ctx.set_source_surface(self._surface, 0, 0)
        ctx.paint()
        cx = cy = self.size / 2
        radius = self.size / 2
        dist = self.sat * radius
        angle = self.hue * 2 * math.pi
        ix = cx + dist * math.cos(angle)
        iy = cy + dist * math.sin(angle)
        ctx.set_line_width(2)
        ctx.set_source_rgb(0, 0, 0)
        ctx.arc(ix, iy, 6, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(ix, iy, 4, 0, 2 * math.pi)
        ctx.fill()

    def _on_pointer(self, _widget, event):
        if event.type == Gdk.EventType.MOTION_NOTIFY:
            if not (event.state & Gdk.ModifierType.BUTTON1_MASK):
                return False
        cx = cy = self.size / 2
        radius = self.size / 2
        dx = event.x - cx
        dy = event.y - cy
        sat = min(math.hypot(dx, dy) / radius, 1.0)
        hue = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
        self.set_hue_sat(hue, sat)
        if self.on_change:
            self.on_change()
        return True


class Panel(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._i18n = []  # (setter, key) pairs, re-applied when the language changes
        self._tr(self.set_title, "title")
        self.set_default_size(*GRID_SIZE)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        self.max_brightness = kbd_led.max_brightness()
        r, g, b, brightness = kbd_led.current()
        cfg = kbd_led.read_effect()
        if cfg and kbd_led.mode_running("effect"):  # the LED shows a mid-animation frame
            (r, g, b), brightness = cfg[2], cfg[3]
        self.current_rgb = (r, g, b)

        self.stack = Gtk.Stack()
        self.stack.set_hhomogeneous(False)
        self.stack.set_vhomogeneous(False)
        self.add(self.stack)

        self.stack.add_named(self._build_grid_view(brightness), "grid")
        self.stack.add_named(self._build_custom_view(), "custom")
        self.stack.set_visible_child_name("grid")

        self.connect("destroy", lambda w: Gtk.main_quit())

    # ---------- grid view ----------

    def _build_grid_view(self, brightness):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(6)

        header = Gtk.Box()
        title = Gtk.Label(xalign=0)
        title.get_style_context().add_class("dim-label")
        self._tr(title.set_text, "title")
        header.pack_start(title, True, True, 0)
        header.pack_end(self._build_settings_button(), False, False, 0)
        box.pack_start(header, False, False, 0)

        self.flow = Gtk.FlowBox()
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_max_children_per_line(6)
        self.flow.set_min_children_per_line(6)
        self.flow.set_homogeneous(True)
        self.flow.set_row_spacing(3)
        self.flow.set_column_spacing(3)
        box.pack_start(self.flow, False, False, 0)
        self._populate_flow()

        box.pack_start(self._label("brightness"), False, False, 0)
        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        init_percent = round(brightness * 100 / self.max_brightness) if self.max_brightness else 0
        self.scale.set_value(init_percent)
        self.scale.set_digits(0)
        self.scale.connect("value-changed", self.on_brightness_change)
        box.pack_start(self.scale, False, False, 0)

        custom_btn = Gtk.Button()
        custom_btn.connect("clicked", lambda b: self.enter_custom())
        self._tr(custom_btn.set_label, "custom")
        self._tr(custom_btn.set_tooltip_text, "custom_tip")
        box.pack_start(custom_btn, False, False, 0)

        pick_btn = Gtk.Button()
        pick_btn.connect("clicked", lambda b: self.pick_from_screen())
        self._tr(pick_btn.set_label, "screen_once")
        self._tr(pick_btn.set_tooltip_text, "screen_once_tip")
        box.pack_start(pick_btn, False, False, 0)

        self.mode_btns = []
        self.screen_btn = self._mode_button("screen_live", "screen", "screen_live_tip", "screen_live_warn")
        box.pack_start(self.screen_btn, False, False, 0)
        self.battery_btn = self._mode_button("battery", "battery", "battery_tip")
        box.pack_start(self.battery_btn, False, False, 0)

        # effects need a plain base color, so they are greyed out while battery/live-screen own the color
        self.effects_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.effects_label = Gtk.Label(xalign=0)
        self.effects_box.pack_start(self.effects_label, False, False, 0)
        grid = Gtk.Grid(column_homogeneous=True, row_spacing=3, column_spacing=3)
        for i, key in enumerate(kbd_led.EFFECTS):
            grid.attach(self._mode_button(f"fx.{key}", key, f"fx.{key}.tip"), i % 3, i // 3, 1, 1)
        self.effects_box.pack_start(grid, False, False, 0)

        self.effects_box.pack_start(self._label("speed"), False, False, 0)
        saved = kbd_led.read_effect()
        self.speed_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        self.speed_scale.set_digits(0)
        self.speed_scale.set_value(saved[1] if saved else 5)
        self.speed_scale.connect("value-changed", self.on_speed_change)
        self.effects_box.pack_start(self.speed_scale, False, False, 0)
        box.pack_start(self.effects_box, False, False, 0)

        for btn in (self.screen_btn, self.battery_btn):
            btn.connect("toggled", self._refresh_effects)
        self._refresh_effects()
        return box

    def _tr(self, setter, key):
        """Apply a translated text now, and again on every language change."""
        setter(t(key))
        self._i18n.append((setter, key))

    def _label(self, key):
        label = Gtk.Label(xalign=0)
        self._tr(label.set_text, key)
        return label

    def _build_settings_button(self):
        """Gear button: a drop-down menu with Language and Refresh rate submenus, and About."""
        btn = Gtk.MenuButton(relief=Gtk.ReliefStyle.NONE)
        gear = Gtk.Label()
        gear.set_markup('<span size="large">\u2699</span>')
        btn.add(gear)
        self._tr(btn.set_tooltip_text, "settings")

        menu = Gtk.Menu()
        lang = Gtk.MenuItem()
        self._tr(lang.set_label, "language")
        lang.set_submenu(self._radio_menu([(name, code) for code, name in kbd_i18n.LANGS],
                                          kbd_i18n.current, self.on_lang_selected))
        menu.append(lang)

        rate = Gtk.MenuItem()
        self._tr(rate.set_label, "menu_rate")
        self._tr(rate.set_tooltip_text, "menu_rate_tip")
        rate.set_submenu(self._radio_menu([(f"{n} Hz", n) for n in kbd_led.SCREEN_FPS_CHOICES],
                                          kbd_led.screen_fps(), kbd_led.set_screen_fps))
        menu.append(rate)

        menu.append(Gtk.SeparatorMenuItem())
        about = Gtk.MenuItem()
        self._tr(about.set_label, "about")
        about.connect("activate", lambda _i: self.show_about())
        menu.append(about)
        menu.show_all()
        btn.set_popup(menu)
        return btn

    @staticmethod
    def _radio_menu(entries, current, on_select):
        """Submenu of radio items; `entries` is [(label, value)], on_select(value) runs on change."""
        menu, group = Gtk.Menu(), None
        for label, value in entries:
            item = Gtk.RadioMenuItem.new_with_label_from_widget(group, label)
            group = group or item
            item.set_active(value == current)
            item.connect("toggled", lambda i, v=value: i.get_active() and on_select(v))
            menu.append(item)
        return menu

    def on_lang_selected(self, code):
        if code != kbd_i18n.current:
            kbd_i18n.set_lang(code)
            for setter, key in self._i18n:
                setter(t(key))
            self._populate_flow()  # swatch names
            self._refresh_effects()

    def show_about(self):
        dlg = Gtk.AboutDialog(transient_for=self, modal=True)
        dlg.set_program_name("Backlit")
        dlg.set_version(kbd_led.VERSION)
        dlg.set_comments(t("about_comments"))
        dlg.set_logo_icon_name("input-keyboard")
        dlg.set_authors(["efwaz"])
        dlg.set_copyright("Copyright © 2026 efwaz")
        dlg.set_license_type(Gtk.License.MIT_X11)
        dlg.add_credit_section(t("about_uses"), ["Claude Code", "GTK 3 / PyGObject", "grim", "slurp", "tuxedo-drivers"])
        dlg.add_credit_section(t("about_inspired"), ["OpenRGB", "TUXEDO Control Center"])
        dlg.run()
        dlg.destroy()

    def _populate_flow(self):
        for child in list(self.flow.get_children()):
            self.flow.remove(child)
            child.destroy()
        for name, rgb, percent in kbd_led.STANDARD_COLORS:
            self.flow.add(self._make_swatch(t("color." + name), rgb, percent, favorite=False))
        for name, rgb, percent, raw in load_favorites(self.max_brightness):
            self.flow.add(self._make_swatch(name, rgb, percent, favorite=True, raw_line=raw))
        self.flow.show_all()

    def _make_swatch(self, name, rgb, percent, favorite, raw_line=None):
        r, g, b = rgb
        btn = Gtk.Button()
        btn.set_tooltip_text(("★ " if favorite else "") + f"{name}  #{r:02X}{g:02X}{b:02X}")
        border = "2px dashed #d4af37" if favorite else "2px solid black"
        css = Gtk.CssProvider()
        css.load_from_data(
            f"button {{ background: rgb({r},{g},{b}); "
            f"min-width: 22px; min-height: 22px; padding: 0; "
            f"border: {border}; }}".encode()
        )
        btn.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        btn.connect("clicked", lambda b: self.apply_swatch(rgb, percent))
        if favorite:
            btn._raw_line = raw_line
            btn.connect("button-press-event", self._on_favorite_press, raw_line)
        return btn

    def _on_favorite_press(self, widget, event, raw_line):
        if event.button != 3:
            return False
        menu = Gtk.Menu()
        for label, action in ((t("rename"), self.rename_favorite), (t("delete"), self.remove_favorite)):
            item = Gtk.MenuItem(label=label)
            item.connect("activate", lambda _i, action=action: action(raw_line))
            menu.append(item)
        menu.show_all()
        menu.popup_at_pointer(event)
        return True

    def rename_favorite(self, raw_line):
        name, rest = raw_line.split("|", 1)
        dlg = Gtk.Dialog(title=t("rename_title"), transient_for=self, modal=True)
        dlg.add_buttons(t("cancel"), Gtk.ResponseType.CANCEL, t("accept"), Gtk.ResponseType.OK)
        dlg.set_default_response(Gtk.ResponseType.OK)
        entry = Gtk.Entry(text=name, activates_default=True)
        dlg.get_content_area().add(entry)
        dlg.get_content_area().show_all()
        if dlg.run() == Gtk.ResponseType.OK:
            new = entry.get_text().strip().replace("|", "/")  # "|" is the file's field separator
            if new:
                with open(kbd_led.FAVORITES_FILE) as f:
                    lines = [f"{new}|{rest}\n" if l.strip() == raw_line else l for l in f]
                with open(kbd_led.FAVORITES_FILE, "w") as f:
                    f.writelines(lines)
                self._populate_flow()
        dlg.destroy()

    def remove_favorite(self, raw_line):
        if os.path.exists(kbd_led.FAVORITES_FILE):
            with open(kbd_led.FAVORITES_FILE) as f:
                lines = [l for l in f if l.strip() != raw_line]
            with open(kbd_led.FAVORITES_FILE, "w") as f:
                f.writelines(lines)
        child = self._find_flow_child(raw_line)
        if child:
            self.flow.remove(child)
            child.destroy()

    def _find_flow_child(self, raw_line):
        for child in self.flow.get_children():
            btn = child.get_child()
            if getattr(btn, "_raw_line", None) == raw_line:
                return child
        return None

    # ---------- background modes (battery / live screen) ----------

    def _mode_button(self, label_key, mode, tip_key, warn_key=None):
        """Toggle button for a background mode: "screen", "battery" or an effect key.
        With warn_key, a warning icon sits at the right edge of the button, with its own tooltip."""
        btn = Gtk.ToggleButton()
        btn.mode = mode
        if warn_key:
            content = Gtk.Box(spacing=6)
            text = Gtk.Label()
            self._tr(text.set_text, label_key)
            content.pack_start(text, True, True, 0)
            icon = Gtk.Label()
            icon.set_markup('<span foreground="#e0a800">\u26a0</span>')
            self._tr(icon.set_tooltip_text, warn_key)
            content.pack_end(icon, False, False, 0)
            btn.add(content)
        else:
            self._tr(btn.set_label, label_key)
        self._tr(btn.set_tooltip_text, tip_key)
        cfg = kbd_led.read_effect()
        if mode in ("screen", "battery"):
            btn.set_active(kbd_led.mode_running(mode))
        else:
            btn.set_active(bool(cfg) and cfg[0] == mode and kbd_led.mode_running("effect"))
        btn.connect("toggled", self.on_mode_toggled)
        self.mode_btns.append(btn)
        return btn

    def _refresh_effects(self, *_args):
        blocked = self.screen_btn.get_active() or self.battery_btn.get_active()
        self.effects_box.set_sensitive(not blocked)
        self.effects_label.set_text(t("effects_off" if blocked else "effects"))

    def stop_modes(self, keep=None):
        """Stop every background mode and untoggle its button (except `keep`)."""
        kbd_led.stop_modes()
        for btn in self.mode_btns:
            if btn is not keep and btn.get_active():
                btn.handler_block_by_func(self.on_mode_toggled)
                btn.set_active(False)
                btn.handler_unblock_by_func(self.on_mode_toggled)

    def _ensure_lit(self):
        if not self.scale.get_value():  # modes keep the slider level; off would stay off
            self.scale.set_value(100)

    def on_mode_toggled(self, btn):
        if not btn.get_active():
            self.stop_modes()
            if btn.mode not in ("screen", "battery"):  # effects: go back to the plain color
                self.apply_swatch(self.current_rgb, None)
            return
        self.stop_modes(keep=btn)
        if btn.mode == "battery":
            self._ensure_lit()
            kbd_led.start_battery()
        elif btn.mode == "screen":
            geo = self._select_region()
            if not geo:
                btn.set_active(False)
                return
            self._ensure_lit()
            kbd_led.start_screen(geo)
        else:
            self._ensure_lit()
            level = round(self.max_brightness * self.scale.get_value() / 100)
            kbd_led.start_effect(btn.mode, round(self.speed_scale.get_value()), self.current_rgb, level)

    def on_speed_change(self, scale):
        cfg = kbd_led.read_effect()
        if cfg:  # a running effect picks the new speed up within 0.5s
            kbd_led.write_effect(cfg[0], round(scale.get_value()), cfg[2], cfg[3])

    def _select_region(self):
        """Hide the panel, let the user pick a screen region; None if cancelled or slurp is missing."""
        self.hide()
        while Gtk.events_pending():
            Gtk.main_iteration()
        try:
            return kbd_screen.select_region()
        except FileNotFoundError as e:
            self.show()
            self._error(t("err_tools"), str(e))
        finally:
            self.show()

    def _error(self, title, detail):
        dlg = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.CLOSE, text=title)
        dlg.format_secondary_text(detail)
        dlg.run()
        dlg.destroy()

    def apply_swatch(self, rgb, percent):
        self.stop_modes()
        self.current_rgb = rgb
        if percent is None:  # keep slider level; if it was off, turn on at 100
            percent = round(self.scale.get_value()) or 100
        self.scale.set_value(percent)
        self.on_brightness_change(self.scale)

    def pick_from_screen(self):
        """One-shot: dominant color of a screen region, then keep it fixed."""
        geo = self._select_region()
        if not geo:
            return
        try:
            ppm = kbd_screen.capture(geo)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            self._error(t("err_capture"), str(e))
            return
        self.apply_swatch(kbd_screen.dominant_color(ppm), None)

    def on_brightness_change(self, _scale):
        percent = round(self.scale.get_value())
        brightness = round(self.max_brightness * percent / 100)
        r, g, b = kbd_led.current()[:3] if kbd_led.mode_running() else self.current_rgb
        kbd_led.write_led(r, g, b, brightness)

    # ---------- custom (wheel) view ----------

    def _build_custom_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(6)

        self.wheel = ColorWheel()
        self.wheel.on_change = self.on_custom_change
        self.wheel.set_halign(Gtk.Align.CENTER)
        self.wheel.set_valign(Gtk.Align.CENTER)
        box.pack_start(self.wheel, True, True, 0)

        hex_box = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
        hex_box.pack_start(Gtk.Label(label="Hex"), False, False, 0)
        self.hex_entry = Gtk.Entry(max_length=7, width_chars=8, placeholder_text="#RRGGBB")
        self.hex_entry.connect("changed", self.on_hex_changed)
        self.hex_entry.connect("activate", lambda e: self._sync_hex())
        hex_box.pack_start(self.hex_entry, False, False, 0)
        box.pack_start(hex_box, False, False, 0)

        box.pack_start(self._label("brightness"), False, False, 0)
        self.custom_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.custom_scale.set_digits(0)
        self.custom_scale.connect("value-changed", self.on_custom_change)
        box.pack_start(self.custom_scale, False, False, 0)

        btn_box = Gtk.Box(spacing=10)
        save = Gtk.Button()
        self._tr(save.set_label, "save")
        save.connect("clicked", lambda b: self.on_save_favorite())
        btn_box.pack_start(save, False, False, 0)

        spacer = Gtk.Box()
        btn_box.pack_start(spacer, True, True, 0)

        cancel = Gtk.Button()
        self._tr(cancel.set_label, "cancel")
        cancel.connect("clicked", lambda b: self.exit_custom(restore=True))
        accept = Gtk.Button()
        self._tr(accept.set_label, "accept")
        accept.connect("clicked", lambda b: self.exit_custom(restore=False))
        btn_box.pack_start(cancel, False, False, 0)
        btn_box.pack_start(accept, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        return box

    def enter_custom(self):
        r, g, b, brightness = kbd_led.current()
        self._custom_orig = (r, g, b, brightness)
        percent = round(brightness * 100 / self.max_brightness) if self.max_brightness else 0

        self.wheel.set_rgb(r, g, b)
        self._sync_hex()

        self.custom_scale.handler_block_by_func(self.on_custom_change)
        self.custom_scale.set_value(percent)
        self.custom_scale.handler_unblock_by_func(self.on_custom_change)

        self.stack.set_visible_child_name("custom")

    def on_custom_change(self, *_args):
        self._apply_custom()
        self._sync_hex()

    def _apply_custom(self):
        self.stop_modes()
        r, g, b = self.wheel.get_rgb()
        percent = round(self.custom_scale.get_value())
        brightness = round(self.max_brightness * percent / 100)
        kbd_led.write_led(r, g, b, brightness)

    def _sync_hex(self):
        """Show the wheel's color in the hex entry (the wheel is always full value, so this normalizes)."""
        r, g, b = self.wheel.get_rgb()
        self.hex_entry.handler_block_by_func(self.on_hex_changed)
        self.hex_entry.set_text(f"#{r:02X}{g:02X}{b:02X}")
        self.hex_entry.handler_unblock_by_func(self.on_hex_changed)

    def on_hex_changed(self, entry):
        m = re.fullmatch(r"#?([0-9a-fA-F]{6})", entry.get_text().strip())
        if m:
            self.wheel.set_rgb(*(int(m[1][i:i + 2], 16) for i in (0, 2, 4)))
            self._apply_custom()

    def exit_custom(self, restore):
        if restore:
            r, g, b, brightness = self._custom_orig
            kbd_led.write_led(r, g, b, brightness)
        else:
            r, g, b, brightness = kbd_led.current()

        self.current_rgb = (r, g, b)
        percent = round(brightness * 100 / self.max_brightness) if self.max_brightness else 0
        self.scale.handler_block_by_func(self.on_brightness_change)
        self.scale.set_value(percent)
        self.scale.handler_unblock_by_func(self.on_brightness_change)

        self.stack.set_visible_child_name("grid")
        self.resize(*GRID_SIZE)

    def on_save_favorite(self):
        r, g, b = self.wheel.get_rgb()
        percent = round(self.custom_scale.get_value())
        brightness = round(self.max_brightness * percent / 100)
        name = f"{r},{g},{b}"
        with open(kbd_led.FAVORITES_FILE, "a") as f:
            f.write(f"{name}|{r} {g} {b}|{brightness}\n")
        self._populate_flow()


win = Panel()
win.show_all()
Gtk.main()
