import Resource from './base';

/**
 * Recordings resource.
 */
class RecordingsResource extends Resource {
  /**
   * List recordings for a camera.
   * @param {string} cameraName - Camera name
   * @param {Object} options - Options
   * @param {number} options.after - Filter recordings after this timestamp
   * @param {number} options.before - Filter recordings before this timestamp
   * @returns {Promise<Array>} List of recordings
   */
  async list(cameraName, options = {}) {
    return this.get(`/api/v1/${cameraName}/recordings`, { params: options });
  }

  /**
   * Get recordings storage usage.
   * @returns {Promise<Object>} Storage usage information
   */
  async getStorageUsage() {
    return this.get('/api/v1/recordings/storage');
  }

  /**
   * Get recordings summary.
   * @param {string} timezone - Timezone
   * @param {string} cameras - Comma-separated list of cameras or "all"
   * @returns {Promise<Object>} Recordings summary
   */
  async getSummary(timezone = 'utc', cameras = 'all') {
    return this.get('/api/v1/recordings/summary', {
      params: { timezone, cameras },
    });
  }

  /**
   * Get recordings summary for a specific camera.
   * @param {string} cameraName - Camera name
   * @param {string} timezone - Timezone
   * @returns {Promise<Object>} Camera recordings summary
   */
  async getCameraSummary(cameraName, timezone = 'utc') {
    return this.get(`/api/v1/${cameraName}/recordings/summary`, {
      params: { timezone },
    });
  }

  /**
   * Get recording clip.
   * @param {string} cameraName - Camera name
   * @param {number} startTs - Start timestamp
   * @param {number} endTs - End timestamp
   * @returns {Promise<Blob>} Video data
   */
  async getClip(cameraName, startTs, endTs) {
    return this.get(
      `/api/v1/${cameraName}/start/${startTs}/end/${endTs}/clip.mp4`,
      {
        headers: { Accept: 'video/mp4' },
        responseType: 'blob',
      }
    );
  }

  /**
   * Get snapshot from recording.
   * @param {string} cameraName - Camera name
   * @param {number} frameTime - Frame timestamp
   * @param {Object} options - Options
   * @param {string} options.format - Image format (jpg, png)
   * @param {number} options.height - Image height
   * @returns {Promise<Blob>} Image data
   */
  async getSnapshot(cameraName, frameTime, options = {}) {
    const { format = 'jpg', ...params } = options;
    const validFormats = ['jpg', 'jpeg', 'png'];
    const imageFormat = validFormats.includes(format) ? format : 'jpg';

    return this.get(
      `/api/v1/${cameraName}/recordings/${frameTime}/snapshot.${imageFormat}`,
      {
        params,
        headers: { Accept: 'image/*' },
        responseType: 'blob',
      }
    );
  }

  /**
   * Export recording.
   * @param {string} cameraName - Camera name
   * @param {number} startTime - Start timestamp
   * @param {number} endTime - End timestamp
   * @param {Object} options - Options
   * @param {string} options.playback - Playback factor (realtime, timelapse_25x)
   * @param {string} options.source - Playback source (recordings, preview)
   * @param {string} options.name - Friendly name
   * @param {string} options.image_path - Image path
   * @returns {Promise<Object>} Export information
   */
  async export(cameraName, startTime, endTime, options = {}) {
    return this.post(
      `/api/v1/export/${cameraName}/start/${startTime}/end/${endTime}`,
      { data: options }
    );
  }

  /**
   * Get exports.
   * @returns {Promise<Array>} List of exports
   */
  async getExports() {
    return this.get('/api/v1/exports');
  }

  /**
   * Get export details.
   * @param {string} exportId - Export ID
   * @returns {Promise<Object>} Export details
   */
  async getExport(exportId) {
    return this.get(`/api/v1/exports/${exportId}`);
  }

  /**
   * Rename export.
   * @param {string} exportId - Export ID
   * @param {string} name - New name
   * @returns {Promise<Object>} Response data
   */
  async renameExport(exportId, name) {
    return this.patch(`/api/v1/export/${exportId}/rename`, {
      data: { name },
    });
  }

  /**
   * Delete export.
   * @param {string} exportId - Export ID
   * @returns {Promise<Object>} Response data
   */
  async deleteExport(exportId) {
    return this.delete(`/api/v1/export/${exportId}`);
  }

  /**
   * Get preview.
   * @param {string} cameraName - Camera name
   * @param {number} startTs - Start timestamp
   * @param {number} endTs - End timestamp
   * @param {string} format - Preview format (gif, mp4)
   * @returns {Promise<Blob>} Preview data
   */
  async getPreview(cameraName, startTs, endTs, format = 'gif') {
    const contentType = format === 'gif' ? 'image/gif' : 'video/mp4';
    return this.get(
      `/api/v1/${cameraName}/start/${startTs}/end/${endTs}/preview.${format}`,
      {
        headers: { Accept: contentType },
        responseType: 'blob',
      }
    );
  }
}

export default RecordingsResource;
