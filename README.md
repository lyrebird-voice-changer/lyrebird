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
- A clean and easy to use GUI

# Usage
1. Open Lyrebird by running `python src/app.py` (a .desktop file will be made later)
2. Make sure that the toggle switch is enabled on, this will create a new Null Output
3. Select a preset from the UI, or select "Custom" to use a custom pitch of your own. Presets
   can be edited and added in `presets.toml`, see this file for the syntax for defining your own.
4. Since Lyrebird uses `sox` behind the scenes, it outputs all of the effects to a special PulseAudio Null Output
   sink. Change the input device of the application to record from "Null Output" in `pavucontrol` for
   the applications you wish to change your voice in.

# Editing Presets
To edit the presets and add your own presets edit the file `presets.toml`. This file is in the TOML format,
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