import os
from datetime import timedelta

# Read database password from file
def get_db_password():
    password_file = os.path.join(os.path.dirname(__file__), 'db_password.txt')
    try:
        with open(password_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'postgres'  # Default fallback

class Config:
    """Application configuration class."""
    
    # Database configuration for psycopg2
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or 5432
    DB_NAME = os.environ.get('DB_NAME') or 'vehicle_service_db'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or get_db_password()
    
    # Schema name for all tables
    DB_SCHEMA = 'vehicle_service'
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-super-secret-jwt-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # Application secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
