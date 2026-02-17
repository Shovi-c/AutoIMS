"""
Vehicles API routes.
"""
from flask import Blueprint, request, jsonify
from controllers import vehicles as veh_ctrl
from controllers import customers as cust_ctrl
from utils.jwt_utils import token_required

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')


@vehicles_bp.route('', methods=['GET'])
@token_required
def get_all_vehicles(current_user):
    """Get all vehicles. Query params: search=<term>, customer_id=<id>"""
    try:
        search_term = request.args.get('search')
        customer_id = request.args.get('customer_id')
        
        if search_term:
            vehicles = veh_ctrl.search_vehicles(search_term)
        elif customer_id:
            vehicles = veh_ctrl.get_vehicles_by_customer(int(customer_id))
        else:
            vehicles = veh_ctrl.get_all_vehicles()
        
        return jsonify({
            'message': 'Vehicles retrieved successfully',
            'vehicles': vehicles
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get vehicles: {str(e)}'}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
@token_required
def get_vehicle(current_user, vehicle_id):
    """Get a single vehicle by ID."""
    try:
        vehicle = veh_ctrl.get_vehicle_by_id(vehicle_id)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        return jsonify({
            'message': 'Vehicle retrieved successfully',
            'vehicle': vehicle
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get vehicle: {str(e)}'}), 500


@vehicles_bp.route('/plate/<plate_no>', methods=['GET'])
@token_required
def get_vehicle_by_plate(current_user, plate_no):
    """Get a vehicle by plate number."""
    try:
        vehicle = veh_ctrl.get_vehicle_by_plate(plate_no)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        return jsonify({
            'message': 'Vehicle retrieved successfully',
            'vehicle': vehicle
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get vehicle: {str(e)}'}), 500


@vehicles_bp.route('', methods=['POST'])
@token_required
def create_vehicle(current_user):
    """
    Create a new vehicle.
    
    Expected JSON:
    {
        "plate_no": "ABC-1234",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "White",
        "customer_id": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        plate_no = data.get('plate_no')
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')
        color = data.get('color')
        customer_id = data.get('customer_id')
        
        if not plate_no or not plate_no.strip():
            return jsonify({'error': 'Plate number is required'}), 400
        
        if not brand or not brand.strip():
            return jsonify({'error': 'Brand is required'}), 400
        
        if not model or not model.strip():
            return jsonify({'error': 'Model is required'}), 400
        
        if not year:
            return jsonify({'error': 'Year is required'}), 400
        
        if not color or not color.strip():
            return jsonify({'error': 'Color is required'}), 400
        
        if not customer_id:
            return jsonify({'error': 'Customer ID is required'}), 400
        
        # Validate customer exists
        if not cust_ctrl.customer_exists(customer_id):
            return jsonify({'error': 'Customer not found'}), 404
        
        try:
            year = int(year)
        except ValueError:
            return jsonify({'error': 'Invalid year value'}), 400
        
        vehicle = veh_ctrl.create_vehicle(
            plate_no=plate_no.strip(),
            brand=brand.strip(),
            model=model.strip(),
            year=year,
            color=color.strip(),
            customer_id=customer_id
        )
        
        if not vehicle:
            return jsonify({'error': 'Failed to create vehicle'}), 500
        
        return jsonify({
            'message': 'Vehicle created successfully',
            'vehicle': vehicle
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Plate number already exists'}), 409
        return jsonify({'error': f'Failed to create vehicle: {error_msg}'}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@token_required
def update_vehicle(current_user, vehicle_id):
    """
    Update a vehicle.
    
    Expected JSON (all fields optional):
    {
        "plate_no": "XYZ-9876",
        "brand": "Honda",
        "model": "Civic",
        "year": 2023,
        "color": "Black",
        "customer_id": 2
    }
    """
    try:
        if not veh_ctrl.vehicle_exists(vehicle_id):
            return jsonify({'error': 'Vehicle not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate customer if provided
        customer_id = data.get('customer_id')
        if customer_id and not cust_ctrl.customer_exists(customer_id):
            return jsonify({'error': 'Customer not found'}), 404
        
        # Validate year if provided
        year = data.get('year')
        if year:
            try:
                year = int(year)
            except ValueError:
                return jsonify({'error': 'Invalid year value'}), 400
        
        vehicle = veh_ctrl.update_vehicle(
            vehicle_id=vehicle_id,
            plate_no=data.get('plate_no'),
            brand=data.get('brand'),
            model=data.get('model'),
            year=year,
            color=data.get('color'),
            customer_id=customer_id
        )
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Plate number already exists'}), 409
        return jsonify({'error': f'Failed to update vehicle: {error_msg}'}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@token_required
def delete_vehicle(current_user, vehicle_id):
    """Delete a vehicle."""
    try:
        if not veh_ctrl.vehicle_exists(vehicle_id):
            return jsonify({'error': 'Vehicle not found'}), 404
        
        deleted = veh_ctrl.delete_vehicle(vehicle_id)
        
        if not deleted:
            return jsonify({'error': 'Failed to delete vehicle'}), 500
        
        return jsonify({
            'message': 'Vehicle deleted successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': f'Failed to delete vehicle: {str(e)}'}), 500


@vehicles_bp.route('/<int:vehicle_id>/service-requests', methods=['GET'])
@token_required
def get_vehicle_service_requests(current_user, vehicle_id):
    """Get all service requests for a specific vehicle."""
    try:
        if not veh_ctrl.vehicle_exists(vehicle_id):
            return jsonify({'error': 'Vehicle not found'}), 404
        
        from controllers import service_requests as sr_ctrl
        requests = sr_ctrl.get_requests_by_vehicle(vehicle_id)
        
        return jsonify({
            'message': 'Vehicle service requests retrieved successfully',
            'requests': requests
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get service requests: {str(e)}'}), 500
