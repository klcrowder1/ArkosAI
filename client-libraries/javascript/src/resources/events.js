import Resource from './base';

/**
 * Events resource.
 */
class EventsResource extends Resource {
  /**
   * List events.
   * @param {Object} options - Query parameters
   * @param {string} options.camera - Filter by camera
   * @param {string} options.cameras - Filter by multiple cameras (comma-separated)
   * @param {string} options.label - Filter by label
   * @param {string} options.labels - Filter by multiple labels (comma-separated)
   * @param {string} options.sub_label - Filter by sub-label
   * @param {string} options.sub_labels - Filter by multiple sub-labels (comma-separated)
   * @param {string} options.zone - Filter by zone
   * @param {string} options.zones - Filter by multiple zones (comma-separated)
   * @param {number} options.limit - Maximum number of events to return
   * @param {number} options.after - Filter events after this timestamp
   * @param {number} options.before - Filter events before this timestamp
   * @param {string} options.time_range - Filter events by time range (format: "HH:MM,HH:MM")
   * @param {number} options.has_clip - Filter events with clips (1) or without clips (0)
   * @param {number} options.has_snapshot - Filter events with snapshots (1) or without snapshots (0)
   * @param {number} options.in_progress - Filter in-progress events (1) or completed events (0)
   * @param {number} options.include_thumbnails - Include thumbnails in response (1) or not (0)
   * @param {number} options.favorites - Filter favorite events (1) or non-favorite events (0)
   * @param {number} options.min_score - Filter events with score >= min_score
   * @param {number} options.max_score - Filter events with score <= max_score
   * @param {number} options.min_speed - Filter events with speed >= min_speed
   * @param {number} options.max_speed - Filter events with speed <= max_speed
   * @param {string} options.recognized_license_plate - Filter by recognized license plate
   * @param {number} options.is_submitted - Filter submitted events (1) or non-submitted events (0)
   * @param {number} options.min_length - Filter events with length >= min_length
   * @param {number} options.max_length - Filter events with length <= max_length
   * @param {string} options.event_id - Filter by event ID
   * @param {string} options.sort - Sort events (format: "field:direction")
   * @param {string} options.timezone - Timezone for time-based filtering
   * @returns {Promise<Array>} List of events
   */
  async list(options = {}) {
    return this.get('/api/v1/events', { params: options });
  }

  /**
   * Get event details.
   * @param {string} eventId - Event ID
   * @returns {Promise<Object>} Event details
   */
  async get(eventId) {
    return this.get(`/api/v1/events/${eventId}`);
  }

  /**
   * Delete an event.
   * @param {string} eventId - Event ID
   * @returns {Promise<Object>} Response data
   */
  async delete(eventId) {
    return this.delete(`/api/v1/events/${eventId}`);
  }

  /**
   * Create a new event.
   * @param {string} cameraName - Camera name
   * @param {string} label - Event label
   * @param {Object} options - Additional parameters
   * @param {string} options.source_type - Source type (default: "api")
   * @param {string} options.sub_label - Sub-label
   * @param {number} options.score - Score (default: 0)
   * @param {number} options.duration - Duration in seconds (default: 30)
   * @param {boolean} options.include_recording - Include recording (default: true)
   * @param {Object} options.draw - Drawing options (default: {})
   * @returns {Promise<Object>} Created event
   */
  async create(cameraName, label, options = {}) {
    return this.post(`/api/v1/events/${cameraName}/${label}/create`, {
      data: options,
    });
  }

  /**
   * End an event.
   * @param {string} eventId - Event ID
   * @param {number} endTime - End time
   * @returns {Promise<Object>} Response data
   */
  async end(eventId, endTime) {
    const data = {};
    if (endTime !== undefined) {
      data.end_time = endTime;
    }
    return this.put(`/api/v1/events/${eventId}/end`, { data });
  }

  /**
   * Set retain flag for an event.
   * @param {string} eventId - Event ID
   * @returns {Promise<Object>} Response data
   */
  async setRetain(eventId) {
    return this.post(`/api/v1/events/${eventId}/retain`);
  }

  /**
   * Delete retain flag for an event.
   * @param {string} eventId - Event ID
   * @returns {Promise<Object>} Response data
   */
  async deleteRetain(eventId) {
    return this.delete(`/api/v1/events/${eventId}/retain`);
  }

  /**
   * Set sub-label for an event.
   * @param {string} eventId - Event ID
   * @param {string} subLabel - Sub-label
   * @param {number} subLabelScore - Sub-label score
   * @param {string} camera - Camera name
   * @returns {Promise<Object>} Response data
   */
  async setSubLabel(eventId, subLabel, subLabelScore, camera) {
    const data = { subLabel };
    if (subLabelScore !== undefined) {
      data.subLabelScore = subLabelScore;
    }
    if (camera !== undefined) {
      data.camera = camera;
    }
    return this.post(`/api/v1/events/${eventId}/sub_label`, { data });
  }

  /**
   * Set description for an event.
   * @param {string} eventId - Event ID
   * @param {string} description - Description
   * @returns {Promise<Object>} Response data
   */
  async setDescription(eventId, description) {
    return this.post(`/api/v1/events/${eventId}/description`, {
      data: { description },
    });
  }

  /**
   * Regenerate description for an event.
   * @param {string} eventId - Event ID
   * @param {string} source - Source for description generation (thumbnails or snapshot)
   * @returns {Promise<Object>} Response data
   */
  async regenerateDescription(eventId, source = 'thumbnails') {
    return this.put(`/api/v1/events/${eventId}/description/regenerate`, {
      params: { source },
    });
  }

  /**
   * Delete multiple events.
   * @param {Array<string>} eventIds - List of event IDs
   * @returns {Promise<Object>} Response data
   */
  async deleteMultiple(eventIds) {
    return this.delete('/api/v1/events/', {
      data: { event_ids: eventIds },
    });
  }

  /**
   * Get event snapshot.
   * @param {string} eventId - Event ID
   * @param {Object} options - Additional parameters
   * @param {boolean} options.download - Download snapshot
   * @param {number} options.timestamp - Include timestamp
   * @param {number} options.bbox - Include bounding box
   * @param {number} options.crop - Crop to object
   * @param {number} options.height - Image height
   * @param {number} options.quality - Image quality (default: 70)
   * @returns {Promise<Blob>} Image data
   */
  async getSnapshot(eventId, options = {}) {
    return this.get(`/api/v1/events/${eventId}/snapshot.jpg`, {
      params: options,
      headers: { Accept: 'image/*' },
      responseType: 'blob',
    });
  }

  /**
   * Get event thumbnail.
   * @param {string} eventId - Event ID
   * @param {string} extension - Image extension (jpg, png)
   * @param {Object} options - Additional parameters
   * @param {number} options.max_cache_age - Maximum cache age in seconds
   * @param {string} options.format - Format (ios, android)
   * @returns {Promise<Blob>} Image data
   */
  async getThumbnail(eventId, extension = 'jpg', options = {}) {
    return this.get(`/api/v1/events/${eventId}/thumbnail.${extension}`, {
      params: options,
      headers: { Accept: 'image/*' },
      responseType: 'blob',
    });
  }

  /**
   * Get event clip.
   * @param {string} eventId - Event ID
   * @returns {Promise<Blob>} Video data
   */
  async getClip(eventId) {
    return this.get(`/api/v1/events/${eventId}/clip.mp4`, {
      headers: { Accept: 'video/mp4' },
      responseType: 'blob',
    });
  }

  /**
   * Search events.
   * @param {Object} options - Query parameters
   * @param {string} options.query - Search query
   * @param {string} options.event_id - Event ID for similarity search
   * @param {string} options.search_type - Search type (default: "thumbnail")
   * @param {number} options.include_thumbnails - Include thumbnails in response (default: 1)
   * @param {number} options.limit - Maximum number of events to return (default: 50)
   * @param {string} options.cameras - Filter by cameras (comma-separated)
   * @param {string} options.labels - Filter by labels (comma-separated)
   * @param {string} options.zones - Filter by zones (comma-separated)
   * @param {number} options.after - Filter events after this timestamp
   * @param {number} options.before - Filter events before this timestamp
   * @param {string} options.time_range - Filter events by time range (format: "HH:MM,HH:MM")
   * @param {boolean} options.has_clip - Filter events with clips
   * @param {boolean} options.has_snapshot - Filter events with snapshots
   * @param {boolean} options.is_submitted - Filter submitted events
   * @param {string} options.timezone - Timezone for time-based filtering (default: "utc")
   * @param {number} options.min_score - Filter events with score >= min_score
   * @param {number} options.max_score - Filter events with score <= max_score
   * @param {number} options.min_speed - Filter events with speed >= min_speed
   * @param {number} options.max_speed - Filter events with speed <= max_speed
   * @param {string} options.recognized_license_plate - Filter by recognized license plate
   * @param {string} options.sort - Sort events (format: "field:direction")
   * @returns {Promise<Object>} Search results
   */
  async search(options = {}) {
    return this.get('/api/v1/events/search', { params: options });
  }

  /**
   * Get events summary.
   * @param {Object} options - Query parameters
   * @param {string} options.timezone - Timezone (default: "utc")
   * @param {number} options.has_clip - Filter events with clips (1) or without clips (0)
   * @param {number} options.has_snapshot - Filter events with snapshots (1) or without snapshots (0)
   * @returns {Promise<Object>} Events summary
   */
  async getSummary(options = {}) {
    return this.get('/api/v1/events/summary', { params: options });
  }
}

export default EventsResource;
