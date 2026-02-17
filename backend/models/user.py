"""
User model utilities for authentication.
Uses plain Python with werkzeug for password hashing.
No ORM - all database operations use raw SQL.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_db_cursor, execute_returning

SCHEMA = 'vehicle_service'


def hash_password(password):
    """Hash a password for storage."""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)


def create_user(name, email, password, username=None):
    """
    Create a new user in the database.
    
    Returns:
        dict: The created user (without password_hash)
    """
    password_hash = hash_password(password)
    
    query = f"""
        INSERT INTO {SCHEMA}.users (name, username, email, password_hash)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id, name, username, email, created_at
    """
    
    user = execute_returning(query, (name, username, email, password_hash))
    return dict(user) if user else None


def get_user_by_email(email):
    """Find a user by email address."""
    query = f"""
        SELECT user_id, name, username, email, password_hash, created_at
        FROM {SCHEMA}.users
        WHERE email = %s
    """
    
    with get_db_cursor() as cur:
        cur.execute(query, (email.lower().strip(),))
        return cur.fetchone()


def get_user_by_username(username):
    """Find a user by username."""
    query = f"""
        SELECT user_id, name, username, email, password_hash, created_at
        FROM {SCHEMA}.users
        WHERE username = %s
    """
    
    with get_db_cursor() as cur:
        cur.execute(query, (username.strip(),))
        return cur.fetchone()


def get_user_by_id(user_id):
    """Find a user by ID."""
    query = f"""
        SELECT user_id, name, username, email, created_at
        FROM {SCHEMA}.users
        WHERE user_id = %s
    """
    
    with get_db_cursor() as cur:
        cur.execute(query, (user_id,))
        return cur.fetchone()


def user_to_dict(user_row):
    """Convert a user row to a safe dictionary (no password)."""
    if not user_row:
        return None
    
    return {
        'user_id': user_row['user_id'],
        'name': user_row['name'],
        'username': user_row['username'],
        'email': user_row['email'],
        'created_at': user_row['created_at'].isoformat() if user_row.get('created_at') else None
    }
