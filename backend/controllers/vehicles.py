"""
Vehicles controller - Raw SQL operations for vehicle management.
"""
from db.connection import get_db_cursor, execute_returning

SCHEMA = 'vehicle_service'


def get_all_vehicles():
    """Get all vehicles with customer info."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT v.*, c.name as customer_name, c.phone as customer_phone
            FROM {SCHEMA}.vehicles v
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            ORDER BY v.vehicle_id DESC
        """)
        return [dict(row) for row in cur.fetchall()]


def get_vehicle_by_id(vehicle_id):
    """Get a single vehicle by ID with customer info."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT v.*, c.name as customer_name, c.phone as customer_phone, c.email as customer_email
            FROM {SCHEMA}.vehicles v
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            WHERE v.vehicle_id = %s
        """, (vehicle_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_vehicle_by_plate(plate_no):
    """Get a vehicle by plate number."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.vehicles WHERE plate_no = %s", (plate_no,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_vehicles_by_customer(customer_id):
    """Get all vehicles for a specific customer."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.vehicles 
            WHERE customer_id = %s 
            ORDER BY vehicle_id DESC
        """, (customer_id,))
        return [dict(row) for row in cur.fetchall()]


def create_vehicle(plate_no, brand, model, year, color, customer_id):
    """Create a new vehicle. Let SERIAL handle the ID."""
    query = f"""
        INSERT INTO {SCHEMA}.vehicles (plate_no, brand, model, year, color, customer_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = execute_returning(query, (plate_no, brand, model, year, color, customer_id))
    return dict(result) if result else None


def update_vehicle(vehicle_id, plate_no=None, brand=None, model=None, year=None, color=None, customer_id=None):
    """Update an existing vehicle."""
    updates = []
    params = []
    
    if plate_no is not None:
        updates.append("plate_no = %s")
        params.append(plate_no)
    if brand is not None:
        updates.append("brand = %s")
        params.append(brand)
    if model is not None:
        updates.append("model = %s")
        params.append(model)
    if year is not None:
        updates.append("year = %s")
        params.append(year)
    if color is not None:
        updates.append("color = %s")
        params.append(color)
    if customer_id is not None:
        updates.append("customer_id = %s")
        params.append(customer_id)
    
    if not updates:
        return get_vehicle_by_id(vehicle_id)
    
    params.append(vehicle_id)
    query = f"""
        UPDATE {SCHEMA}.vehicles
        SET {', '.join(updates)}
        WHERE vehicle_id = %s
        RETURNING *
    """
    
    result = execute_returning(query, tuple(params))
    return dict(result) if result else None


def delete_vehicle(vehicle_id):
    """Delete a vehicle (hard delete)."""
    with get_db_cursor() as cur:
        # Check if vehicle has service requests first
        cur.execute(f"SELECT COUNT(*) as cnt FROM {SCHEMA}.service_requests WHERE vehicle_id = %s", (vehicle_id,))
        count = cur.fetchone()['cnt']
        if count > 0:
            raise ValueError("Cannot delete vehicle with associated service requests")
        
        cur.execute(f"DELETE FROM {SCHEMA}.vehicles WHERE vehicle_id = %s RETURNING *", (vehicle_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def vehicle_exists(vehicle_id):
    """Check if a vehicle exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.vehicles WHERE vehicle_id = %s", (vehicle_id,))
        return cur.fetchone() is not None


def search_vehicles(search_term):
    """Search vehicles by plate number, brand, or model."""
    with get_db_cursor() as cur:
        search_pattern = f"%{search_term}%"
        cur.execute(f"""
            SELECT v.*, c.name as customer_name
            FROM {SCHEMA}.vehicles v
            LEFT JOIN {SCHEMA}.customers c ON v.customer_id = c.customer_id
            WHERE v.plate_no ILIKE %s OR v.brand ILIKE %s OR v.model ILIKE %s
            ORDER BY v.vehicle_id DESC
        """, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in cur.fetchall()]
