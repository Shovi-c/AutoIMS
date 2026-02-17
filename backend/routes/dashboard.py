from flask import Blueprint, jsonify
from db.connection import get_db_cursor
from models.user import user_to_dict
from utils.jwt_utils import token_required

SCHEMA = 'vehicle_service'

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

@dashboard_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user):
    """
    Get dashboard data for the authenticated user.
    
    Requires:
        Authorization header with Bearer token
    
    Returns:
        JSON with dashboard statistics and user info
    """
    try:
        stats = get_dashboard_stats()
        
        return jsonify({
            'message': 'Dashboard data retrieved successfully',
            'user': user_to_dict(current_user),
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/customers', methods=['GET'])
@token_required
def get_customers(current_user):
    """Get all customers."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.customers ORDER BY created_at DESC")
            customers = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Customers retrieved successfully',
            'customers': customers
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get customers: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/vehicles', methods=['GET'])
@token_required
def get_vehicles(current_user):
    """Get all vehicles with customer info."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT v.*, c.name as customer_name, c.phone as customer_phone
                FROM {SCHEMA}.vehicles v
                LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
                ORDER BY v.vehicle_id DESC
            """)
            vehicles = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Vehicles retrieved successfully',
            'vehicles': vehicles
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get vehicles: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/service-requests', methods=['GET'])
@token_required
def get_service_requests(current_user):
    """Get all service requests with vehicle info."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT sr.*, v.plate_no, v.brand, v.model, c.name as customer_name
                FROM {SCHEMA}.service_requests sr
                LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
                LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
                ORDER BY sr.request_date DESC
            """)
            requests = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Service requests retrieved successfully',
            'service_requests': requests
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get service requests: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/service-jobs', methods=['GET'])
@token_required
def get_service_jobs(current_user):
    """Get all service jobs."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT sj.*, sr.service_type, sr.status as request_status,
                       v.plate_no, v.brand, v.model
                FROM {SCHEMA}.service_jobs sj
                LEFT JOIN {SCHEMA}.service_requests sr ON sj.request_id = sr.request_id
                LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
                ORDER BY sj.start_time DESC
            """)
            jobs = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Service jobs retrieved successfully',
            'service_jobs': jobs
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get service jobs: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    """Get all inventory items."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"SELECT * FROM {SCHEMA}.inventory ORDER BY part_name")
            inventory = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Inventory retrieved successfully',
            'inventory': inventory
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get inventory: {str(e)}'}), 500


@dashboard_bp.route('/dashboard/billing', methods=['GET'])
@token_required
def get_billing(current_user):
    """Get all billing records."""
    try:
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT b.*, sj.job_status, sr.service_type,
                       v.plate_no, c.name as customer_name
                FROM {SCHEMA}.billing b
                LEFT JOIN {SCHEMA}.service_jobs sj ON b.job_id = sj.job_id
                LEFT JOIN {SCHEMA}.service_requests sr ON sj.request_id = sr.request_id
                LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
                LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
                ORDER BY b.bill_date DESC
            """)
            bills = [dict(row) for row in cur.fetchall()]
        
        return jsonify({
            'message': 'Billing records retrieved successfully',
            'billing': bills
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get billing: {str(e)}'}), 500


def get_dashboard_stats():
    """Get summary statistics for the dashboard."""
    try:
        with get_db_cursor() as cur:
            # Count customers
            cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.customers")
            customers_count = cur.fetchone()['count'] or 0
            
            # Count vehicles
            cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.vehicles")
            vehicles_count = cur.fetchone()['count'] or 0
            
            # Count pending service requests
            cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.service_requests WHERE status = 'Pending'")
            pending_requests = cur.fetchone()['count'] or 0
            
            # Count active service jobs
            cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.service_jobs WHERE job_status = 'In Progress'")
            active_jobs = cur.fetchone()['count'] or 0
            
            # Count low stock inventory items
            cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.inventory WHERE quantity_in_stock <= reorder_level")
            low_stock = cur.fetchone()['count'] or 0
            
            # Total unpaid bills
            cur.execute(f"SELECT COALESCE(SUM(total_amount), 0) as total FROM {SCHEMA}.billing WHERE payment_status = 'Unpaid'")
            unpaid_total = cur.fetchone()['total'] or 0
            
            # Total revenue (paid bills)
            cur.execute(f"SELECT COALESCE(SUM(total_amount), 0) as total FROM {SCHEMA}.billing WHERE payment_status = 'Paid'")
            total_revenue = cur.fetchone()['total'] or 0
        
        return {
            'customers_count': customers_count,
            'vehicles_count': vehicles_count,
            'pending_requests': pending_requests,
            'active_jobs': active_jobs,
            'low_stock_items': low_stock,
            'unpaid_total': float(unpaid_total),
            'total_revenue': float(total_revenue)
        }
        
    except Exception:
        return {
            'customers_count': 0,
            'vehicles_count': 0,
            'pending_requests': 0,
            'active_jobs': 0,
            'low_stock_items': 0,
            'unpaid_total': 0.0,
            'total_revenue': 0.0
        }
