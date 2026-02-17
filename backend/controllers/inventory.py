"""
Inventory controller - Raw SQL operations for inventory management.
"""
from db.connection import get_db_cursor, execute_returning
from datetime import datetime

SCHEMA = 'vehicle_service'


def get_all_items():
    """Get all inventory items."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.inventory ORDER BY part_name")
        return [dict(row) for row in cur.fetchall()]


def get_item_by_id(part_id):
    """Get a single inventory item by ID."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.inventory WHERE part_id = %s", (part_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_low_stock_items():
    """Get items where quantity is at or below reorder level."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.inventory 
            WHERE quantity_in_stock <= reorder_level
            ORDER BY (quantity_in_stock - reorder_level) ASC
        """)
        return [dict(row) for row in cur.fetchall()]


def add_item(part_name, part_code, unit_price, reorder_level, brand=None, quantity_in_stock=0, description=None):
    """Add a new inventory item."""
    query = f"""
        INSERT INTO {SCHEMA}.inventory 
            (part_name, part_code, brand, unit_price, quantity_in_stock, reorder_level, description, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = execute_returning(query, (
        part_name, part_code, brand, unit_price, quantity_in_stock, reorder_level, description, datetime.now()
    ))
    return dict(result) if result else None


def update_stock(part_id, quantity_change):
    """
    Update stock quantity by adding/subtracting.
    Use positive values to add stock, negative to subtract.
    """
    query = f"""
        UPDATE {SCHEMA}.inventory
        SET quantity_in_stock = quantity_in_stock + %s, last_updated = %s
        WHERE part_id = %s
        RETURNING *
    """
    result = execute_returning(query, (quantity_change, datetime.now(), part_id))
    return dict(result) if result else None


def set_stock(part_id, new_quantity):
    """Set stock to a specific quantity."""
    query = f"""
        UPDATE {SCHEMA}.inventory
        SET quantity_in_stock = %s, last_updated = %s
        WHERE part_id = %s
        RETURNING *
    """
    result = execute_returning(query, (new_quantity, datetime.now(), part_id))
    return dict(result) if result else None


def update_item(part_id, part_name=None, part_code=None, brand=None, unit_price=None, 
                quantity_in_stock=None, reorder_level=None, description=None):
    """Update an inventory item."""
    updates = []
    params = []
    
    if part_name is not None:
        updates.append("part_name = %s")
        params.append(part_name)
    if part_code is not None:
        updates.append("part_code = %s")
        params.append(part_code)
    if brand is not None:
        updates.append("brand = %s")
        params.append(brand)
    if unit_price is not None:
        updates.append("unit_price = %s")
        params.append(unit_price)
    if quantity_in_stock is not None:
        updates.append("quantity_in_stock = %s")
        params.append(quantity_in_stock)
    if reorder_level is not None:
        updates.append("reorder_level = %s")
        params.append(reorder_level)
    if description is not None:
        updates.append("description = %s")
        params.append(description)
    
    if not updates:
        return get_item_by_id(part_id)
    
    updates.append("last_updated = %s")
    params.append(datetime.now())
    params.append(part_id)
    
    query = f"""
        UPDATE {SCHEMA}.inventory
        SET {', '.join(updates)}
        WHERE part_id = %s
        RETURNING *
    """
    
    result = execute_returning(query, tuple(params))
    return dict(result) if result else None


def part_exists(part_id):
    """Check if a part exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.inventory WHERE part_id = %s", (part_id,))
        return cur.fetchone() is not None


def check_stock_available(part_id, quantity_needed):
    """Check if enough stock is available."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT quantity_in_stock FROM {SCHEMA}.inventory WHERE part_id = %s", (part_id,))
        row = cur.fetchone()
        if row:
            return row['quantity_in_stock'] >= quantity_needed
        return False
