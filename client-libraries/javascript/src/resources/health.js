import Resource from './base';

/**
 * Health resource.
 */
class HealthResource extends Resource {
  /**
   * Get health status of the system, cameras, and storage.
   * @returns {Promise<Object>} Health status
   */
  async get() {
    return this.get('/api/v1/health');
  }

  /**
   * Get system health.
   * @returns {Promise<Object>} System health
   */
  async getSystem() {
    return this.get('/api/v1/health/system');
  }

  /**
   * Get camera health.
   * @returns {Promise<Object>} Camera health
   */
  async getCameras() {
    return this.get('/api/v1/health/cameras');
  }

  /**
   * Get storage health.
   * @returns {Promise<Object>} Storage health
   */
  async getStorage() {
    return this.get('/api/v1/health/storage');
  }

  /**
   * Get system statistics.
   * @returns {Promise<Object>} System statistics
   */
  async getStats() {
    return this.get('/api/v1/stats');
  }

  /**
   * Get system statistics history.
   * @param {string} keys - Comma-separated list of keys to include
   * @returns {Promise<Object>} System statistics history
   */
  async getStatsHistory(keys) {
    const params = {};
    if (keys) {
      params.keys = keys;
    }
    return this.get('/api/v1/stats/history', { params });
  }

  /**
   * Get system metrics.
   * @returns {Promise<Object>} System metrics
   */
  async getMetrics() {
    return this.get('/api/v1/metrics');
  }

  /**
   * Get ffprobe information.
   * @param {string} paths - Comma-separated list of paths to probe
   * @returns {Promise<Object>} FFprobe information
   */
  async getFfprobe(paths) {
    const params = {};
    if (paths) {
      params.paths = paths;
    }
    return this.get('/api/v1/ffprobe', { params });
  }

  /**
   * Get VA-API information.
   * @returns {Promise<Object>} VA-API information
   */
  async getVainfo() {
    return this.get('/api/v1/vainfo');
  }

  /**
   * Get NVIDIA information.
   * @returns {Promise<Object>} NVIDIA information
   */
  async getNvinfo() {
    return this.get('/api/v1/nvinfo');
  }

  /**
   * Get logs for a service.
   * @param {string} service - Service name (arkos, nginx, go2rtc)
   * @param {Object} options - Options
   * @param {string} options.download - Download filename
   * @param {boolean} options.stream - Stream logs
   * @param {number} options.start - Start line
   * @param {number} options.end - End line
   * @returns {Promise<string>} Logs
   */
  async getLogs(service, options = {}) {
    return this.get(`/api/v1/logs/${service}`, { params: options });
  }
}

export default HealthResource;
