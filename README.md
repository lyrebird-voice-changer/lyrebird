# Lyrebird

Simple and powerful voice changer for Linux, written with Python & GTK.

![Lyrebird Screenshot](https://raw.githubusercontent.com/lyrebird-voice-changer/lyrebird/master/preview.png)

## Features

- Built in effects for accurate male and female voices.
- Ability to create and load custom presets.
- Manual pitch scale for finer adjustment.
- Creates its own temporary virtual input device.
- A clean and easy to use GUI.

## Limitations

- The voice changer operates with a few seconds of delay.

## Install

Once installed, Lyrebird can be launched from your launcher (GNOME, Xfce, Rofi) or by running `lyrebird` in the command line.

### Ubuntu / Debian / Mint / Pop!_OS

```sh
wget "https://github.com/lyrebird-voice-changer/lyrebird/releases/download/v1.2.0/lyrebird_1.2.0-1.deb" && sudo apt install ./lyrebird_1.2.0-1.deb
```

You can find more [releases here](https://github.com/lyrebird-voice-changer/lyrebird/releases).

### Arch Linux

Use an AUR package manager?

```sh
yay -S lyrebird
```

Otherwise:

```sh
wget "https://github.com/lyrebird-voice-changer/lyrebird/releases/download/v1.2.0/lyrebird-1.2.0-1-any-archlinux.pkg.tar.zst" && sudo pacman -U lyrebird-1.2.0-1-any-archlinux.pkg.tar.zst
```

You can find more [releases here](https://github.com/lyrebird-voice-changer/lyrebird/releases).

### Manually

If a package for your distro isn't provided above then you can install the requirements below and use the provided installer script:

```sh
wget "https://github.com/lyrebird-voice-changer/lyrebird/releases/download/v1.2.0/lyrebird_1.2.0-1.tar.gz" && tar xf lyrebird_1.2.0-1.tar.gz && cd lyrebird_1.2.0-1 && sudo ./install.sh
```

### Community Packages

These packages are provided by the community and are not maintained by Lyrebird developers.

- [x] Gentoo (ebuild in the [edgets overlay](https://github.com/BlueManCZ/edgets/tree/master/media-sound/lyrebird))

## Requirements

Installing via package manager will automatically install these packages, only concern yourself with these if you are using the install script.

- **Python 3.7+** - Ubuntu/Debian `python3` / Arch `python3`
    - **toml** - Ubuntu/Debian `python3-toml` / Arch `python-toml`
    - **python-gobject** - Ubuntu/Debian `python3-gi` / Arch `python-gobject`
- **pavucontrol** - Ubuntu/Debian `pavucontrol` / Arch `pavucontrol`
- **SoX** - Ubuntu/Debian `sox libsox-fmt-pulse` / Arch `sox`
- **PipeWire**
- **PulseAudio utilities** (compatible with PipeWire) - Ubuntu/Debian `pipewire-pulse pulseaudio-utils` / Arch `pipewire-pulse`

One-liners to install requirements:

  * Ubuntu/Debian - `sudo apt install python3 python3-toml python3-gi pavucontrol sox libsox-fmt-pulse pulseaudio-utils`
  * Arch - `sudo pacman -S python3 python-toml python-gobject pavucontrol sox`

*(If you wish to see your distro here please submit an issue/pull request for this section.)*

## Lyrebird Usage

1. Select a preset or set a custom pitch and flip the switch
2. Change the input device for the application to **Lyrebird Virtual Input**, this can be done in-app or using `pavucontrol` if you're not given the option
3. Ignore any applications that ask if you want to use "Lyrebird Output" (e.g. Discord), this is used internally and isn't necessary to use Lyrebird

### Changing using `pavucontrol`

If an app doesn't support live input changing then it can be done with `pavucontrol`. Head to the "Recording" tab and change the input using the drop down next to the application name.

#### I can't?

For some apps on some distros (like Ubuntu) changing the input won't work. To fix this you need to create a file at `~/.alsoftrc` and add the following contents:

```ini
drivers = alsa,pulse,core,oss

[pulse]
allow-moves=yes
```

### Common Issues

#### `ModuleNotFoundError: No module named 'lyrebird.mainwindow'`

Firstly make sure you've ran the most up-to-date `install.sh` script. If the issue still persists then this is probably a permissions issue, running `sudo chmod -R 755 /usr/local/share/lyrebird /etc/lyrebird` should fix this.

If the issue still sticks around then please open a GitHub issue and include the output of `id -u; which lyrebird; sudo ls -lAn /usr/local/share/lyrebird; sudo ls -lAn ~/.local/share/lyrebird`.

## Editing Presets

Custom presets are stored in `~/.config/lyrebird/presets.toml`. To edit and add your own presets edit the file `presets.toml`, this file is in the TOML format and the syntax is described below.

```toml
# Effect presets are defined in presets.toml
# The following parameters are available for presets

# name: Preset name, will be displayed in the GUI
# pitch_value: The pitch value of the preset, float value between -10.0 to 10.0. Omit if pitch value should not be affected from slider value.
# downsample_amount Downsample by an integer factor.
# volume_boost: Amount in dB to boost the audio. Can be negative to make the audio quieter.

# e.g.
# [[presets]]
# name = "Bad Mic"
# pitch_scale = -1.5
# downsample_amount = 8
# volume_boost = 8
```

## Packaging

  * Packaging for Debian is handled in a [separate repo](https://github.com/lyrebird-voice-changer/lyrebird-deb).
  * Packaging for Arch (AUR) is handled in a [separate repo](https://github.com/lyrebird-voice-changer/lyrebird-arch).

## Developers

Lyrebird was created by [megabytesofrem](https://github.com/megabytesofrem) in 2020, and is now maintained by [Harry Stanton](https://github.com/harrego).
