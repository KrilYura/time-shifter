# Time Shifter

**Version:** 0.3.2

A Home Assistant custom integration that creates time-shifted sensors. Report sensor states from the past with configurable offsets.

## Overview

Time Shifter monitors a source entity and creates a new sensor that displays what the state was N hours ago. It uses a smart prefetch strategy that periodically fetches historical data from Home Assistant's history database, minimizing memory usage. The shifted sensor is attached to the same device as the source entity when one exists.

## Features

- **Time-shifted sensors**: Create sensors that show historical states
- **Configurable offset**: Specify how many hours in the past to report
- **Efficient prefetching**: Only stores a small window of historical data
- **UI configuration**: Easy setup through Home Assistant's UI
- **Reconfigurable**: Update settings without removing the integration
- **Attribute preservation**: Maintains attributes from the source entity
- **Device linking**: Shifted sensor appears on the source entity's device

## Installation

### Manual Installation

1. Copy the `custom_components/time_shifter` directory to your Home Assistant's `config/custom_components/` directory.

   ```bash
   rsync -a --delete custom_components/time_shifter/ /path/to/homeassistant/config/custom_components/time_shifter/
   ```

2. Restart Home Assistant.

3. Add the integration through the UI:
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for "Time Shifter"
   - Follow the configuration steps

### HACS Installation (Future)

This integration is not yet available in HACS but may be added in the future.

## Configuration

### Parameters

- **Source Entity** (required): The entity to shift in time. Uses Home Assistant's standard entity picker, which searches by `entity_id` and friendly name (multi-term queries like `z01 temp` work against ids such as `sensor.socket_z01_temperature`).
- **Offset Hours** (required): How many hours in the past to show the state (must be positive)
- **Prefetch Interval** (optional, default: 5 minutes): How often to fetch new historical data
- **Buffer** (optional, default: 60 seconds): Extra buffer to ensure smooth transitions between prefetch cycles

Name and `entity_id` are generated automatically:
- **Name**: `<source name> <N> hours ago`
- **Entity ID**: `sensor.<source_object_id>_<N>_hours_ago`

Offset, prefetch, and buffer can be changed later via **Configure** on the integration entry.

### Example Setup

**Scenario**: You want to create a sensor that shows what your energy sensor read 1 hour ago.

1. **Source Entity**: `sensor.socket_z03_energy` (name: `Energy`)
2. **Offset Hours**: `1`
3. **Prefetch Interval**: `5` (minutes)
4. **Buffer**: `60` (seconds)

**Result**: A sensor named **Energy 1 hours ago** with `entity_id` `sensor.socket_z03_energy_1_hours_ago`, on the same device as the source when applicable.

### How It Works

The integration uses a prefetch strategy:

1. Every 5 minutes (configurable), it fetches historical states from Home Assistant's database
2. It fetches states from `[now - offset, now - offset + prefetch_interval + buffer]`
3. The shifted sensor reports the appropriate state from this cached window
4. This approach minimizes memory usage while ensuring smooth state updates

**Practical Example**:
- Current time: 14:00
- Offset: 1 hour
- Prefetch interval: 5 minutes
- Buffer: 1 minute

**At 14:00**: Fetch states from 13:00 to 13:06 (5 min + 1 min buffer)
**At 14:05**: Fetch states from 13:05 to 13:11
**And so on...**

## Use Cases

- **Energy monitoring**: Compare current vs. past consumption
- **Weather trends**: See temperature changes hour-by-hour
- **Automation delays**: Trigger actions based on historical states
- **Data analysis**: Create dashboards showing current vs. historical data side-by-side

## Attributes

The shifted sensor includes several attributes:

- `source_entity`: The original entity being tracked
- `offset_hours`: The configured offset
- `prefetch_interval_minutes`: How often data is fetched
- `buffer_seconds`: The configured buffer
- `cache_size`: Number of states currently cached
- `source_attributes`: Attributes from the original state
- `shifted_timestamp`: When the shifted state was recorded
- `actual_shift_seconds`: Actual time difference from now

## Troubleshooting

### Sensor shows "unavailable"

- **Cause**: No historical data found in the cache
- **Solution**:
  - Ensure the source entity has been recording data
  - Check that the offset isn't larger than your history retention period
  - Wait for the next prefetch cycle

### States seem delayed

- **Cause**: Prefetch interval is too large for your use case
- **Solution**: Reduce the prefetch interval in the integration options

### High memory usage

- **Cause**: Very short prefetch interval or long buffer
- **Solution**: Increase prefetch interval or reduce buffer

## Development

### Version Management

When releasing a change, bump the version in all of these files to the same value:

- `.version`
- `custom_components/time_shifter/manifest.json` (`version` field)
- `custom_components/time_shifter/const.py` (`VERSION` constant)
- `README.md` (`**Version:**` at the top)
- `VERSION.md` (changelog entry)

Follow [Semantic Versioning](https://semver.org/). See `.agent/workflows/update-version.md` for the full checklist.

### Releasing

HACS needs a **GitHub Release** (not only a commit on `main`) to show a version like `v0.2.1` instead of a commit hash.

```bash
# After bumping version files and updating VERSION.md:
git add .
git commit -m "Release version X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push && git push --tags

# Then publish a GitHub Release from the tag (gh example):
gh release create vX.Y.Z --repo KrilYura/time-shifter --title "X.Y.Z" --notes-file VERSION.md
```

Or create the release manually: GitHub → **Releases** → **Draft a new release** → select tag `vX.Y.Z` → paste notes from `VERSION.md` → **Publish release**.

### File Structure

```
time_shifter/
├── custom_components/
│   └── time_shifter/
│       ├── __init__.py          # Integration setup / migration
│       ├── config_flow.py       # UI configuration
│       ├── const.py             # Constants and version
│       ├── manifest.json        # Integration metadata
│       ├── sensor.py            # Sensor platform
│       └── strings.json         # Localization
├── .agent/workflows/            # Agent versioning workflow
├── .version                     # Version number
├── README.md                    # This file
└── VERSION.md                   # Changelog
```

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
