import axios from 'axios';
import {
  ArkosApiError,
  ArkosAuthError,
  ArkosRateLimitError,
  ArkosConnectionError,
  ArkosTimeoutError,
} from '../errors';

/**
 * Base resource class.
 */
class Resource {
  /**
   * Create a new Resource.
   * @param {Object} client - The Arkos client
   */
  constructor(client) {
    this.client = client;
  }

  /**
   * Make a URL from a path.
   * @param {string} path - Path
   * @returns {string} URL
   */
  _makeUrl(path) {
    return `${this.client.host}${path}`;
  }

  /**
   * Handle a response.
   * @param {Object} response - Response
   * @returns {Object} Response data
   * @throws {ArkosAuthError} If authentication fails
   * @throws {ArkosRateLimitError} If rate limit is exceeded
   * @throws {ArkosApiError} If API returns an error
   */
  _handleResponse(response) {
    return response.data;
  }

  /**
   * Make a request.
   * @param {string} method - HTTP method
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @param {Object} options.params - Query parameters
   * @param {Object} options.data - Request body
   * @param {Object} options.headers - Headers
   * @param {FormData} options.formData - Form data
   * @param {number} options.retryCount - Number of retries
   * @returns {Promise<Object>} Response data
   * @throws {ArkosConnectionError} If connection fails
   * @throws {ArkosTimeoutError} If request times out
   * @throws {ArkosAuthError} If authentication fails
   * @throws {ArkosRateLimitError} If rate limit is exceeded
   * @throws {ArkosApiError} If API returns an error
   */
  async _request(method, path, options = {}) {
    const {
      params,
      data,
      headers = {},
      formData,
      retryCount = 3,
    } = options;

    const url = this._makeUrl(path);
    const authHeaders = await this.client.auth.getHeaders();
    const requestHeaders = { ...headers, ...authHeaders };

    for (let i = 0; i < retryCount; i++) {
      try {
        const config = {
          method,
          url,
          params,
          headers: requestHeaders,
          timeout: this.client.timeout,
        };

        if (data) {
          config.data = data;
        }

        if (formData) {
          config.data = formData;
          config.headers['Content-Type'] = 'multipart/form-data';
        }

        const response = await axios(config);

        return this._handleResponse(response);
      } catch (error) {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          if (error.response.status === 401) {
            throw new ArkosAuthError(
              error.response.data?.message || 'Authentication failed',
              error.response.data
            );
          } else if (error.response.status === 429) {
            const resetTime = error.response.headers['x-ratelimit-reset'];
            if (resetTime && i < retryCount - 1) {
              const sleepTime = Math.min(
                parseInt(resetTime) * 1000 - Date.now(),
                60000
              );
              if (sleepTime > 0) {
                await new Promise((resolve) => setTimeout(resolve, sleepTime));
                continue;
              }
            } else if (i < retryCount - 1) {
              // If no reset time, use exponential backoff
              await new Promise((resolve) =>
                setTimeout(resolve, Math.pow(2, i) * 1000)
              );
              continue;
            }
            throw new ArkosRateLimitError(resetTime, error.response.data);
          } else if (error.response.status >= 400) {
            const errorData = error.response.data || {};
            const errorCode =
              errorData.error?.code || `error_${error.response.status}`;
            const errorMessage =
              errorData.error?.message || error.message || 'Unknown error';
            const errorDetails = errorData.error?.details || {};
            throw new ArkosApiError(
              error.response.status,
              errorCode,
              errorMessage,
              errorDetails
            );
          }
        } else if (error.code === 'ECONNABORTED') {
          if (i < retryCount - 1) {
            await new Promise((resolve) =>
              setTimeout(resolve, Math.pow(2, i) * 1000)
            );
            continue;
          }
          throw new ArkosTimeoutError();
        } else {
          if (i < retryCount - 1) {
            await new Promise((resolve) =>
              setTimeout(resolve, Math.pow(2, i) * 1000)
            );
            continue;
          }
          throw new ArkosConnectionError(error.message);
        }
      }
    }
  }

  /**
   * Make a GET request.
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async get(path, options = {}) {
    return this._request('GET', path, options);
  }

  /**
   * Make a POST request.
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async post(path, options = {}) {
    return this._request('POST', path, options);
  }

  /**
   * Make a PUT request.
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async put(path, options = {}) {
    return this._request('PUT', path, options);
  }

  /**
   * Make a DELETE request.
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async delete(path, options = {}) {
    return this._request('DELETE', path, options);
  }

  /**
   * Make a PATCH request.
   * @param {string} path - Path
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async patch(path, options = {}) {
    return this._request('PATCH', path, options);
  }
}

export default Resource;
