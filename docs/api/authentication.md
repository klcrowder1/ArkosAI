# Authentication and Authorization

This document describes the authentication and authorization system in Arkos AI, including how to authenticate with the API, manage users, API keys, and sessions, and understand the role-based access control system.

## Overview

Arkos AI implements a comprehensive authentication and authorization system to secure the API and ensure that users can only access the resources they are authorized to use. The system includes:

- User authentication with username and password
- JWT token-based authentication
- API key authentication for server-to-server communication
- Session management
- Role-based access control
- Account security features (password policies, account lockout, etc.)

## Authentication Methods

### JWT Token Authentication

JWT (JSON Web Token) authentication is the primary authentication method for user-facing applications. It provides a secure way to authenticate users and maintain their session state.

To authenticate with JWT:

1. Obtain a JWT token by logging in with username and password:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-05-12T10:00:00Z",
    "is_active": true
  }
}
```

2. Use the access token in subsequent requests:

```http
GET /api/v1/cameras
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. When the access token expires, use the refresh token to obtain a new access token:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-05-12T10:00:00Z",
    "is_active": true
  }
}
```

4. To log out and invalidate the current session:

```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### API Key Authentication

API key authentication is designed for server-to-server communication and automated scripts. It provides a simpler authentication method that doesn't require refreshing tokens.

To authenticate with an API key:

1. Create an API key:

```http
POST /api/v1/auth/api-keys
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "My API Key",
  "expires_in_days": 365
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My API Key",
  "key": "abcdef1234567890abcdef1234567890",
  "created_at": "2025-05-12T10:00:00Z",
  "expires_at": "2026-05-12T10:00:00Z",
  "is_active": true
}
```

2. Use the API key in subsequent requests:

```http
GET /api/v1/cameras
X-API-Key: abcdef1234567890abcdef1234567890
```

3. To list all API keys:

```http
GET /api/v1/auth/api-keys
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "My API Key",
    "created_at": "2025-05-12T10:00:00Z",
    "expires_at": "2026-05-12T10:00:00Z",
    "last_used_at": "2025-05-12T10:30:00Z",
    "is_active": true
  }
]
```

4. To delete an API key:

```http
DELETE /api/v1/auth/api-keys/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "success": true,
  "message": "API key My API Key deleted"
}
```

## User Management

### Creating a User

To create a new user:

```http
POST /api/v1/auth/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "username": "john",
  "password": "password123",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "operator"
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "operator",
  "created_at": "2025-05-12T10:00:00Z",
  "updated_at": "2025-05-12T10:00:00Z",
  "is_active": true
}
```

### Listing Users

To list all users:

```http
GET /api/v1/auth/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-05-12T10:00:00Z",
    "is_active": true
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "username": "john",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "operator",
    "created_at": "2025-05-12T10:00:00Z",
    "updated_at": "2025-05-12T10:00:00Z",
    "is_active": true
  }
]
```

### Getting a User

To get a specific user:

```http
GET /api/v1/auth/users/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-05-12T10:00:00Z",
  "is_active": true
}
```

### Updating a User

To update a user:

```http
PUT /api/v1/auth/users/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "email": "admin@arkosai.com",
  "full_name": "Administrator",
  "role": "admin",
  "is_active": true
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "email": "admin@arkosai.com",
  "full_name": "Administrator",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-05-12T11:00:00Z",
  "last_login": "2025-05-12T10:00:00Z",
  "is_active": true
}
```

### Deleting a User

To delete a user:

```http
DELETE /api/v1/auth/users/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "success": true,
  "message": "User admin deleted"
}
```

## Session Management

### Listing Sessions

To list all active sessions for the current user:

```http
GET /api/v1/auth/sessions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2025-05-12T10:00:00Z",
    "expires_at": "2025-05-13T10:00:00Z",
    "last_activity": "2025-05-12T11:00:00Z",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "is_active": true
  }
]
```

### Deleting a Session

To delete a session:

```http
DELETE /api/v1/auth/sessions/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "success": true,
  "message": "Session deleted"
}
```

## Role-Based Access Control

Arkos AI implements a role-based access control system with the following roles:

- **Admin**: Full access to all resources and operations
- **Operator**: Read and write access to most resources, but cannot manage users or system settings
- **Viewer**: Read-only access to resources

Each role has a set of permissions:

- **Admin**: read, write, admin
- **Operator**: read, write
- **Viewer**: read

### Permissions

The following permissions are used in the system:

- **read**: Allows reading resources
- **write**: Allows creating, updating, and deleting resources
- **admin**: Allows managing users, roles, and system settings

### Custom Roles

Custom roles can be defined in the configuration file:

```yaml
auth:
  roles:
    custom_roles:
      camera_operator:
        name: camera_operator
        description: "Camera operator with limited access"
        permissions:
          - read
          - write
```

## Configuration

Authentication and authorization can be configured in the Arkos AI configuration file:

```yaml
auth:
  enabled: true
  jwt:
    secret_key: "your-secret-key"
    algorithm: "HS256"
    access_token_expire_minutes: 1440
    refresh_token_expire_minutes: 10080
  api_key:
    enabled: true
    expiration_days: 365
    key_length: 32
  session:
    enabled: true
    max_sessions_per_user: 5
    session_timeout_minutes: 60
  default_admin_username: "admin"
  default_admin_password: "admin"
  allow_default_admin: true
  password_min_length: 8
  password_require_uppercase: true
  password_require_lowercase: true
  password_require_numbers: true
  password_require_special: true
  failed_login_attempts: 5
  lockout_duration_minutes: 30
```

### Configuration Options

- **enabled**: Whether authentication is enabled
- **jwt**: JWT configuration
  - **secret_key**: Secret key for JWT token signing
  - **algorithm**: JWT algorithm
  - **access_token_expire_minutes**: Access token expiration time in minutes
  - **refresh_token_expire_minutes**: Refresh token expiration time in minutes
- **api_key**: API key configuration
  - **enabled**: Whether API key authentication is enabled
  - **expiration_days**: API key expiration time in days
  - **key_length**: API key length in characters
- **session**: Session configuration
  - **enabled**: Whether session management is enabled
  - **max_sessions_per_user**: Maximum number of active sessions per user
  - **session_timeout_minutes**: Session timeout in minutes
- **default_admin_username**: Default admin username
- **default_admin_password**: Default admin password
- **allow_default_admin**: Whether to allow the default admin user
- **password_min_length**: Minimum password length
- **password_require_uppercase**: Whether passwords require uppercase letters
- **password_require_lowercase**: Whether passwords require lowercase letters
- **password_require_numbers**: Whether passwords require numbers
- **password_require_special**: Whether passwords require special characters
- **failed_login_attempts**: Number of failed login attempts before lockout
- **lockout_duration_minutes**: Account lockout duration in minutes

## Security Considerations

### Password Security

Passwords are stored using PBKDF2 with SHA-256, a secure password hashing algorithm. The system enforces password complexity requirements, including minimum length, uppercase and lowercase letters, numbers, and special characters.

### Account Lockout

To prevent brute force attacks, the system implements an account lockout mechanism. After a configurable number of failed login attempts, the account is locked for a configurable duration.

### Session Management

The system implements secure session management with the following features:

- Sessions expire after a configurable timeout
- Sessions can be revoked by the user
- Sessions are tied to the user's IP address and user agent
- Sessions are limited to a configurable number per user

### API Key Security

API keys are generated using a secure random number generator and are stored using a secure hashing algorithm. API keys can be revoked by the user and have a configurable expiration time.

## Best Practices

### Secure Your Secret Key

The JWT secret key is used to sign and verify JWT tokens. It should be kept secret and should be a strong, random value. It's recommended to set it via an environment variable rather than hardcoding it in the configuration file.

### Use HTTPS

Always use HTTPS in production to encrypt communication between clients and the server. This prevents eavesdropping and man-in-the-middle attacks.

### Regularly Rotate API Keys

Regularly rotate API keys to limit the impact of a compromised key. Set an appropriate expiration time for API keys based on your security requirements.

### Monitor Failed Login Attempts

Monitor failed login attempts to detect potential brute force attacks. Consider implementing additional security measures, such as IP-based rate limiting, for high-security environments.

### Implement Multi-Factor Authentication

For high-security environments, consider implementing multi-factor authentication (MFA) to provide an additional layer of security.

## Conclusion

Arkos AI provides a comprehensive authentication and authorization system that balances security and usability. By following the best practices outlined in this document, you can ensure that your Arkos AI installation is secure and that users can only access the resources they are authorized to use.
