"""
File utilities for MetaDoc

Provides file handling utilities including:
- Secure file operations
- Hash calculation
- File type detection
- Cleanup operations
"""

import os
import hashlib
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def generate_secure_filename(original_filename, prefix=None):
        """Generate a secure, unique filename"""
        secure_name = secure_filename(original_filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        
        if prefix:
            return f"{prefix}_{timestamp}_{secure_name}"
        else:
            return f"{timestamp}_{secure_name}"
    
    @staticmethod
    def calculate_file_hash(file_path, algorithm='sha256'):
        """Calculate file hash for integrity verification"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def safe_remove_file(file_path):
        """Safely remove a file with error handling"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Failed to remove file {file_path}: {e}")
        return False
    
    @staticmethod
    def ensure_directory_exists(directory_path):
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to create directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def move_file_safely(source, destination):
        """Move file with error handling and directory creation"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            FileUtils.ensure_directory_exists(dest_dir)
            
            # Move file
            shutil.move(source, destination)
            return True, None
        except Exception as e:
            error_msg = f"Failed to move file from {source} to {destination}: {e}"
            current_app.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_file_info(file_path):
        """Get comprehensive file information"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }