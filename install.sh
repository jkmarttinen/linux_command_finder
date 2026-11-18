#!/usr/bin/env bash
# Asentaa Linux Command Finderin käyttäjälle: sovellusvalikon kuvake + (XFCE:ssä) pikanäppäin Super+K.
# Installs a menu launcher and (on XFCE) the Super+K shortcut. No sudo needed.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$DIR/komentoapuri.py"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

if ! python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk' 2>/dev/null; then
  echo "Puuttuu GTK3 Python-sidonnat / GTK3 Python bindings missing. Asenna / install:"
  echo "  sudo apt install python3-gi gir1.2-gtk-3.0"
  exit 1
fi

chmod +x "$APP"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/komentoapuri.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Linux Command Finder
Name[fi]=Komentoapuri
Comment=Searchable Linux commands and package search
Comment[fi]=Linux-komennot ja pakettihaku hakutoiminnolla
Exec=python3 $APP
Icon=utilities-terminal
Terminal=false
Categories=Utility;System;
DESKTOP
echo "Käynnistin asennettu / Launcher installed: $DESKTOP_DIR/komentoapuri.desktop"

if command -v xfconf-query >/dev/null 2>&1; then
  xfconf-query -c xfce4-keyboard-shortcuts -n -t string \
    -p "/commands/custom/<Super>k" -s "python3 $APP"
  echo "Pikanäppäin Super+K asetettu / Shortcut Super+K set (XFCE)."
else
  echo "Ei XFCE:tä: aseta pikanäppäin itse komennolle / Not on XFCE: bind a shortcut to:  python3 $APP"
fi
