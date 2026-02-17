"""
Employees controller - Raw SQL operations for employee management.
"""
import logging
from decimal import Decimal
from datetime import datetime
from db.connection import get_db_cursor, execute_returning

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCHEMA = 'vehicle_service'


def _serialize_employee(row):
    """Convert employee row to JSON-serializable dict."""
    if row is None:
        return None
    emp = dict(row)
    # Convert Decimal to float for JSON serialization
    for key in ['salary', 'rating']:
        if key in emp and isinstance(emp[key], Decimal):
            emp[key] = float(emp[key])
    # Convert datetime to ISO string
    if 'created_at' in emp and isinstance(emp['created_at'], datetime):
        emp['created_at'] = emp['created_at'].isoformat()
    return emp


def get_all_employees(include_inactive=False):
    """Get all employees."""
    logger.info(f"==> get_all_employees called")
    with get_db_cursor() as cur:
        if include_inactive:
            cur.execute(f"SELECT * FROM {SCHEMA}.employees ORDER BY created_at DESC")
        else:
            cur.execute(f"SELECT * FROM {SCHEMA}.employees WHERE working_status = 'Working' OR working_status IS NULL ORDER BY created_at DESC")
        rows = cur.fetchall()
        logger.info(f"==> Fetched {len(rows)} rows from database")
        return [_serialize_employee(row) for row in rows]


def get_employee_by_id(employee_id):
    """Get a single employee by ID."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.employees WHERE id = %s", (employee_id,))
        row = cur.fetchone()
        return _serialize_employee(row)


def create_employee(name, position, salary=0.0, phone=None, email=None, working_status='Working', rating=0.0, jobs_done=0):
    """Create a new employee with all fields."""
    logger.info(f"==> create_employee called: name={name}, position={position}, salary={salary}")
    
    query = f"""
        INSERT INTO {SCHEMA}.employees (name, position, salary, phone, email, working_status, rating, jobs_done)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    params = (
        name,
        position,
        float(salary) if salary else 0.0,
        phone,
        email,
        working_status or 'Working',
        float(rating) if rating else 0.0,
        int(jobs_done) if jobs_done else 0
    )
    logger.info(f"==> Executing INSERT with params: {params}")
    result = execute_returning(query, params)
    logger.info(f"==> INSERT result: {result}")
    return _serialize_employee(result)


def update_employee(employee_id, name=None, role=None, position=None, phone=None, email=None, 
                    working_status=None, salary=None, rating=None, jobs_done=None):
    """Update an existing employee."""
    logger.info(f"==> update_employee called for id={employee_id}")
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = %s")
        params.append(name)
    
    # Accept both 'role' and 'position' - map to 'position' column
    pos_value = position or role
    if pos_value is not None:
        updates.append("position = %s")
        params.append(pos_value)
    
    if salary is not None:
        updates.append("salary = %s")
        params.append(float(salary))
    
    if phone is not None:
        updates.append("phone = %s")
        params.append(phone)
    
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    
    if working_status is not None:
        updates.append("working_status = %s")
        params.append(working_status)
    
    if rating is not None:
        updates.append("rating = %s")
        params.append(float(rating))
    
    if jobs_done is not None:
        updates.append("jobs_done = %s")
        params.append(int(jobs_done))
    
    if not updates:
        return get_employee_by_id(employee_id)
    
    params.append(employee_id)
    query = f"""
        UPDATE {SCHEMA}.employees
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING *
    """
    logger.info(f"==> Executing UPDATE with params: {params}")
    
    result = execute_returning(query, tuple(params))
    logger.info(f"==> UPDATE result: {result}")
    return _serialize_employee(result)


def delete_employee(employee_id):
    """Delete an employee (hard delete)."""
    logger.info(f"==> delete_employee called for id={employee_id}")
    query = f"""
        DELETE FROM {SCHEMA}.employees
        WHERE id = %s
        RETURNING *
    """
    result = execute_returning(query, (employee_id,))
    return _serialize_employee(result)


def soft_delete_employee(employee_id):
    """Soft delete employee by setting working_status to 'Not Working'."""
    logger.info(f"==> soft_delete_employee called for id={employee_id}")
    query = f"""
        UPDATE {SCHEMA}.employees
        SET working_status = 'Not Working'
        WHERE id = %s
        RETURNING *
    """
    result = execute_returning(query, (employee_id,))
    return _serialize_employee(result)


def employee_exists(employee_id):
    """Check if an employee exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.employees WHERE id = %s", (employee_id,))
        return cur.fetchone() is not None
