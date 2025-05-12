import Resource from './base';

/**
 * Storage resource.
 */
class StorageResource extends Resource {
  /**
   * Get storage information.
   * @returns {Promise<Object>} Storage information
   */
  async get() {
    return this.get('/api/v1/storage');
  }

  /**
   * Get storage usage statistics.
   * @returns {Promise<Object>} Storage usage statistics
   */
  async getUsage() {
    return this.get('/api/v1/storage/usage');
  }

  /**
   * List backups.
   * @returns {Promise<Array>} List of backups
   */
  async getBackups() {
    return this.get('/api/v1/storage/backups');
  }

  /**
   * Create a new backup.
   * @param {Object} options - Backup options
   * @param {string} options.name - Backup name
   * @param {boolean} options.include_recordings - Include recordings
   * @param {boolean} options.include_events - Include events
   * @param {boolean} options.include_config - Include configuration
   * @returns {Promise<Object>} Backup information
   */
  async createBackup(options = {}) {
    return this.post('/api/v1/storage/backups', { data: options });
  }

  /**
   * Get backup details.
   * @param {string} backupId - Backup ID
   * @returns {Promise<Object>} Backup details
   */
  async getBackup(backupId) {
    return this.get(`/api/v1/storage/backups/${backupId}`);
  }

  /**
   * Delete a backup.
   * @param {string} backupId - Backup ID
   * @returns {Promise<Object>} Response data
   */
  async deleteBackup(backupId) {
    return this.delete(`/api/v1/storage/backups/${backupId}`);
  }

  /**
   * Restore from a backup.
   * @param {Object} options - Restore options
   * @param {string} options.backup_id - Backup ID
   * @param {boolean} options.restore_recordings - Restore recordings
   * @param {boolean} options.restore_events - Restore events
   * @param {boolean} options.restore_config - Restore configuration
   * @returns {Promise<Object>} Restore information
   */
  async restore(options = {}) {
    return this.post('/api/v1/storage/restore', { data: options });
  }

  /**
   * Get restore status.
   * @param {string} restoreId - Restore ID
   * @returns {Promise<Object>} Restore status
   */
  async getRestoreStatus(restoreId) {
    return this.get(`/api/v1/storage/restore/${restoreId}`);
  }

  /**
   * Get storage paths.
   * @returns {Promise<Object>} Storage paths
   */
  async getPaths() {
    return this.get('/api/v1/storage/paths');
  }

  /**
   * Get storage disk information.
   * @returns {Promise<Object>} Storage disk information
   */
  async getDisks() {
    return this.get('/api/v1/storage/disks');
  }

  /**
   * Get storage mount information.
   * @returns {Promise<Object>} Storage mount information
   */
  async getMounts() {
    return this.get('/api/v1/storage/mounts');
  }
}

export default StorageResource;
