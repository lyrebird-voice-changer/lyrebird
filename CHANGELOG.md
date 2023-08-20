# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2.0] - 2023/08/20

### Added

- **PipeWire is officially supported!**
  - Utilizes `pactl`.
  - On Ubuntu / Debian / Mint / Pop!_OS you'll need `pulseaudio-utils` and `pipewire-pulse` (`.deb` will auto install).
  - On most other distros `pipewire-pulse` provides `pactl` (check your distro documentation before installing).
- The active preset is now clearly selected in the UI.
- Lyrebird dependencies (Python modules and shell commands) are now checked at application launch resulting in a warning alert when something is missing instead of a crash later down the line.

### Changed

- Custom presets have been overhauled:
  - Default presets now live in Lyrebird instead of `presets.toml` meaning that they can be more easily kept up to date.
  - Launching Lyrebird v1.2.0 will now automatically migrate your `presets.toml` by removing all the old defaults while retaining your custom presets. A backup (`presets.toml.old`) is made in the unlikely case of any presets being lost during the migration.
  - Preset options have been changed while remaining fully backwards compatible:
    - `pitch_value`, `downsample_amount`, and `volume_boost` can now be omitted instead of providing `none` or `scale`.
    - `override_pitch_scale` is now deprecated and no longer has an effect, to achieve the same effect omit `pitch_value`.
  - Custom presets are now validated at launch and will be disabled if they are malformed along with a warning alert.
- Only Lyrebird controlled PulseAudio sinks are now unloaded instead of all sinks on the system. This fixes a crash on some distros.
- The pitch slider is no longer disabled when a preset is active.
- Default buffer size for SoX is now 128, recommended that you change in `~/.config/lyrebird/config.toml` for improved latency.
- Codebase has been refactored into `core` and `ui`. Audio related methods now live in `core/audio.py` instead of the UI code.
- `AudioVideo` category added to `.desktop`.

## [v1.1.0] - 2020/08/30

### Added

- Volume boost effects
- Window title name
- Distribution specific packages
- New installer and uninstaller scripts
- Only one instance of Lyrebird can be ran at a time

### Changed

- Installer scripts no longer requires bash or sudo
- Handles subprocess better and doesn't kill all SoX instances upon changing preset/closing
- `~/.config/lyrebird` is the only directory for config/presets (`/etc/lyrebird/` no longer used and should be migrated)
- Lyrebird will now automatically create missing config/preset files

## [v1.0.2] - 2020/08/13

### Added

- Explicit permissions to installer to fix launching issues on some distributions

## [v1.0.1] - 2020/08/13

### Added

- Licensed under MIT
- Added shebang line to `App.py`

### Changed

- Default config/preset location is at `/etc/lyrebird` but now can be overridden at `~/.config/lyrebird`
- Renamed `/src` to `/lyrebird` in root of project

## [v1.0.0] - 2020/08/13

### Added

- Initial version of Lyrebird with options to change pitch of voice and downsample audio
- Presets and config are at `/etc/lyrebird`
