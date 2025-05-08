# Database Schema

This document outlines the database schema for Arkos AI, including tables, relationships, and indexes.

## Overview

Arkos AI uses SQLite as its primary database, with extensions for vector search capabilities. The database schema is designed to support the core functionality of the system, including camera management, event detection, recording management, and analytics.

## Database File

The database is stored in a single file:

```
/config/arkos.db
```

## Tables

### Cameras

The `cameras` table stores information about configured cameras.

```sql
CREATE TABLE cameras (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  config TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);
```

### Events

The `events` table stores detected events from cameras.

```sql
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  label TEXT NOT NULL,
  sub_label TEXT,
  start_time REAL NOT NULL,
  end_time REAL,
  top_score REAL,
  false_positive INTEGER DEFAULT 0,
  zones TEXT,
  thumbnail TEXT,
  region TEXT,
  box TEXT,
  area INTEGER,
  has_snapshot INTEGER DEFAULT 0,
  has_clip INTEGER DEFAULT 0,
  retain_indefinitely INTEGER DEFAULT 0,
  current_zones TEXT,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX events_camera_id ON events(camera_id);
CREATE INDEX events_label ON events(label);
CREATE INDEX events_start_time ON events(start_time);
CREATE INDEX events_end_time ON events(end_time);
CREATE INDEX events_zones ON events(zones);
```

### Recordings

The `recordings` table stores information about recorded video segments.

```sql
CREATE TABLE recordings (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  path TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  duration REAL NOT NULL,
  motion INTEGER DEFAULT 0,
  objects TEXT,
  segment_size INTEGER,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX recordings_camera_id ON recordings(camera_id);
CREATE INDEX recordings_start_time ON recordings(start_time);
CREATE INDEX recordings_end_time ON recordings(end_time);
CREATE INDEX recordings_motion ON recordings(motion);
```

### RecordingsToDelete

The `recordings_to_delete` table stores recordings that are marked for deletion.

```sql
CREATE TABLE recordings_to_delete (
  id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  delete_after REAL NOT NULL
);

CREATE INDEX recordings_to_delete_delete_after ON recordings_to_delete(delete_after);
```

### Timeline

The `timeline` table stores timeline events for day-in-the-life analytics.

```sql
CREATE TABLE timeline (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  source_id TEXT,
  type TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id),
  FOREIGN KEY (source_id) REFERENCES events(id)
);

CREATE INDEX timeline_camera_id ON timeline(camera_id);
CREATE INDEX timeline_type ON timeline(type);
CREATE INDEX timeline_start_time ON timeline(start_time);
CREATE INDEX timeline_end_time ON timeline(end_time);
CREATE INDEX timeline_source_id ON timeline(source_id);
```

### Previews

The `previews` table stores preview images for recordings.

```sql
CREATE TABLE previews (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  path TEXT NOT NULL,
  timestamp REAL NOT NULL,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX previews_camera_id ON previews(camera_id);
CREATE INDEX previews_timestamp ON previews(timestamp);
```

### ReviewSegment

The `review_segment` table stores segments for review.

```sql
CREATE TABLE review_segment (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL,
  viewed INTEGER DEFAULT 0,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX review_segment_camera_id ON review_segment(camera_id);
CREATE INDEX review_segment_start_time ON review_segment(start_time);
CREATE INDEX review_segment_end_time ON review_segment(end_time);
CREATE INDEX review_segment_viewed ON review_segment(viewed);
```

### Export

The `export` table stores information about exported clips.

```sql
CREATE TABLE export (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  path TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  created_at REAL NOT NULL,
  status TEXT NOT NULL,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX export_camera_id ON export(camera_id);
CREATE INDEX export_created_at ON export(created_at);
CREATE INDEX export_status ON export(status);
```

### User

The `user` table stores user information for authentication.

```sql
CREATE TABLE user (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  notification_tokens TEXT,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE INDEX user_username ON user(username);
CREATE INDEX user_role ON user(role);
```

### UserReviewStatus

The `user_review_status` table stores review status for each user.

```sql
CREATE TABLE user_review_status (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  review_segment_id TEXT NOT NULL,
  viewed INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (review_segment_id) REFERENCES review_segment(id)
);

CREATE INDEX user_review_status_user_id ON user_review_status(user_id);
CREATE INDEX user_review_status_review_segment_id ON user_review_status(review_segment_id);
```

### Regions

The `regions` table stores region information for cameras.

```sql
CREATE TABLE regions (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  region TEXT NOT NULL,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX regions_camera_id ON regions(camera_id);
```

### HealthStatus

The `health_status` table stores health status information for cameras.

```sql
CREATE TABLE health_status (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  details TEXT,
  timestamp REAL NOT NULL,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX health_status_camera_id ON health_status(camera_id);
CREATE INDEX health_status_type ON health_status(type);
CREATE INDEX health_status_timestamp ON health_status(timestamp);
```

### HealthAlerts

The `health_alerts` table stores health alerts for cameras.

```sql
CREATE TABLE health_alerts (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL,
  details TEXT,
  timestamp REAL NOT NULL,
  acknowledged INTEGER DEFAULT 0,
  resolved INTEGER DEFAULT 0,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX health_alerts_camera_id ON health_alerts(camera_id);
CREATE INDEX health_alerts_type ON health_alerts(type);
CREATE INDEX health_alerts_severity ON health_alerts(severity);
CREATE INDEX health_alerts_timestamp ON health_alerts(timestamp);
CREATE INDEX health_alerts_acknowledged ON health_alerts(acknowledged);
CREATE INDEX health_alerts_resolved ON health_alerts(resolved);
```

### IOState

The `io_state` table stores the state of IO devices.

```sql
CREATE TABLE io_state (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  state TEXT NOT NULL,
  timestamp REAL NOT NULL
);

CREATE INDEX io_state_type ON io_state(type);
CREATE INDEX io_state_name ON io_state(name);
CREATE INDEX io_state_timestamp ON io_state(timestamp);
```

### IOTriggers

The `io_triggers` table stores IO trigger configurations.

```sql
CREATE TABLE io_triggers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  event_type TEXT NOT NULL,
  event_source TEXT,
  event_condition TEXT,
  actions TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE INDEX io_triggers_name ON io_triggers(name);
CREATE INDEX io_triggers_event_type ON io_triggers(event_type);
CREATE INDEX io_triggers_event_source ON io_triggers(event_source);
```

### IOSchedules

The `io_schedules` table stores IO schedule configurations.

```sql
CREATE TABLE io_schedules (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  type TEXT NOT NULL,
  schedule TEXT NOT NULL,
  actions TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE INDEX io_schedules_name ON io_schedules(name);
CREATE INDEX io_schedules_type ON io_schedules(type);
```

### ActivityEvents

The `activity_events` table stores detected activity events.

```sql
CREATE TABLE activity_events (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  type TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL,
  confidence REAL NOT NULL,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX activity_events_camera_id ON activity_events(camera_id);
CREATE INDEX activity_events_type ON activity_events(type);
CREATE INDEX activity_events_start_time ON activity_events(start_time);
CREATE INDEX activity_events_end_time ON activity_events(end_time);
```

### BehaviorEvents

The `behavior_events` table stores detected behavior events.

```sql
CREATE TABLE behavior_events (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  type TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL,
  confidence REAL NOT NULL,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX behavior_events_camera_id ON behavior_events(camera_id);
CREATE INDEX behavior_events_type ON behavior_events(type);
CREATE INDEX behavior_events_start_time ON behavior_events(start_time);
CREATE INDEX behavior_events_end_time ON behavior_events(end_time);
```

### AudioEvents

The `audio_events` table stores detected audio events.

```sql
CREATE TABLE audio_events (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  type TEXT NOT NULL,
  timestamp REAL NOT NULL,
  confidence REAL NOT NULL,
  duration REAL,
  data TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE INDEX audio_events_camera_id ON audio_events(camera_id);
CREATE INDEX audio_events_type ON audio_events(type);
CREATE INDEX audio_events_timestamp ON audio_events(timestamp);
```

### DetectionModels

The `detection_models` table stores information about custom detection models.

```sql
CREATE TABLE detection_models (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  path TEXT NOT NULL,
  config TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE INDEX detection_models_name ON detection_models(name);
CREATE INDEX detection_models_type ON detection_models(type);
```

### CameraModels

The `camera_models` table stores the association between cameras and detection models.

```sql
CREATE TABLE camera_models (
  id TEXT PRIMARY KEY,
  camera_id TEXT NOT NULL,
  model_id TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  zones TEXT,
  schedule TEXT,
  FOREIGN KEY (camera_id) REFERENCES cameras(id),
  FOREIGN KEY (model_id) REFERENCES detection_models(id)
);

CREATE INDEX camera_models_camera_id ON camera_models(camera_id);
CREATE INDEX camera_models_model_id ON camera_models(model_id);
```

### Webhooks

The `webhooks` table stores webhook configurations.

```sql
CREATE TABLE webhooks (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  events TEXT NOT NULL,
  headers TEXT,
  enabled INTEGER DEFAULT 1,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE INDEX webhooks_name ON webhooks(name);
CREATE INDEX webhooks_enabled ON webhooks(enabled);
```

### WebhookDeliveries

The `webhook_deliveries` table stores webhook delivery history.

```sql
CREATE TABLE webhook_deliveries (
  id TEXT PRIMARY KEY,
  webhook_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload TEXT NOT NULL,
  response_code INTEGER,
  response_body TEXT,
  timestamp REAL NOT NULL,
  success INTEGER DEFAULT 0,
  FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
);

CREATE INDEX webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX webhook_deliveries_event_type ON webhook_deliveries(event_type);
CREATE INDEX webhook_deliveries_timestamp ON webhook_deliveries(timestamp);
CREATE INDEX webhook_deliveries_success ON webhook_deliveries(success);
```

### SystemLogs

The `system_logs` table stores system logs.

```sql
CREATE TABLE system_logs (
  id TEXT PRIMARY KEY,
  level TEXT NOT NULL,
  source TEXT NOT NULL,
  message TEXT NOT NULL,
  details TEXT,
  timestamp REAL NOT NULL
);

CREATE INDEX system_logs_level ON system_logs(level);
CREATE INDEX system_logs_source ON system_logs(source);
CREATE INDEX system_logs_timestamp ON system_logs(timestamp);
```

## Vector Search Extensions

For semantic search capabilities, Arkos AI uses SQLite vector extensions.

### EventEmbeddings

The `event_embeddings` table stores embeddings for events to enable semantic search.

```sql
CREATE VIRTUAL TABLE event_embeddings USING vss0(
  embedding(384),
  event_id TEXT,
  camera_id TEXT,
  label TEXT,
  start_time REAL,
  FOREIGN KEY (event_id) REFERENCES events(id),
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);
```

### ImageEmbeddings

The `image_embeddings` table stores embeddings for images to enable semantic search.

```sql
CREATE VIRTUAL TABLE image_embeddings USING vss0(
  embedding(384),
  image_id TEXT,
  camera_id TEXT,
  timestamp REAL,
  FOREIGN KEY (camera_id) REFERENCES cameras(id)
);
```

## Relationships

The following diagram illustrates the relationships between the main tables:

```
cameras
  ├── events
  │     ├── timeline
  │     └── event_embeddings
  ├── recordings
  │     └── previews
  ├── review_segment
  │     └── user_review_status
  ├── regions
  ├── health_status
  ├── health_alerts
  ├── activity_events
  ├── behavior_events
  ├── audio_events
  ├── camera_models
  │     └── detection_models
  └── image_embeddings
```

## Data Types

- `TEXT`: String values
- `INTEGER`: Integer values (0 or 1 for boolean values)
- `REAL`: Floating-point values (used for timestamps as Unix time)
- `BLOB`: Binary data

## Timestamps

All timestamps are stored as Unix time (seconds since the Unix epoch) using the `REAL` data type.

## JSON Data

Several fields store JSON data:
- `config` in the `cameras` table
- `data` in various tables
- `actions` in the `io_triggers` and `io_schedules` tables

## Migrations

Database migrations are managed through the migration system in the `migrations` directory. Each migration is a Python script that defines the changes to be applied to the database schema.

New migrations should be added to the `migrations` directory with a sequential number prefix.

Example migration:

```python
def migrate(db):
    db.execute("""
    CREATE TABLE new_table (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      created_at REAL NOT NULL
    );
    """)
    
    db.execute("""
    CREATE INDEX new_table_name ON new_table(name);
    """)
