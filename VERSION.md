# Changelog

All notable changes to the Time Shifter integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-11-24

### Fixed
- Sensors staying `unavailable` because history was fetched via the removed `homeassistant.components.history.get_significant_states` API
- History queries now use `recorder.history` through the recorder database executor

## [0.3.0] - 2026-11-24

### Changed
- Removed the `sensor_name` config field; name and `entity_id` are generated automatically
- Name is now `<source name> <N> hours ago`
- Entity ID is now `sensor.<source_object_id>_<N>_hours_ago`
- Config entry migration to v3 (drops stored `sensor_name`)

## [0.2.1] - 2026-03-24

### Fixed
- Sensor name is kept as a friendly name (e.g. `Energy 1h ago`) instead of being stored as snake_case
- Entity ID is now `sensor.<source_object_id>_<slugified_name>` (e.g. `sensor.socket_z03_energy_energy_1h_ago`)

## [0.2.0] - 2026-03-24

### Added
- Shifted sensors attach to the source entity's device when one exists
- Config entry migration from v1 to v2 (`data` / `options` split)

### Changed
- Refactored to current Home Assistant patterns (`OptionsFlowWithReload`, options stored separately from entry data)
- Sensor name no longer incorrectly prefixed with `sensor.`
- Use `native_unit_of_measurement` instead of legacy `unit_of_measurement`
- Removed `update_version.sh`; version bumps are done directly in `.version`, `manifest.json`, `const.py`, and `VERSION.md`
- Documented that source entity selection uses the standard HA entity picker (multi-term search on entity id / name)

### Removed
- Automatic version management script (`update_version.sh`)
- `hass.data` storage and manual options update listener

## [0.1.1] - 2025-12-02

### Added
- Custom sensor naming field in configuration flow
- Automatic snake_case transformation for sensor names
- User can now specify custom names instead of auto-generated `{entity}_shifted`
- Validation for sensor name (required, non-empty after transformation)

### Changed
- Offset field description clarified to indicate it must be positive

## [0.1.0] - 2025-12-02

### Added
- Initial release of Time Shifter integration
- Time-shifted sensor creation with configurable offset
- Prefetch strategy for efficient memory usage
- UI-based configuration flow
- Options flow for reconfiguration
- Automatic version management script
- Support for positive offset values (historical states only)
- Configurable prefetch interval (default 5 minutes)
- Configurable buffer duration (default 60 seconds)
- State attribute preservation from source entity
- Device class and unit of measurement inheritance
- Detailed state attributes including cache size and actual shift

### Technical Details
- Uses Home Assistant's history API for state retrieval
- Periodic prefetch using `async_track_time_interval`
- Efficient state caching (only stores prefetch window)
- Dependency on Home Assistant's history component

## [Unreleased]

### Planned Features
- Support for multiple sensors in one integration entry
- Configurable sensor naming patterns
- Statistics and analytics on shifted vs. current states
- Optional persistent state caching across restarts
- Support for non-numeric entities (binary sensors, switches, etc.)
