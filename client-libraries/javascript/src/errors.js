/**
 * Base error class for Arkos client errors.
 */
class ArkosError extends Error {
  /**
   * Create a new ArkosError.
   * @param {string} message - Error message
   */
  constructor(message) {
    super(message);
    this.name = 'ArkosError';
    this.isArkosError = true;
  }
}

/**
 * Error class for API errors.
 */
class ArkosApiError extends ArkosError {
  /**
   * Create a new ArkosApiError.
   * @param {number} statusCode - HTTP status code
   * @param {string} errorCode - Error code
   * @param {string} message - Error message
   * @param {Object} details - Error details
   */
  constructor(statusCode, errorCode, message, details = {}) {
    super(message);
    this.name = 'ArkosApiError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.details = details;
  }
}

/**
 * Error class for authentication errors.
 */
class ArkosAuthError extends ArkosApiError {
  /**
   * Create a new ArkosAuthError.
   * @param {string} message - Error message
   * @param {Object} details - Error details
   */
  constructor(message = 'Authentication failed', details = {}) {
    super(401, 'unauthorized', message, details);
    this.name = 'ArkosAuthError';
  }
}

/**
 * Error class for rate limit errors.
 */
class ArkosRateLimitError extends ArkosApiError {
  /**
   * Create a new ArkosRateLimitError.
   * @param {number} resetTime - Time when the rate limit resets
   * @param {Object} details - Error details
   */
  constructor(resetTime = null, details = {}) {
    let message = 'Rate limit exceeded';
    if (resetTime) {
      message += `, resets at ${resetTime}`;
    }
    super(429, 'rate_limit_exceeded', message, details);
    this.name = 'ArkosRateLimitError';
    this.resetTime = resetTime;
  }
}

/**
 * Error class for connection errors.
 */
class ArkosConnectionError extends ArkosError {
  /**
   * Create a new ArkosConnectionError.
   * @param {string} message - Error message
   * @param {Object} details - Error details
   */
  constructor(message = 'Connection error', details = {}) {
    super(message);
    this.name = 'ArkosConnectionError';
    this.details = details;
  }
}

/**
 * Error class for timeout errors.
 */
class ArkosTimeoutError extends ArkosConnectionError {
  /**
   * Create a new ArkosTimeoutError.
   * @param {string} message - Error message
   * @param {Object} details - Error details
   */
  constructor(message = 'Request timed out', details = {}) {
    super(message, details);
    this.name = 'ArkosTimeoutError';
  }
}

export {
  ArkosError,
  ArkosApiError,
  ArkosAuthError,
  ArkosRateLimitError,
  ArkosConnectionError,
  ArkosTimeoutError,
};
