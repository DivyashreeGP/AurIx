"""
Secure Code Example - Should Pass Advanced Detection (95% Accuracy Test)
Tests: Proper validation, secure practices, no false positives
"""

import re
import hashlib
import secrets
import os
from typing import Optional, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SecureUserManager:
    """Manages user operations securely with proper validation"""
    
    def __init__(self):
        self.min_password_length = 12
        self.valid_email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate_email(self, email: str) -> bool:
        """Validate email format using safe regex"""
        if not isinstance(email, str) or len(email) > 254:
            return False
        return bool(re.match(self.valid_email_pattern, email))
    
    def validate_username(self, username: str) -> bool:
        """Validate username with strict rules"""
        if not isinstance(username, str):
            return False
        if len(username) < 3 or len(username) > 20:
            return False
        # Only alphanumeric and underscores
        return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
    
    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if not isinstance(password, str):
            return False
        if len(password) < self.min_password_length:
            return False
        # Check for complexity: uppercase, lowercase, digit, special
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?]', password))
        return all([has_upper, has_lower, has_digit, has_special])
    
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2 (secure method)"""
        if not isinstance(password, str):
            raise TypeError("Password must be string")
        
        salt = secrets.token_hex(32)  # 64 character hex = 32 bytes
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash - constant time comparison"""
        if not isinstance(password, str) or not isinstance(stored_hash, str):
            return False
        
        try:
            salt, pwd_hash = stored_hash.split('$', 1)
            calculated_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            # Use constant-time comparison to prevent timing attacks
            return secrets.compare_digest(calculated_hash.hex(), pwd_hash)
        except (ValueError, AttributeError):
            logger.warning("Invalid stored hash format")
            return False
    
    def create_user(self, username: str, email: str, password: str) -> Optional[Dict]:
        """Create new user with validation"""
        # Validate all inputs
        if not self.validate_username(username):
            logger.warning(f"Invalid username format: {username}")
            return None
        
        if not self.validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            return None
        
        if not self.validate_password(password):
            logger.warning("Password does not meet complexity requirements")
            return None
        
        # Hash password securely
        password_hash = self.hash_password(password)
        
        # Create user object (in real system, would save to DB with parameterized query)
        user_data = {
            'username': username,  # Already validated
            'email': email,        # Already validated
            'password_hash': password_hash,
            'created_timestamp': secrets.randbits(32)
        }
        
        logger.info(f"User created successfully: {username}")
        return user_data


class SecureFileHandler:
    """Handles file operations securely"""
    
    def __init__(self, base_dir: str = '/tmp/secure'):
        # Restrict to safe directory
        if not isinstance(base_dir, str):
            raise TypeError("base_dir must be string")
        self.base_dir = os.path.abspath(base_dir)
    
    def _validate_filename(self, filename: str) -> bool:
        """Validate filename to prevent path traversal"""
        if not isinstance(filename, str):
            return False
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
            return False
        return True
    
    def safe_read_file(self, filename: str) -> Optional[str]:
        """Read file safely with validation"""
        if not self._validate_filename(filename):
            logger.warning(f"Invalid filename: {filename}")
            return None
        
        # Construct safe path
        safe_path = os.path.join(self.base_dir, filename)
        safe_path = os.path.abspath(safe_path)
        
        # Verify path is still within base_dir (prevent traversal)
        if not safe_path.startswith(self.base_dir):
            logger.error(f"Path traversal attempt detected: {filename}")
            return None
        
        try:
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError) as e:
            logger.error(f"File read error: {str(e)}")
            return None
    
    def safe_write_file(self, filename: str, content: str) -> bool:
        """Write file safely with validation"""
        if not self._validate_filename(filename):
            logger.warning(f"Invalid filename: {filename}")
            return False
        
        if not isinstance(content, str):
            logger.warning("Content must be string")
            return False
        
        # Construct safe path
        safe_path = os.path.join(self.base_dir, filename)
        safe_path = os.path.abspath(safe_path)
        
        # Verify path is within base_dir
        if not safe_path.startswith(self.base_dir):
            logger.error(f"Path traversal attempt detected: {filename}")
            return False
        
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File written successfully: {filename}")
            return True
        except IOError as e:
            logger.error(f"File write error: {str(e)}")
            return False


def process_api_request(user_id: str, action: str, data: str) -> Optional[Dict]:
    """Process API request with proper validation"""
    # Type validation
    if not all(isinstance(x, str) for x in [user_id, action, data]):
        logger.warning("Invalid parameter types")
        return None
    
    # Length validation
    if not (1 <= len(user_id) <= 20) or not (1 <= len(action) <= 50):
        logger.warning("Parameter length exceeded")
        return None
    
    # Whitelist validation for action
    allowed_actions = ['read', 'write', 'delete', 'list']
    if action not in allowed_actions:
        logger.warning(f"Invalid action: {action}")
        return None
    
    # Sanitize user_id
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        logger.warning("Invalid user_id format")
        return None
    
    # Process based on validated action
    try:
        result = {
            'user_id': user_id,
            'action': action,
            'status': 'success'
        }
        logger.info(f"API request processed: {action} for user {user_id}")
        return result
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return None


if __name__ == "__main__":
    # Test secure operations
    print("Testing Secure Code Example...")
    
    # Test user manager
    manager = SecureUserManager()
    
    # Valid user creation
    user = manager.create_user(
        username="john_doe",
        email="john.doe@example.com",
        password="SecureP@ssw0rd123"
    )
    
    if user:
        print(f"✓ User created: {user['username']}")
        
        # Verify password
        is_valid = manager.verify_password("SecureP@ssw0rd123", user['password_hash'])
        print(f"✓ Password verification: {is_valid}")
    
    # Test file handler
    file_handler = SecureFileHandler()
    
    # Safe file write
    success = file_handler.safe_write_file("test_data.txt", "Secure content here")
    print(f"✓ File write: {success}")
    
    # Test API request processing
    result = process_api_request("user_123", "read", "some_data")
    print(f"✓ API request: {result['status'] if result else 'failed'}")
    
    print("\n✅ All secure operations completed successfully!")
