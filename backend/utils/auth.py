"""
Authentication utilities for Smart Locomotive Health Monitor
Handles JWT tokens and password hashing
"""

import jwt
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify, current_app
from models.database import User

class AuthManager:
    """Authentication and JWT management"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password for storage"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify a password against its hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_token(user_id, expires_in=None):
        """Generate JWT token for user"""
        if expires_in is None:
            expires_in = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + expires_in,
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    @staticmethod
    def get_token_from_request():
        """Extract JWT token from request headers"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = AuthManager.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = AuthManager.verify_token(token)
        
        if user_id is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user to request context
        request.user_id = user_id
        request.user = User.query.get(user_id)
        
        if not request.user or not request.user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(*roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


class TokenBlacklist:
    """Track invalidated tokens (for logout)"""
    _blacklist = set()
    
    @classmethod
    def add_token(cls, token):
        """Add token to blacklist"""
        cls._blacklist.add(token)
    
    @classmethod
    def is_blacklisted(cls, token):
        """Check if token is blacklisted"""
        return token in cls._blacklist
