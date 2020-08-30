# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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