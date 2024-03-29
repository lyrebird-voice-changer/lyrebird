# shutil.which supported from Python 3.3+
from shutil import which
from json import loads
import subprocess


class Launch:
    # Check if a shell command is available on the system.
    @staticmethod
    def check_shell_tool(name):
        return which(name) is not None

    @staticmethod
    def check_py_gtk():
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, Gdk, GdkPixbuf
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_py_toml():
        try:
            import toml
            return True
        except ModuleNotFoundError:
            return False

    @staticmethod
    def check_sox():
        return Launch.check_shell_tool("sox")

    @staticmethod
    def check_sox_pulse():
        sox_help = subprocess.run(["sox", "--help"], capture_output=True, encoding="utf8")
        stdout = sox_help.stdout
        sox_drivers_prefix = "AUDIO DEVICE DRIVERS: "
        for line in stdout.split("\n"):
            if line.startswith(sox_drivers_prefix):
                drivers = line[len(sox_drivers_prefix):].split(" ")
                return "pulseaudio" in drivers
        return False

    @staticmethod
    def check_pactl():
        return Launch.check_shell_tool("pactl")

    @staticmethod
    def determine_audio_server():
        pactl_info = subprocess.run(["pactl", "--format=json", "info"], capture_output=True, encoding="utf8")
        server_info = loads(pactl_info.stdout)
        if "server_name" in server_info:
            return server_info["server_name"]
        return None
