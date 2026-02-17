from flask import Blueprint, request, jsonify
from db.connection import get_db_cursor
from models.user import (
    create_user, get_user_by_email, get_user_by_username,
    verify_password, user_to_dict
)
from utils.jwt_utils import generate_token, token_required

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user.
    
    Expected JSON payload:
        {
            "name": "User Name",
            "username": "johndoe",
            "email": "user@example.com",
            "password": "securepassword"
        }
    
    Returns:
        JSON with message, token, and user info on success
        JSON with error message on failure
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not name.strip():
            return jsonify({'error': 'Name is required'}), 400
        
        if not email or not email.strip():
            return jsonify({'error': 'Email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists by email
        existing_user = get_user_by_email(email.lower().strip())
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Check if username already exists (if provided)
        if username and username.strip():
            existing_username = get_user_by_username(username.strip())
            if existing_username:
                return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        new_user = create_user(
            name=name.strip(),
            email=email.lower().strip(),
            password=password,
            username=username.strip() if username else None
        )
        
        if not new_user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate JWT token
        token = generate_token(new_user['user_id'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user_to_dict(new_user)
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    
    Expected JSON payload:
        {
            "email": "user@example.com",
            "password": "securepassword"
        }
    
    Returns:
        JSON with message, token, and user info on success
        JSON with error message on failure
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not email.strip():
            return jsonify({'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Find user by email
        user = get_user_by_email(email.lower().strip())
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = generate_token(user['user_id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_to_dict(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get the currently authenticated user's information.
    
    Requires:
        Authorization header with Bearer token
    
    Returns:
        JSON with user info on success
        JSON with error message on failure
    """
    try:
        return jsonify({
            'message': 'User retrieved successfully',
            'user': user_to_dict(current_user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500
