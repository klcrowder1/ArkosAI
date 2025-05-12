import Resource from './base';

/**
 * System resource.
 */
class SystemResource extends Resource {
  /**
   * Get system information.
   * @returns {Promise<Object>} System information
   */
  async getInfo() {
    return this.get('/api/v1/system/info');
  }

  /**
   * Get system statistics.
   * @returns {Promise<Object>} System statistics
   */
  async getStats() {
    return this.get('/api/v1/system/stats');
  }

  /**
   * Get system configuration.
   * @returns {Promise<Object>} System configuration
   */
  async getConfig() {
    return this.get('/api/v1/system/config');
  }

  /**
   * Update system configuration.
   * @param {Object} configData - Configuration data
   * @param {boolean} requiresRestart - Whether the update requires a restart
   * @returns {Promise<Object>} Response data
   */
  async updateConfig(configData, requiresRestart = true) {
    return this.put('/api/v1/config/set', {
      data: { requires_restart: requiresRestart ? 1 : 0, ...configData },
    });
  }

  /**
   * Restart the system.
   * @returns {Promise<Object>} Response data
   */
  async restart() {
    return this.post('/api/v1/restart');
  }

  /**
   * Get system logs.
   * @param {string} service - Service name (arkos, nginx, go2rtc)
   * @param {Object} options - Additional parameters
   * @param {string} options.download - Download filename
   * @param {boolean} options.stream - Stream logs
   * @param {number} options.start - Start line
   * @param {number} options.end - End line
   * @returns {Promise<string>} Logs
   */
  async getLogs(service, options = {}) {
    return this.get(`/api/v1/logs/${service}`, { params: options });
  }

  /**
   * Get version.
   * @returns {Promise<string>} Version
   */
  async getVersion() {
    return this.get('/api/v1/version');
  }

  /**
   * Get configuration schema.
   * @returns {Promise<Object>} Configuration schema
   */
  async getConfigSchema() {
    return this.get('/api/v1/config/schema.json');
  }

  /**
   * Get raw configuration.
   * @returns {Promise<Object>} Raw configuration
   */
  async getRawConfig() {
    return this.get('/api/v1/config/raw');
  }

  /**
   * Save configuration.
   * @param {string} configContent - Configuration content
   * @param {string} saveOption - Save option
   * @returns {Promise<Object>} Response data
   */
  async saveConfig(configContent, saveOption) {
    return this.post('/api/v1/config/save', {
      params: { save_option: saveOption },
      data: configContent,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  /**
   * Get labels.
   * @param {string} camera - Camera name
   * @returns {Promise<Array>} Labels
   */
  async getLabels(camera) {
    const params = {};
    if (camera) {
      params.camera = camera;
    }
    return this.get('/api/v1/labels', { params });
  }

  /**
   * Get sub-labels.
   * @param {number} splitJoined - Split joined sub-labels
   * @returns {Promise<Array>} Sub-labels
   */
  async getSubLabels(splitJoined) {
    const params = {};
    if (splitJoined !== undefined) {
      params.split_joined = splitJoined;
    }
    return this.get('/api/v1/sub_labels', { params });
  }

  /**
   * Get recognized license plates.
   * @param {number} splitJoined - Split joined license plates
   * @returns {Promise<Array>} Recognized license plates
   */
  async getRecognizedLicensePlates(splitJoined) {
    const params = {};
    if (splitJoined !== undefined) {
      params.split_joined = splitJoined;
    }
    return this.get('/api/v1/recognized_license_plates', { params });
  }

  /**
   * Get timeline.
   * @param {string} camera - Camera name or "all"
   * @param {number} limit - Maximum number of items to return
   * @param {string} sourceId - Source ID
   * @returns {Promise<Array>} Timeline
   */
  async getTimeline(camera = 'all', limit = 100, sourceId) {
    const params = { camera, limit };
    if (sourceId) {
      params.source_id = sourceId;
    }
    return this.get('/api/v1/timeline', { params });
  }

  /**
   * Get hourly timeline.
   * @param {Object} options - Query parameters
   * @param {string} options.cameras - Comma-separated list of cameras or "all"
   * @param {string} options.labels - Comma-separated list of labels or "all"
   * @param {number} options.after - Filter events after this timestamp
   * @param {number} options.before - Filter events before this timestamp
   * @param {number} options.limit - Maximum number of items to return
   * @param {string} options.timezone - Timezone
   * @returns {Promise<Object>} Hourly timeline
   */
  async getHourlyTimeline(options = {}) {
    return this.get('/api/v1/timeline/hourly', { params: options });
  }
}

export default SystemResource;
