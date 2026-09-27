#!/bin/bash
# Copy the scripts to ~/.config/scripts and (re)load the systemd user service.
# Run again after every change. Favorites/state files there are left untouched.
set -e
cd "$(dirname "$(readlink -f "$0")")"

DEST="$HOME/.config/scripts"
mkdir -p "$DEST" "$HOME/.config/systemd/user"
cp kbd-backlight-menu.sh kbd-panel.py kbd-battery.py kbd-effects.py kbd-ctl.py kbd_led.py kbd_screen.py kbd_i18n.py kbd-restore.sh "$DEST/"
chmod +x "$DEST"/kbd-backlight-menu.sh "$DEST"/kbd-panel.py "$DEST"/kbd-battery.py "$DEST"/kbd-effects.py "$DEST"/kbd-ctl.py "$DEST"/kbd_screen.py "$DEST"/kbd_i18n.py "$DEST"/kbd-restore.sh
cp kbd-backlight-restore.service "$HOME/.config/systemd/user/"
# launcher for a global shortcut (.desktop files need an absolute path, so fill in $HOME)
mkdir -p "$HOME/.local/share/applications"
sed "s|@HOME@|$HOME|" net.local.kbd-backlight-menu.sh.desktop > "$HOME/.local/share/applications/net.local.kbd-backlight-menu.sh.desktop"
systemctl --user daemon-reload
systemctl --user enable kbd-backlight-restore.service
echo "Instalado en $DEST"
