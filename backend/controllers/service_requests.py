"""
Service Requests controller - Raw SQL operations for service request management.
"""
from db.connection import get_db_cursor, execute_returning
from datetime import date

SCHEMA = 'vehicle_service'


def get_all_requests():
    """Get all service requests with vehicle and customer info."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT sr.*, 
                   v.plate_no, v.brand AS vehicle_brand, v.model AS vehicle_model, v.year AS vehicle_year, v.color AS vehicle_color,
                   c.customer_id, c.name AS customer_name, c.phone AS customer_phone, c.email AS customer_email, c.address AS customer_address
            FROM {SCHEMA}.service_requests sr
            LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            ORDER BY sr.request_date DESC, sr.request_id DESC
        """)
        return [dict(row) for row in cur.fetchall()]


def get_request_by_id(request_id):
    """Get a single service request with full details."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT sr.*, 
                   v.plate_no, v.brand AS vehicle_brand, v.model AS vehicle_model, v.year AS vehicle_year, v.color AS vehicle_color,
                   c.customer_id, c.name AS customer_name, c.phone AS customer_phone, c.email AS customer_email, c.address AS customer_address
            FROM {SCHEMA}.service_requests sr
            LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            WHERE sr.request_id = %s
        """, (request_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_requests_by_status(status):
    """Get all service requests with a specific status."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT sr.*, 
                   v.plate_no, v.brand AS vehicle_brand, v.model AS vehicle_model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM {SCHEMA}.service_requests sr
            LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            WHERE sr.status = %s
            ORDER BY sr.request_date DESC
        """, (status,))
        return [dict(row) for row in cur.fetchall()]


def get_requests_by_vehicle(vehicle_id):
    """Get all service requests for a specific vehicle."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.service_requests 
            WHERE vehicle_id = %s 
            ORDER BY request_date DESC
        """, (vehicle_id,))
        return [dict(row) for row in cur.fetchall()]


def get_requests_by_customer(customer_id):
    """Get all service requests for a customer (through their vehicles)."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT sr.*, v.plate_no, v.brand AS vehicle_brand, v.model AS vehicle_model
            FROM {SCHEMA}.service_requests sr
            JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
            WHERE v.customer_id = %s
            ORDER BY sr.request_date DESC
        """, (customer_id,))
        return [dict(row) for row in cur.fetchall()]


def create_request(vehicle_id, service_type, problem_note=None, priority='Normal', status='Pending'):
    """Create a new service request. Let SERIAL handle the ID."""
    query = f"""
        INSERT INTO {SCHEMA}.service_requests 
            (vehicle_id, service_type, problem_note, priority, status, request_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = execute_returning(query, (vehicle_id, service_type, problem_note, priority, status, date.today()))
    return dict(result) if result else None


def update_request(request_id, service_type=None, problem_note=None, priority=None, status=None, vehicle_id=None):
    """Update an existing service request."""
    updates = []
    params = []
    
    if service_type is not None:
        updates.append("service_type = %s")
        params.append(service_type)
    if problem_note is not None:
        updates.append("problem_note = %s")
        params.append(problem_note)
    if priority is not None:
        updates.append("priority = %s")
        params.append(priority)
    if status is not None:
        updates.append("status = %s")
        params.append(status)
    if vehicle_id is not None:
        updates.append("vehicle_id = %s")
        params.append(vehicle_id)
    
    if not updates:
        return get_request_by_id(request_id)
    
    params.append(request_id)
    query = f"""
        UPDATE {SCHEMA}.service_requests
        SET {', '.join(updates)}
        WHERE request_id = %s
        RETURNING *
    """
    
    result = execute_returning(query, tuple(params))
    return dict(result) if result else None


def update_request_status(request_id, status):
    """Update the status of a service request."""
    query = f"""
        UPDATE {SCHEMA}.service_requests
        SET status = %s
        WHERE request_id = %s
        RETURNING *
    """
    result = execute_returning(query, (status, request_id))
    return dict(result) if result else None


def delete_request(request_id):
    """Delete a service request (hard delete)."""
    with get_db_cursor() as cur:
        # Check if service request has jobs first
        cur.execute(f"SELECT COUNT(*) as cnt FROM {SCHEMA}.service_jobs WHERE request_id = %s", (request_id,))
        count = cur.fetchone()['cnt']
        if count > 0:
            raise ValueError("Cannot delete service request with associated jobs")
        
        cur.execute(f"DELETE FROM {SCHEMA}.service_requests WHERE request_id = %s RETURNING *", (request_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def request_exists(request_id):
    """Check if a service request exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.service_requests WHERE request_id = %s", (request_id,))
        return cur.fetchone() is not None


def search_requests(search_term):
    """Search service requests by customer name, plate number, or service type."""
    with get_db_cursor() as cur:
        search_pattern = f"%{search_term}%"
        cur.execute(f"""
            SELECT sr.*, v.plate_no, v.brand AS vehicle_brand, v.model AS vehicle_model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM {SCHEMA}.service_requests sr
            LEFT JOIN {SCHEMA}.vehicles v ON sr.vehicle_id = v.vehicle_id
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            WHERE c.name ILIKE %s OR v.plate_no ILIKE %s OR sr.service_type ILIKE %s
            ORDER BY sr.request_date DESC
        """, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in cur.fetchall()]


def get_request_with_employees(request_id):
    """Get a service request with assigned employees from related jobs."""
    with get_db_cursor() as cur:
        # Get the request details
        request = get_request_by_id(request_id)
        if not request:
            return None
        
        # Get employees assigned to this request's jobs
        cur.execute(f"""
            SELECT DISTINCT e.employee_id, e.name AS employee_name, e.role
            FROM {SCHEMA}.service_jobs sj
            JOIN {SCHEMA}.employees e ON sj.assigned_employee = e.employee_id
            WHERE sj.request_id = %s
        """, (request_id,))
        employees = [dict(row) for row in cur.fetchall()]
        
        request['employees'] = employees
        return request


def get_all_requests_with_employees():
    """Get all service requests with assigned employees."""
    requests = get_all_requests()
    
    with get_db_cursor() as cur:
        for req in requests:
            cur.execute(f"""
                SELECT DISTINCT e.employee_id, e.name AS employee_name, e.role
                FROM {SCHEMA}.service_jobs sj
                JOIN {SCHEMA}.employees e ON sj.assigned_employee = e.employee_id
                WHERE sj.request_id = %s
            """, (req['request_id'],))
            req['employees'] = [dict(row) for row in cur.fetchall()]
    
    return requests
