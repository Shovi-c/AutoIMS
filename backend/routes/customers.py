"""
Customers API routes.
"""
from flask import Blueprint, request, jsonify
from controllers import customers as cust_ctrl
from utils.jwt_utils import token_required

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customers_bp.route('', methods=['GET'])
@token_required
def get_all_customers(current_user):
    """Get all customers. Query param: search=<term> to filter."""
    try:
        search_term = request.args.get('search')
        
        if search_term:
            customers = cust_ctrl.search_customers(search_term)
        else:
            customers = cust_ctrl.get_all_customers()
        
        return jsonify({
            'message': 'Customers retrieved successfully',
            'customers': customers
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get customers: {str(e)}'}), 500


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(current_user, customer_id):
    """Get a single customer by ID."""
    try:
        customer = cust_ctrl.get_customer_by_id(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({
            'message': 'Customer retrieved successfully',
            'customer': customer
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get customer: {str(e)}'}), 500


@customers_bp.route('', methods=['POST'])
@token_required
def create_customer(current_user):
    """
    Create a new customer.
    
    Expected JSON:
    {
        "name": "John Doe",
        "phone": "1234567890",
        "email": "john@example.com",
        "address": "123 Main St"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address')
        
        if not name or not name.strip():
            return jsonify({'error': 'Name is required'}), 400
        
        if not phone or not phone.strip():
            return jsonify({'error': 'Phone is required'}), 400
        
        if not email or not email.strip():
            return jsonify({'error': 'Email is required'}), 400
        
        if not address or not address.strip():
            return jsonify({'error': 'Address is required'}), 400
        
        customer = cust_ctrl.create_customer(
            name=name.strip(),
            phone=phone.strip(),
            email=email.strip(),
            address=address.strip()
        )
        
        if not customer:
            return jsonify({'error': 'Failed to create customer'}), 500
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Phone or email already exists'}), 409
        return jsonify({'error': f'Failed to create customer: {error_msg}'}), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(current_user, customer_id):
    """
    Update a customer.
    
    Expected JSON (all fields optional):
    {
        "name": "Updated Name",
        "phone": "9876543210",
        "email": "updated@example.com",
        "address": "456 New St"
    }
    """
    try:
        if not cust_ctrl.customer_exists(customer_id):
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        customer = cust_ctrl.update_customer(
            customer_id=customer_id,
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address')
        )
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Phone or email already exists'}), 409
        return jsonify({'error': f'Failed to update customer: {error_msg}'}), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_user, customer_id):
    """Delete a customer."""
    try:
        if not cust_ctrl.customer_exists(customer_id):
            return jsonify({'error': 'Customer not found'}), 404
        
        deleted = cust_ctrl.delete_customer(customer_id)
        
        if not deleted:
            return jsonify({'error': 'Failed to delete customer'}), 500
        
        return jsonify({
            'message': 'Customer deleted successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': f'Failed to delete customer: {str(e)}'}), 500


@customers_bp.route('/<int:customer_id>/vehicles', methods=['GET'])
@token_required
def get_customer_vehicles(current_user, customer_id):
    """Get all vehicles for a specific customer."""
    try:
        if not cust_ctrl.customer_exists(customer_id):
            return jsonify({'error': 'Customer not found'}), 404
        
        from controllers import vehicles as veh_ctrl
        vehicles = veh_ctrl.get_vehicles_by_customer(customer_id)
        
        return jsonify({
            'message': 'Customer vehicles retrieved successfully',
            'vehicles': vehicles
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get customer vehicles: {str(e)}'}), 500
