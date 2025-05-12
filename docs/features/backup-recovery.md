# Backup and Recovery System

Arkos AI includes a robust backup and recovery system to protect your valuable data. This system allows you to create backups of your configuration, database, recordings, events, and exports, and restore them when needed.

## Backup Types

The backup system supports the following types of content:

- **Configuration**: Backs up all configuration files, including camera settings, detection settings, and other system configurations.
- **Database**: Backs up the Arkos database, which contains event data, recording metadata, and other important information.
- **Recordings**: Backs up video recordings from your cameras.
- **Events**: Backs up event clips and snapshots.
- **Exports**: Backs up exported videos.

## Backup Destinations

Arkos supports multiple backup destinations:

### Local Storage

Store backups on a local disk or network-attached storage (NAS). This is the simplest option and provides quick access to backups.

Example configuration:

```yaml
storage:
  backup:
    destinations:
      - name: local_backup
        type: local
        path: /path/to/backup/directory
        retention_days: 30
        max_backups: 10
```

### Remote Storage (SSH/rsync)

Store backups on a remote server using SSH and rsync. This provides off-site backup capability for better data protection.

Example configuration:

```yaml
storage:
  backup:
    destinations:
      - name: remote_backup
        type: remote
        path: /path/to/backup/directory
        host: backup-server.example.com
        user: backup-user
        ssh_key: /path/to/ssh/key
        retention_days: 30
        max_backups: 10
```

### Cloud Storage (rclone)

Store backups in cloud storage services like Google Drive, Dropbox, Amazon S3, etc., using rclone. This provides the highest level of protection against data loss.

Example configuration:

```yaml
storage:
  backup:
    destinations:
      - name: cloud_backup
        type: cloud
        path: arkos-backups
        provider: gdrive
        rclone_config: /path/to/rclone.conf
        retention_days: 30
        max_backups: 10
```

## Scheduled Backups

Arkos can automatically create backups on a schedule. You can configure multiple schedules with different frequencies, content types, and destinations.

Example configuration:

```yaml
storage:
  backup:
    schedules:
      - name: daily_config_backup
        destination: local_backup
        content_type: config
        frequency: daily
        time: "02:00"
        enabled: true
      
      - name: weekly_full_backup
        destination: remote_backup
        content_type: all
        frequency: weekly
        day: 0  # Sunday
        time: "03:00"
        enabled: true
      
      - name: monthly_cloud_backup
        destination: cloud_backup
        content_type: all
        frequency: monthly
        day: 1  # First day of the month
        time: "04:00"
        enabled: true
```

## Backup Retention

Backups are automatically managed according to the retention policy configured for each destination:

- `retention_days`: Number of days to keep backups before they are automatically deleted.
- `max_backups`: Maximum number of backups to keep for each destination.

## Creating Manual Backups

You can create manual backups through the Arkos web interface or API:

1. Go to the Storage section in the Arkos web interface
2. Select the Backup tab
3. Click "Create Backup"
4. Select the destination and content types
5. Click "Start Backup"

## Restoring from Backup

To restore from a backup:

1. Go to the Storage section in the Arkos web interface
2. Select the Backup tab
3. Find the backup you want to restore
4. Click "Restore"
5. Select the content types to restore
6. Click "Start Restore"

## Backup Verification

Arkos can verify the integrity of backups to ensure they are valid and can be restored if needed. You can manually verify a backup through the web interface or API, or configure automatic verification after backup creation.

## API Access

The backup and recovery system is fully accessible through the Arkos API, allowing for integration with external systems and automation.

API endpoints:

- `GET /api/storage/backup/destinations`: List all backup destinations
- `GET /api/storage/backup/backups`: List all backups
- `POST /api/storage/backup/backups`: Create a new backup
- `GET /api/storage/backup/backups/{backup_id}`: Get backup details
- `DELETE /api/storage/backup/backups/{backup_id}`: Delete a backup
- `POST /api/storage/backup/backups/{backup_id}/restore`: Restore from a backup
- `POST /api/storage/backup/backups/{backup_id}/verify`: Verify a backup

## Best Practices

1. **Multiple Destinations**: Configure backups to multiple destinations for redundancy.
2. **Regular Verification**: Periodically verify your backups to ensure they can be restored if needed.
3. **Off-site Backups**: Use remote or cloud destinations to protect against local disasters.
4. **Regular Testing**: Periodically test the restore process to ensure it works as expected.
5. **Monitor Backup Status**: Check the backup status regularly to ensure backups are being created successfully.
