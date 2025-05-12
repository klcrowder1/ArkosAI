import Resource from './base';

/**
 * Cameras resource.
 */
class CamerasResource extends Resource {
  /**
   * List all cameras.
   * @returns {Promise<Array>} List of cameras
   */
  async list() {
    return this.get('/api/v1/cameras');
  }

  /**
   * Get camera details.
   * @param {string} cameraId - Camera ID
   * @returns {Promise<Object>} Camera details
   */
  async get(cameraId) {
    return this.get(`/api/v1/cameras/${cameraId}`);
  }

  /**
   * Create a new camera.
   * @param {Object} cameraData - Camera data
   * @returns {Promise<Object>} Created camera
   */
  async create(cameraData) {
    return this.post('/api/v1/cameras', { data: cameraData });
  }

  /**
   * Update an existing camera.
   * @param {string} cameraId - Camera ID
   * @param {Object} cameraData - Camera data
   * @returns {Promise<Object>} Updated camera
   */
  async update(cameraId, cameraData) {
    return this.put(`/api/v1/cameras/${cameraId}`, { data: cameraData });
  }

  /**
   * Delete an existing camera.
   * @param {string} cameraId - Camera ID
   * @returns {Promise<Object>} Response data
   */
  async delete(cameraId) {
    return this.delete(`/api/v1/cameras/${cameraId}`);
  }

  /**
   * Get connection status for cameras.
   * @param {string} cameraId - Camera ID (optional)
   * @returns {Promise<Object>} Connection status
   */
  async getConnectionStatus(cameraId) {
    if (cameraId) {
      return this.get(`/api/v1/cameras/${cameraId}/connection/status`);
    }
    return this.get('/api/v1/cameras/connection/status');
  }

  /**
   * Reset connection for a specific camera.
   * @param {string} cameraId - Camera ID
   * @returns {Promise<Object>} Response data
   */
  async resetConnection(cameraId) {
    return this.post(`/api/v1/cameras/${cameraId}/connection/reset`);
  }

  /**
   * Get the latest frame from a camera.
   * @param {string} cameraId - Camera ID
   * @param {Object} options - Options
   * @param {string} options.format - Image format (jpg, png, webp)
   * @param {boolean} options.bbox - Include bounding box
   * @param {boolean} options.timestamp - Include timestamp
   * @param {boolean} options.zones - Include zones
   * @param {boolean} options.mask - Include mask
   * @param {boolean} options.motion - Include motion
   * @param {boolean} options.regions - Include regions
   * @param {number} options.quality - Image quality
   * @param {number} options.height - Image height
   * @returns {Promise<Blob>} Image data
   */
  async getLatestFrame(cameraId, options = {}) {
    const { format = 'jpg', ...params } = options;
    const validFormats = ['jpg', 'jpeg', 'png', 'webp'];
    const imageFormat = validFormats.includes(format) ? format : 'jpg';

    return this.get(`/api/v1/${cameraId}/latest.${imageFormat}`, {
      params,
      headers: { Accept: 'image/*' },
      responseType: 'blob',
    });
  }

  /**
   * Get MJPEG feed URL for a camera.
   * @param {string} cameraId - Camera ID
   * @param {Object} options - Options
   * @param {number} options.fps - Frames per second
   * @param {number} options.height - Image height
   * @param {boolean} options.bbox - Include bounding box
   * @param {boolean} options.timestamp - Include timestamp
   * @param {boolean} options.zones - Include zones
   * @param {boolean} options.mask - Include mask
   * @param {boolean} options.motion - Include motion
   * @param {boolean} options.regions - Include regions
   * @returns {string} MJPEG feed URL
   */
  getMjpegFeed(cameraId, options = {}) {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      params.append(key, value);
    });
    return `${this.client.host}/api/v1/${cameraId}?${params.toString()}`;
  }

  /**
   * Get PTZ information for a camera.
   * @param {string} cameraId - Camera ID
   * @returns {Promise<Object>} PTZ information
   */
  async getPtzInfo(cameraId) {
    return this.get(`/api/v1/${cameraId}/ptz/info`);
  }

  /**
   * Control PTZ for a camera.
   * @param {string} cameraId - Camera ID
   * @param {string} command - PTZ command
   * @param {Object} options - Command options
   * @returns {Promise<Object>} Response data
   */
  async controlPtz(cameraId, command, options = {}) {
    return this.post(`/api/v1/${cameraId}/ptz/${command}`, { data: options });
  }
}

export default CamerasResource;
