# Lyrebird
Simple and powerful voice changer for Linux, written in GTK 3.

# Why?
I decided to write this as a tool for myself, partly for fun and partly
because I hate my own voice and since there was no decent Linux voice changers. The UI
is based *very* loosely off of Clownfish for Windows, and is very simple and easy to use.

# Features
- Built in effects for accurate male and female voices
- Ability to create and load custom presets
- Manual pitch scale for finer adjustment
- Creates its own temporary virtual input device
- A clean and easy to use GUI

# Usage
1. Make sure you satisfy all requirements listed below (e.g. PulseAudio, sox)
2. Run `install.sh` to install dependencies and Lyrebird itself
3. Launch Lyrebird from your preferred application launcher (e.g. GNOME, Rofi)
4. Select a preset or set a custom pitch and flip the switch
5. Change the input device for the application to **Lyrebird Virtual Input**, this can be done in-app or using `pavucontrol` if you're not given the option
6. Ignore any applications that ask if you want to use "Lyrebird Output" (e.g. Discord), this is used internally and isn't necessary to use Lyrebird

## Changing using `pavucontrol`
If an app doesn't support live input changing then it can be done with `pavucontrol`. Head to the "Recording" tab and change the input using the drop down next to the application name.

### I can't?
For some apps on some distros (like Ubuntu) changing the input won't work. To fix this you need to create a file at `~/.alsoftrc` and add the following contents:

```
drivers = alsa,pulse,core,oss

[pulse]
allow-moves=yes
```

# Editing Presets
To edit the presets and add your own presets edit the file `~/.config/lyrebird/presets.toml`. This file is in the TOML format,
and the syntax is described below.

```toml
# name = Preset name, will be displayed in the GUI
# pitch_value = The pitch value of the preset, if you want to be able to adjust this use "scale"
# downsample_amount = The amount of downsampling to do, set as "none" if you don't want any
# override_pitch_slider = Whether the preset overrides the pitch slider or not

# Example preset, the [[presets]] is required for each preset
[[presets]]
name = "Woman"
pitch_value = "2.5"
downsample_amount = "none"
override_pitch_slider = true
```

# Requirements
- python-gobject
- pavucontrol
- sox
- PulseAudio