# Lyrebird

Simple and powerful voice changer for Linux, written in GTK 3.

[Discord](https://discord.gg/mvCSwYVe5t) | [#lyrebird](https://webchat.freenode.net/#lyrebird) (Freenode IRC)

![Lyrebird Screenshot](https://raw.githubusercontent.com/chxrlt/lyrebird/master/preview.png)

# Why?

I decided to write this as a tool for myself, partly for fun and partly because I hate my own voice and since there was no decent Linux voice changers. The UI is based *very* loosely off of Clownfish for Windows, and is very simple and easy to use.

# Features

- Built in effects for accurate male and female voices
- Ability to create and load custom presets
- Manual pitch scale for finer adjustment
- Creates its own temporary virtual input device
- A clean and easy to use GUI

# Install

## Distro Packages

Check the [releases page](https://github.com/chxrlt/lyrebird/releases) to find a package for your distro.

- [x] Ubuntu/Debian (download `.deb` from [releases page](https://github.com/chxrlt/lyrebird/releases))
- [x] Arch (AUR package `lyrebird`)

### Community

These packages are provided by the community and are not maintained by Lyrebird developers.

- [x] Gentoo (ebuild in the [edgets overlay](https://github.com/BlueManCZ/edgets/tree/master/media-sound/lyrebird))

## Manually

If a package for your distro isn't provided above then you can use the provided installer script:

1. Download the latest `tar.gz` from the [releases page](https://github.com/chxrlt/lyrebird/releases) and extract it
2. Make sure you satisfy all requirements listed below (e.g. Python 3.7, using PulseAudio, sox)
3. Run `install.sh` to install dependencies and Lyrebird itself
4. Launch Lyrebird from your preferred application launcher (e.g. GNOME, Rofi)

# Usage

1. Select a preset or set a custom pitch and flip the switch
2. Change the input device for the application to **Lyrebird Virtual Input**, this can be done in-app or using `pavucontrol` if you're not given the option
3. Ignore any applications that ask if you want to use "Lyrebird Output" (e.g. Discord), this is used internally and isn't necessary to use Lyrebird

## Changing using `pavucontrol`

If an app doesn't support live input changing then it can be done with `pavucontrol`. Head to the "Recording" tab and change the input using the drop down next to the application name.

### I can't?

For some apps on some distros (like Ubuntu) changing the input won't work. To fix this you need to create a file at `~/.alsoftrc` and add the following contents:

```ini
drivers = alsa,pulse,core,oss

[pulse]
allow-moves=yes
```

## Common Issues

### `ModuleNotFoundError: No module named 'lyrebird.mainwindow'`

Firstly make sure you've ran the most up-to-date `install.sh` script. If the issue still persists then this is probably a permissions issue, running `sudo chmod -R 755 /usr/local/share/lyrebird /etc/lyrebird` should fix this.

If the issue still sticks around then please open a GitHub issue and include the output of `id -u; which lyrebird; sudo ls -lAn /usr/local/share/lyrebird; sudo ls -lAn ~/.local/share/lyrebird`.

# Editing Presets

Presets and config is initally stored in `/etc/lyrebird/` however it can be overriden by copying the files to `~/.config/lyrebird/`.

To edit and add your own presets edit the file `presets.toml`, this file is in the TOML format and the syntax is described below.

```toml
# name = Preset name, will be displayed in the GUI
# pitch_value = The pitch value of the preset, if you want to be able to adjust this use "scale"
# downsample_amount = The amount of downsampling to do, set as "none" if you don't want any
# override_pitch_slider = Whether the preset overrides the pitch slider or not
# volume_boost = The amount of decibels to boost by

# Example preset, the [[presets]] is required for each preset
[[presets]]
name = "Woman"
pitch_value = "2.5"
downsample_amount = "none"
override_pitch_slider = true

# Boost by 2 dB to make the voice louder
volume_boost = "2"
```

# Requirements

- Python 3.7+
    - toml
    - python-gobject (check [issue #13](https://github.com/chxrlt/lyrebird/issues/13) if having issues)
- pavucontrol
- SoX
    - libsox-fmt-pulse (some distros may already bundle with SoX)
- PulseAudio
