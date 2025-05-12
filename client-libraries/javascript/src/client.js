import { Auth, ApiKeyAuth, JwtAuth } from './auth';
import CamerasResource from './resources/cameras';
import EventsResource from './resources/events';
import RecordingsResource from './resources/recordings';
import HealthResource from './resources/health';
import StorageResource from './resources/storage';
import SystemResource from './resources/system';

/**
 * Client for the Arkos API.
 */
class ArkosClient {
  /**
   * Create a new ArkosClient.
   * @param {Object} options - Client options
   * @param {string} options.host - API host
   * @param {string} options.apiKey - API key for authentication
   * @param {string} options.username - Username for JWT authentication
   * @param {string} options.password - Password for JWT authentication
   * @param {number} options.timeout - Request timeout in milliseconds
   */
  constructor(options = {}) {
    const {
      host,
      apiKey,
      username,
      password,
      timeout = 30000,
    } = options;

    if (!host) {
      throw new Error('Host is required');
    }

    this.host = host.endsWith('/') ? host.slice(0, -1) : host;
    this.timeout = timeout;

    // Set up authentication
    if (apiKey) {
      this.auth = new ApiKeyAuth(apiKey);
    } else if (username && password) {
      this.auth = new JwtAuth(this.host, username, password);
    } else {
      this.auth = new Auth();
    }

    // Initialize resources
    this.cameras = new CamerasResource(this);
    this.events = new EventsResource(this);
    this.recordings = new RecordingsResource(this);
    this.health = new HealthResource(this);
    this.storage = new StorageResource(this);
    this.system = new SystemResource(this);
  }
}

export default ArkosClient;
