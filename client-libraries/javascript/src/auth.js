import axios from 'axios';
import jwtDecode from 'jwt-decode';
import { ArkosAuthError } from './errors';

/**
 * Base authentication class.
 */
class Auth {
  /**
   * Get authentication headers.
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return {};
  }
}

/**
 * API key authentication.
 */
class ApiKeyAuth extends Auth {
  /**
   * Create a new ApiKeyAuth.
   * @param {string} apiKey - API key
   */
  constructor(apiKey) {
    super();
    this.apiKey = apiKey;
  }

  /**
   * Get authentication headers.
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return {
      'X-API-Key': this.apiKey,
    };
  }
}

/**
 * JWT authentication.
 */
class JwtAuth extends Auth {
  /**
   * Create a new JwtAuth.
   * @param {string} host - API host
   * @param {string} username - Username
   * @param {string} password - Password
   */
  constructor(host, username, password) {
    super();
    this.host = host;
    this.username = username;
    this.password = password;
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = 0;
  }

  /**
   * Login to get JWT tokens.
   * @returns {Promise<void>}
   * @throws {ArkosAuthError} If authentication fails
   */
  async login() {
    try {
      const response = await axios.post(
        `${this.host}/api/v1/auth/login`,
        {
          username: this.username,
          password: this.password,
        }
      );

      this.accessToken = response.data.access_token;
      this.refreshToken = response.data.refresh_token;

      // Decode token to get expiry time
      const decoded = jwtDecode(this.accessToken);
      this.tokenExpiry = decoded.exp || 0;
    } catch (error) {
      throw new ArkosAuthError(
        `Login failed: ${error.message}`,
        error.response?.data
      );
    }
  }

  /**
   * Refresh JWT tokens.
   * @returns {Promise<void>}
   * @throws {ArkosAuthError} If refresh fails
   */
  async refresh() {
    try {
      const response = await axios.post(
        `${this.host}/api/v1/auth/refresh`,
        {},
        {
          headers: {
            Authorization: `Bearer ${this.refreshToken}`,
          },
        }
      );

      this.accessToken = response.data.access_token;
      this.refreshToken = response.data.refresh_token;

      // Decode token to get expiry time
      const decoded = jwtDecode(this.accessToken);
      this.tokenExpiry = decoded.exp || 0;
    } catch (error) {
      // If refresh fails, try to login again
      await this.login();
    }
  }

  /**
   * Get authentication headers.
   * @returns {Promise<Object>} Authentication headers
   */
  async getHeaders() {
    // If no token or token is about to expire, login
    if (!this.accessToken || Date.now() / 1000 > this.tokenExpiry - 60) {
      if (!this.accessToken) {
        await this.login();
      } else {
        await this.refresh();
      }
    }

    return {
      Authorization: `Bearer ${this.accessToken}`,
    };
  }
}

export { Auth, ApiKeyAuth, JwtAuth };
