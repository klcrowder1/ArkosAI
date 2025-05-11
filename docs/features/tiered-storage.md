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
        min_priority: low  # Minimum priority level for recordings to be stored in this tier
        objects: []  # Empty means all objects
        zones: []  # Empty means all zones
        time_ranges: []  # Empty means all times
      
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
        min_priority: medium
        objects: ["person", "car"]  # Only store these object types
        zones: []  # Empty means all zones
      
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
        min_priority: high  # Only store high or critical priority recordings
        objects: []  # Empty means all objects
        zones: ["front_door", "driveway"]  # Only store recordings from these zones
        time_ranges:
          - start_time: "18:00"
            end_time: "06:00"
            days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
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
- `min_priority`: Minimum priority level for recordings to be stored in this tier (low, medium, high, critical)
- `objects`: List of object types to store in this tier (empty means all objects)
- `zones`: List of zones to store in this tier (empty means all zones)
- `time_ranges`: List of time ranges for this tier (empty means all times)
  - `start_time`: Start time in HH:MM format
  - `end_time`: End time in HH:MM format
  - `days`: List of days of the week this time range applies to

## How It Works

The tiered storage system works as follows:

1. Recordings are initially stored in the default tier (the tier with the lowest priority value)
2. Periodically, the system checks for recordings that should be moved to a different tier based on:
   - Age of the recording
   - Whether it's an event recording
   - Priority level of the recording
   - Object types in the recording
   - Zones present in the recording
   - Time of day and day of week when the recording was made
3. If a recording matches the criteria for a different tier, it is moved to that tier
4. If a tier is running low on space (below `min_free_space_mb`), the system will:
   - Try to move recordings to lower-priority tiers based on the tier's criteria
   - If no suitable tier is found, delete the oldest recordings to free up space
5. Event recordings (recordings associated with events marked with `retain_indefinitely=True`) can be prioritized by setting `events_only: true` on specific tiers
6. Higher priority recordings (based on the `priority` field in retention policies) are retained longer when storage is limited

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

### Priority-Based Configuration

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: critical
        path: /media/ssd/critical
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: null
        min_free_space_mb: 5000
        readonly: false
        min_priority: critical
      
      - name: high
        path: /media/ssd/high
        type: hot
        priority: 10
        min_age_days: 0
        max_age_days: 30
        min_free_space_mb: 5000
        readonly: false
        min_priority: high
      
      - name: medium
        path: /media/hdd/medium
        type: warm
        priority: 100
        min_age_days: 0
        max_age_days: 14
        min_free_space_mb: 10000
        readonly: false
        min_priority: medium
      
      - name: low
        path: /media/hdd/low
        type: cold
        priority: 200
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 10000
        readonly: false
        min_priority: low
```

### Object and Zone-Based Configuration

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: people
        path: /media/ssd/people
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: 30
        min_free_space_mb: 5000
        readonly: false
        objects: ["person"]
      
      - name: vehicles
        path: /media/ssd/vehicles
        type: hot
        priority: 10
        min_age_days: 0
        max_age_days: 14
        min_free_space_mb: 5000
        readonly: false
        objects: ["car", "truck", "motorcycle"]
      
      - name: front_door
        path: /media/hdd/front_door
        type: warm
        priority: 100
        min_age_days: 0
        max_age_days: 30
        min_free_space_mb: 10000
        readonly: false
        zones: ["front_door"]
      
      - name: other
        path: /media/hdd/other
        type: cold
        priority: 200
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 10000
        readonly: false
```

### Time-Based Configuration

```yaml
record:
  tiered_storage:
    enabled: true
    check_interval: 3600
    tiers:
      - name: night
        path: /media/ssd/night
        type: hot
        priority: 0
        min_age_days: 0
        max_age_days: 14
        min_free_space_mb: 5000
        readonly: false
        time_ranges:
          - start_time: "18:00"
            end_time: "06:00"
            days: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
      
      - name: weekends
        path: /media/ssd/weekends
        type: hot
        priority: 10
        min_age_days: 0
        max_age_days: 14
        min_free_space_mb: 5000
        readonly: false
        time_ranges:
          - start_time: "00:00"
            end_time: "23:59"
            days: ["saturday", "sunday"]
      
      - name: other
        path: /media/hdd/other
        type: warm
        priority: 100
        min_age_days: 0
        max_age_days: 7
        min_free_space_mb: 10000
        readonly: false
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
        min_priority: high  # Only archive high and critical priority recordings
