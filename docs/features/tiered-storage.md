# Tiered Storage

Arkos AI supports tiered storage for recordings, allowing you to optimize storage costs and performance by moving recordings between different storage tiers based on age and importance.

## Overview

Tiered storage enables you to:

- Store recent recordings on fast, expensive storage for quick access
- Move older recordings to slower, less expensive storage for archival
- Automatically migrate recordings between tiers based on age
- Prioritize event recordings for retention in higher-tier storage
- Configure minimum free space requirements for each tier
- Customize age thresholds for each tier

## Configuration

Tiered storage is configured in the `record` section of your configuration file:

```yaml
record:
  # Tiered storage configuration
  tiered_storage:
    enabled: true
    check_interval: 3600  # Check interval in seconds
    tiers:
      # Hot tier (fast, expensive storage for recent recordings)
      - name: hot
        path: /media/ssd/recordings
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 5000
        readonly: false
        events_only: false
      
      # Warm tier (medium-speed storage for older recordings)
      - name: warm
        path: /media/hdd/recordings
        type: warm
        priority: 100
        min_age_days: 7
        max_age_days: 30
        min_free_space_mb: 10000
        readonly: false
        events_only: false
      
      # Cold tier (slow, inexpensive storage for archival recordings)
      - name: cold
        path: /media/nas/recordings
        type: cold
        priority: 200
        min_age_days: 30
        max_age_days: null  # No maximum age
        min_free_space_mb: 50000
        readonly: false
        events_only: true  # Only store event recordings in this tier
```

### Configuration Options

#### Global Options

- `enabled`: Enable or disable tiered storage
- `check_interval`: Interval in seconds to check for recordings to move between tiers

#### Tier Options

Each tier has the following options:

- `name`: Name of the storage tier
- `path`: Path to the storage location
- `type`: Type of storage tier (hot, warm, cold, archive)
- `priority`: Priority of the tier (lower is higher priority)
- `min_age_days`: Minimum age of recordings in days to be stored in this tier
- `max_age_days`: Maximum age of recordings in days to be stored in this tier (null for no maximum)
- `min_free_space_mb`: Minimum free space in MB to maintain on this tier
- `readonly`: Whether this tier is read-only
- `events_only`: Whether this tier should only store event recordings

## How It Works

The tiered storage system works as follows:

1. Recordings are initially stored in the default tier (the tier with the lowest priority value)
2. Periodically, the system checks for recordings that should be moved to a different tier based on their age
3. If a recording's age falls within the age range of a different tier, it is moved to that tier
4. If a tier is running low on space (below `min_free_space_mb`), the system will:
   - Try to move older recordings to lower-priority tiers
   - If no suitable tier is found, delete the oldest recordings to free up space
5. Event recordings (recordings associated with events marked with `retain_indefinitely=True`) can be prioritized by setting `events_only: true` on specific tiers

## Storage Tier Types

Arkos AI supports four types of storage tiers:

- **Hot**: Fast, expensive storage for recent recordings (e.g., NVMe SSD)
- **Warm**: Medium-speed storage for older recordings (e.g., SATA SSD or HDD)
- **Cold**: Slow, inexpensive storage for archival recordings (e.g., NAS or external HDD)
- **Archive**: Very slow storage for long-term archival (e.g., cloud storage or tape)

## Best Practices

### Directory Structure

Each tier maintains the same directory structure as the default recordings directory. When a recording is moved to a different tier, its relative path remains the same, but the base directory changes to the tier's path.

### Storage Planning

When planning your tiered storage:

1. **Hot Tier**: Use fast storage (NVMe SSD) for recent recordings (0-7 days)
2. **Warm Tier**: Use medium-speed storage (SATA SSD or HDD) for older recordings (7-30 days)
3. **Cold Tier**: Use slow, inexpensive storage (NAS or external HDD) for archival recordings (30+ days)
4. **Archive Tier**: Use very slow storage (cloud storage or tape) for long-term archival (optional)

### Capacity Planning

Estimate your storage needs based on:

- Number of cameras
- Recording resolution and frame rate
- Retention period
- Event frequency

For example, a 1080p camera at 5 FPS might use approximately 500 MB per hour. For 10 cameras recording 24/7, that's 120 GB per day, or 3.6 TB per month.

### Performance Considerations

- Ensure your hot tier has enough IOPS to handle concurrent writes from all cameras
- Consider using a separate disk for the database to avoid I/O contention
- Monitor disk usage and performance to adjust tier thresholds as needed

## Troubleshooting

### Recordings Not Moving Between Tiers

If recordings are not moving between tiers as expected:

1. Check that tiered storage is enabled (`tiered_storage.enabled: true`)
2. Verify that the tier paths exist and are writable
3. Check the age thresholds for each tier to ensure they don't overlap incorrectly
4. Look for errors in the logs related to tiered storage

### Disk Space Issues

If a tier is running out of space:

1. Increase the `min_free_space_mb` value for that tier
2. Add more storage to the tier
3. Adjust the age thresholds to move recordings to lower tiers sooner
4. Consider reducing the retention period for non-event recordings

## Example Configurations

### Basic Two-Tier Setup

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: hot
        path: /media/ssd/recordings
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: 14
        min_free_space_mb: 5000
        readonly: false
        events_only: false
      
      - name: cold
        path: /media/hdd/recordings
        type: cold
        priority: 100
        min_age_days: 14
        max_age_days: null
        min_free_space_mb: 10000
        readonly: false
        events_only: false
```

### Event-Focused Configuration

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: events
        path: /media/ssd/recordings
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: null
        min_free_space_mb: 5000
        readonly: false
        events_only: true
      
      - name: regular
        path: /media/hdd/recordings
        type: warm
        priority: 100
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 10000
        readonly: false
        events_only: false
```

### Read-Only Archive Tier

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: hot
        path: /media/ssd/recordings
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 5000
        readonly: false
        events_only: false
      
      - name: archive
        path: /media/backup/recordings
        type: archive
        priority: 100
        min_age_days: 7
        max_age_days: null
        min_free_space_mb: 1000
        readonly: true  # This tier is read-only
        events_only: true
