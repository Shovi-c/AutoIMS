"""
Employees API routes.
"""
import logging
from flask import Blueprint, request, jsonify
from controllers import employees as emp_ctrl
# from utils.jwt_utils import token_required  # Temporarily disabled for testing

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@employees_bp.route('', methods=['GET'])
# @token_required  # Temporarily disabled for testing
def get_all_employees():
    """Get all employees. Query param: include_inactive=true to include inactive."""
    logger.info("==> GET /api/employees called")
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        employees = emp_ctrl.get_all_employees(include_inactive=include_inactive)
        logger.info(f"==> Retrieved {len(employees)} employees from database")
        
        return jsonify({
            'message': 'Employees retrieved successfully',
            'employees': employees
        }), 200
        
    except Exception as e:
        logger.error(f"==> GET /api/employees ERROR: {str(e)}")
        return jsonify({'error': f'Failed to get employees: {str(e)}'}), 500


@employees_bp.route('/<int:employee_id>', methods=['GET'])
# @token_required  # Temporarily disabled for testing
def get_employee(employee_id):
    """Get a single employee by ID."""
    try:
        employee = emp_ctrl.get_employee_by_id(employee_id)
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({
            'message': 'Employee retrieved successfully',
            'employee': employee
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get employee: {str(e)}'}), 500


@employees_bp.route('', methods=['POST'])
# @token_required  # Temporarily disabled for testing
def create_employee():
    """
    Create a new employee.
    
    Expected JSON:
    {
        "name": "John Doe",
        "position": "Mechanic",
        "salary": 50000.00,
        "phone": "1234567890",
        "email": "john@example.com",
        "workingStatus": "Working",
        "rating": 4.5,
        "jobsDone": 10
    }
    
    Note: 'role' is also accepted as alias for 'position'
          'employeeName' is also accepted as alias for 'name'
    """
    logger.info("==> POST /api/employees called")
    try:
        data = request.get_json()
        logger.info(f"==> Received data: {data}")
        
        if not data:
            logger.warning("==> No data provided in request body")
            return jsonify({'error': 'No data provided'}), 400
        
        # Accept multiple field name variations for flexibility
        name = data.get('name') or data.get('employeeName')
        position = data.get('position') or data.get('role')
        salary = data.get('salary', 0.0)
        
        if not name or not str(name).strip():
            logger.warning("==> Name is missing")
            return jsonify({'error': 'Name is required'}), 400
        
        if not position or not str(position).strip():
            logger.warning("==> Position/role is missing")
            return jsonify({'error': 'Position is required'}), 400
        
        logger.info(f"==> Creating employee: name={name}, position={position}, salary={salary}")
        
        employee = emp_ctrl.create_employee(
            name=str(name).strip(),
            position=str(position).strip(),
            salary=float(salary) if salary else 0.0,
            phone=data.get('phone'),
            email=data.get('email'),
            working_status=data.get('workingStatus', 'Working'),
            rating=data.get('rating', 0.0),
            jobs_done=data.get('jobsDone', 0)
        )
        
        if not employee:
            logger.error("==> Controller returned None - insert may have failed")
            return jsonify({'error': 'Failed to create employee'}), 500
        
        logger.info(f"==> Employee created successfully: {employee}")
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee': employee
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"==> POST /api/employees ERROR: {error_msg}")
        if 'unique' in error_msg.lower():
            return jsonify({'error': 'Phone or email already exists'}), 409
        return jsonify({'error': f'Failed to create employee: {error_msg}'}), 500


@employees_bp.route('/<int:employee_id>', methods=['PUT'])
# @token_required  # Temporarily disabled for testing
def update_employee(employee_id):
    """
    Update an employee.
    
    Expected JSON (all fields optional):
    {
        "name": "Updated Name",
        "position": "Manager",
        "salary": 60000.00,
        "phone": "1234567890",
        "email": "john@example.com",
        "workingStatus": "Working",
        "rating": 4.5,
        "jobsDone": 10
    }
    
    Note: 'role' is also accepted as alias for 'position'
          'employeeName' is also accepted as alias for 'name'
    """
    logger.info(f"==> PUT /api/employees/{employee_id} called")
    try:
        # Check if employee exists
        if not emp_ctrl.employee_exists(employee_id):
            logger.warning(f"==> Employee {employee_id} not found")
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        logger.info(f"==> Update data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Accept multiple field name variations
        name = data.get('name') or data.get('employeeName')
        
        employee = emp_ctrl.update_employee(
            employee_id=employee_id,
            name=name,
            position=data.get('position'),
            role=data.get('role'),
            salary=data.get('salary'),
            phone=data.get('phone'),
            email=data.get('email'),
            working_status=data.get('workingStatus'),
            rating=data.get('rating'),
            jobs_done=data.get('jobsDone')
        )
        
        logger.info(f"==> Employee updated: {employee}")
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"==> PUT /api/employees/{employee_id} ERROR: {error_msg}")
        return jsonify({'error': f'Failed to update employee: {error_msg}'}), 500


@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
# @token_required  # Temporarily disabled for testing
def delete_employee(employee_id):
    """Soft delete an employee by setting status to 'Inactive'."""
    logger.info(f"==> DELETE /api/employees/{employee_id} called")
    try:
        # Check if employee exists
        if not emp_ctrl.employee_exists(employee_id):
            logger.warning(f"==> Employee {employee_id} not found")
            return jsonify({'error': 'Employee not found'}), 404
        
        employee = emp_ctrl.soft_delete_employee(employee_id)
        logger.info(f"==> Employee {employee_id} deactivated")
        
        return jsonify({
            'message': 'Employee deactivated successfully',
            'employee': employee
        }), 200
        
    except Exception as e:
        logger.error(f"==> DELETE /api/employees/{employee_id} ERROR: {str(e)}")
        return jsonify({'error': f'Failed to deactivate employee: {str(e)}'}), 500
