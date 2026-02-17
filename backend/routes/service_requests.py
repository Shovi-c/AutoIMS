"""
Service Requests API routes.
"""
from flask import Blueprint, request, jsonify
from controllers import service_requests as sr_ctrl
from controllers import vehicles as veh_ctrl
from controllers import customers as cust_ctrl
from utils.jwt_utils import token_required

service_requests_bp = Blueprint('service_requests', __name__, url_prefix='/api/service-requests')


@service_requests_bp.route('', methods=['GET'])
@token_required
def get_all_requests(current_user):
    """
    Get all service requests with full details.
    Query params: status=<status>, search=<term>, customer_id=<id>, vehicle_id=<id>
    """
    try:
        status_filter = request.args.get('status')
        search_term = request.args.get('search')
        customer_id = request.args.get('customer_id')
        vehicle_id = request.args.get('vehicle_id')
        include_employees = request.args.get('include_employees', 'false').lower() == 'true'
        
        if status_filter:
            requests_list = sr_ctrl.get_requests_by_status(status_filter)
        elif search_term:
            requests_list = sr_ctrl.search_requests(search_term)
        elif customer_id:
            requests_list = sr_ctrl.get_requests_by_customer(int(customer_id))
        elif vehicle_id:
            requests_list = sr_ctrl.get_requests_by_vehicle(int(vehicle_id))
        elif include_employees:
            requests_list = sr_ctrl.get_all_requests_with_employees()
        else:
            requests_list = sr_ctrl.get_all_requests()
        
        return jsonify({
            'message': 'Service requests retrieved successfully',
            'requests': requests_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get service requests: {str(e)}'}), 500


@service_requests_bp.route('/<int:request_id>', methods=['GET'])
@token_required
def get_request(current_user, request_id):
    """Get a single service request by ID."""
    try:
        include_employees = request.args.get('include_employees', 'false').lower() == 'true'
        
        if include_employees:
            service_request = sr_ctrl.get_request_with_employees(request_id)
        else:
            service_request = sr_ctrl.get_request_by_id(request_id)
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
        
        return jsonify({
            'message': 'Service request retrieved successfully',
            'request': service_request
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get service request: {str(e)}'}), 500


@service_requests_bp.route('', methods=['POST'])
@token_required
def create_request(current_user):
    """
    Create a new service request.
    
    Expected JSON:
    {
        "vehicle_id": 1,
        "service_type": "Engine Repair",
        "problem_note": "Engine making noise",  (optional)
        "priority": "High",  (optional, default: "Normal")
        "status": "Pending"  (optional, default: "Pending")
    }
    
    OR for creating with new customer and vehicle:
    {
        "customer": {
            "name": "John Doe",
            "phone": "1234567890",
            "email": "john@example.com",
            "address": "123 Main St"
        },
        "vehicle": {
            "plate_no": "ABC-1234",
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2022,
            "color": "White"
        },
        "service_type": "Engine Repair",
        "problem_note": "Engine making noise",
        "priority": "High"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        vehicle_id = data.get('vehicle_id')
        
        # Check if creating with nested customer/vehicle data
        if not vehicle_id and 'customer' in data and 'vehicle' in data:
            # Create customer first
            cust_data = data.get('customer')
            if not cust_data.get('name') or not cust_data.get('phone') or not cust_data.get('email') or not cust_data.get('address'):
                return jsonify({'error': 'Customer name, phone, email, and address are required'}), 400
            
            customer = cust_ctrl.create_customer(
                name=cust_data['name'].strip(),
                phone=cust_data['phone'].strip(),
                email=cust_data['email'].strip(),
                address=cust_data['address'].strip()
            )
            if not customer:
                return jsonify({'error': 'Failed to create customer'}), 500
            
            # Create vehicle
            veh_data = data.get('vehicle')
            if not veh_data.get('plate_no') or not veh_data.get('brand') or not veh_data.get('model') or not veh_data.get('year') or not veh_data.get('color'):
                return jsonify({'error': 'Vehicle plate_no, brand, model, year, and color are required'}), 400
            
            vehicle = veh_ctrl.create_vehicle(
                plate_no=veh_data['plate_no'].strip(),
                brand=veh_data['brand'].strip(),
                model=veh_data['model'].strip(),
                year=int(veh_data['year']),
                color=veh_data['color'].strip(),
                customer_id=customer['customer_id']
            )
            if not vehicle:
                return jsonify({'error': 'Failed to create vehicle'}), 500
            
            vehicle_id = vehicle['vehicle_id']
        
        if not vehicle_id:
            return jsonify({'error': 'vehicle_id is required'}), 400
        
        # Validate vehicle exists
        if not veh_ctrl.vehicle_exists(vehicle_id):
            return jsonify({'error': 'Vehicle not found'}), 404
        
        service_type = data.get('service_type')
        if not service_type or not service_type.strip():
            return jsonify({'error': 'service_type is required'}), 400
        
        service_request = sr_ctrl.create_request(
            vehicle_id=vehicle_id,
            service_type=service_type.strip(),
            problem_note=data.get('problem_note'),
            priority=data.get('priority', 'Normal'),
            status=data.get('status', 'Pending')
        )
        
        if not service_request:
            return jsonify({'error': 'Failed to create service request'}), 500
        
        # Return full request details
        full_request = sr_ctrl.get_request_by_id(service_request['request_id'])
        
        return jsonify({
            'message': 'Service request created successfully',
            'request': full_request
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Phone, email, or plate number already exists'}), 409
        return jsonify({'error': f'Failed to create service request: {error_msg}'}), 500


@service_requests_bp.route('/<int:request_id>', methods=['PUT'])
@token_required
def update_request(current_user, request_id):
    """
    Update a service request.
    
    Expected JSON (all fields optional):
    {
        "service_type": "Brake Repair",
        "problem_note": "Brakes squeaking",
        "priority": "Normal",
        "status": "In Progress",
        "vehicle_id": 2
    }
    """
    try:
        if not sr_ctrl.request_exists(request_id):
            return jsonify({'error': 'Service request not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate vehicle if provided
        vehicle_id = data.get('vehicle_id')
        if vehicle_id and not veh_ctrl.vehicle_exists(vehicle_id):
            return jsonify({'error': 'Vehicle not found'}), 404
        
        service_request = sr_ctrl.update_request(
            request_id=request_id,
            service_type=data.get('service_type'),
            problem_note=data.get('problem_note'),
            priority=data.get('priority'),
            status=data.get('status'),
            vehicle_id=vehicle_id
        )
        
        # Return full request details
        full_request = sr_ctrl.get_request_by_id(request_id)
        
        return jsonify({
            'message': 'Service request updated successfully',
            'request': full_request
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update service request: {str(e)}'}), 500


@service_requests_bp.route('/<int:request_id>/status', methods=['PUT'])
@token_required
def update_request_status(current_user, request_id):
    """
    Update service request status.
    
    Expected JSON:
    {
        "status": "Completed"
    }
    """
    try:
        if not sr_ctrl.request_exists(request_id):
            return jsonify({'error': 'Service request not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        status = data.get('status')
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['Pending', 'In Progress', 'Completed', 'Cancelled']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        service_request = sr_ctrl.update_request_status(request_id, status)
        
        return jsonify({
            'message': 'Status updated successfully',
            'request': service_request
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500


@service_requests_bp.route('/<int:request_id>', methods=['DELETE'])
@token_required
def delete_request(current_user, request_id):
    """Delete a service request."""
    try:
        if not sr_ctrl.request_exists(request_id):
            return jsonify({'error': 'Service request not found'}), 404
        
        deleted = sr_ctrl.delete_request(request_id)
        
        if not deleted:
            return jsonify({'error': 'Failed to delete service request'}), 500
        
        return jsonify({
            'message': 'Service request deleted successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': f'Failed to delete service request: {str(e)}'}), 500
