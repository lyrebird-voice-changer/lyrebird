#!/usr/bin/env python3

import sys
import platform

print("[info] Starting Lyrebird v1.2.0")

major = sys.version_info[0]
minor = sys.version_info[1]

# Check for Python 3.7+
if major < 3 and minor < 7:
    print("[error] Python 3.7 or higher is required to run Lyrebird")
    input("Press return to exit...")
    sys.exit(1)

platform_sys = platform.system()
# Keeping it open to other NIXes!
if platform_sys == "Windows" or platform_sys == "Darwin":
    print("[error] Linux is required to used Lyrebird")
    input("Press return to exit...")
    sys.exit(1)

from app.core.launch import Launch

# Check for Python gobject installation
if not Launch.check_py_gtk():
    msg = '''[error] Python GTK is missing from your system.

  * On Debian, Ubuntu, pop_OS, or Mint, try running: sudo apt install python3-gi
  * On Arch, try running: sudo pacman -S python-gobject
  * On all other distros, this package may have a different name, try searching for "python3 gtk installation instructions".

Additional help can be found in the Lyrebird repo: https://github.com/lyrebird-voice-changer/lyrebird/issues
'''
    print(msg)
    input("Press return to exit...")
    sys.exit(1)

# Import GTK
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if __name__ != '__main__':
    sys.exit(0)

from app.ui.alert import Alert

# Check for pactl
if not Launch.check_pactl():
    console_msg = '''[error] PulseAudio utilities are missing from your system.

  * On Ubuntu, Debian, pop_OS, or Mint, try running: sudo apt install pulseaudio-utilities
  * On Arch, this comes with the package "pipewire-pulse", please refer to the Arch Wiki page (below).
  * On all other distros, this package may have a different name, try searching for "pactl" or "pulseaudio utilities".
  
If after installing PulseAudio utilities and you still see this error, or your distro does not contain an equivalent package, your audio server may be configured in a way that is incompatible with Lyrebird. The "pactl" command is required for Lyrebird.

Additional help can be found in the Lyrebird repo: https://github.com/lyrebird-voice-changer/lyrebird/issues
Arch Wiki PipeWire page: https://wiki.archlinux.org/title/PipeWire (for Arch users)'''
    print(console_msg)

    msg = '''<b>Error:</b> PulseAudio utilities are missing from your system.

On Ubuntu, Debian, pop_OS, or Mint, try running:
    <i>sudo apt install pulseaudio-utilities</i>

On Arch, this comes with the package <i>pipewire-pulse</i>, please refer to the <a href="https://wiki.archlinux.org/title/PipeWire">Arch Wiki page</a>.

On all other distros, this package may have a different name, try searching for "pactl" or "pulseaudio utilities".
  
If after installing PulseAudio utilities and you still see this error, or your distro does not contain an equivalent package, your audio server may be configured in a way that is incompatible with Lyrebird. The "pactl" command is required for Lyrebird.

Additional help can be found in the <a href="https://github.com/lyrebird-voice-changer/lyrebird/issues">Lyrebird repo</a>.'''

    alert = Alert(None)
    alert.show_error_markup("Lyrebird Error: PulseAudio utilities are missing", msg)
    sys.exit(1)

# Check for TOML
if not Launch.check_py_toml():
    console_msg = '''[error] Python module "toml" is missing from your system.

  * On Ubuntu, Debian, pop_OS, or Mint, try running: sudo apt install python3-toml
  * On Arch, try running: sudo pacman -S python-toml
  * For all other distros, try running: pip3 install toml

Additional help can be found in the Lyrebird repo: https://github.com/lyrebird-voice-changer/lyrebird/issues'''
    print(console_msg)

    msg = '''<b>Error:</b> Python module "toml" is missing from your system.

On Ubuntu, Debian, pop_OS, or Mint, try running:
    <i>sudo apt install python3-toml</i>

If you're using Arch, try running:
    <i>sudo pacman -S python-toml</i>

For all other distros, try running:
    <i>pip3 install toml</i>
    
Additional help can be found in the <a href="https://github.com/lyrebird-voice-changer/lyrebird/issues">Lyrebird repo</a>.'''

    alert = Alert(None)
    alert.show_error_markup("Lyrebird Error: Python TOML is Missing", msg)
    sys.exit(1)

# Check for SoX
if not Launch.check_sox():
    console_msg = '''[error] Shell command "sox" is missing from your system.

  * On Ubuntu, Debian, pop_OS, or Mint, try running: sudo apt install sox libsox-fmt-pulse
  * On Arch, try running: sudo pacman -S sox
  * For all other distros, try searching for the package "sox".

Additional help can be found in the Lyrebird repo: https://github.com/lyrebird-voice-changer/lyrebird/issues'''
    print(console_msg)

    msg = '''<b>Error:</b> Shell command "sox" is missing from your system.

On Ubuntu, Debian, pop_OS, or Mint, try running:
    <i>sudo apt install sox libsox-fmt-pulse</i>

If you're using Arch, try running:
    <i>sudo pacman -S sox</i>

For all other distros, try searching for the package "sox".

Additional help can be found in the <a href="https://github.com/lyrebird-voice-changer/lyrebird/issues">Lyrebird repo</a>.'''

    alert = Alert(None)
    alert.show_error_markup("Lyrebird Error: sox is missing", msg)
    sys.exit(1)

if not Launch.check_sox_pulse():
    console_msg = '''[error] SoX is missing the PulseAudio audio driver.

  * On Ubuntu, Debian, pop_OS, or Mint, try running: sudo apt install libsox-fmt-pulse
  * For all other distros, try searching for the the installation of "sox pulseaudio audio driver".

Additional help can be found in the Lyrebird repo: https://github.com/lyrebird-voice-changer/lyrebird/issues'''
    print(console_msg)

    msg = '''<b>Error:</b> SoX is missing the PulseAudio audio driver.

On Ubuntu, Debian, pop_OS, or Mint, try running:
    <i>sudo apt install libsox-fmt-pulse</i>

For all other distros, try searching for the the installation of "sox pulseaudio audio driver".

Additional help can be found in the <a href="https://github.com/lyrebird-voice-changer/lyrebird/issues">Lyrebird repo</a>.'''

    alert = Alert(None)
    alert.show_error_markup("Lyrebird Error: SoX PulseAudio audio driver missing", msg)
    sys.exit(1)

audio_server = Launch.determine_audio_server()
print(f"[info] Audio server: {audio_server}")

from app.ui.mainwindow import MainWindow

# Start main window and launch Lyrebird
win = MainWindow()
win.connect('destroy', win.close)
win.show_all()

try:
    Gtk.main()
except BaseException as e:
    print(e)
    msg = f'''<b>Fatal Lyrebird Error:</b> {str(e)}

Please report to the <a href="https://github.com/lyrebird-voice-changer/lyrebird/issues">Lyrebird repo</a>.'''
    alert = Alert(None)
    alert.show_error_markup("Fatal Lyrebird Error", msg)
    win.close()
