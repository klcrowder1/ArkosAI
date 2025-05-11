"""
Authentication module for Arkos AI API.
"""

import hashlib
import logging
import os
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from arkos.models import User

logger = logging.getLogger(__name__)

security = HTTPBasic()


def hash_password(password: str, iterations: int = 100000) -> str:
    """
    Hash a password using PBKDF2 with SHA-256.
    
    Args:
        password: Password to hash
        iterations: Number of iterations
        
    Returns:
        str: Hashed password
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=32,
    )
    return f"{iterations}${salt.hex()}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Password to verify
        password_hash: Hash to verify against
        
    Returns:
        bool: True if the password matches the hash
    """
    try:
        iterations_str, salt_hex, key_hex = password_hash.split("$")
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=32,
        )
        
        return key == stored_key
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def requires_auth(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
) -> Dict:
    """
    Require authentication for an endpoint.
    
    Args:
        request: FastAPI request
        credentials: HTTP basic credentials
        
    Returns:
        Dict: User information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if auth is enabled
    if not request.app.state.config.auth.enabled:
        return {"username": "admin", "role": "admin"}
    
    # Get the user from the database
    user = User.get_or_none(User.username == credentials.username)
    
    # Check if the user exists and the password is correct
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return {"username": user.username, "role": user.role}
