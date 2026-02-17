"""
Customers controller - Raw SQL operations for customer management.
"""
from db.connection import get_db_cursor, execute_returning

SCHEMA = 'vehicle_service'


def get_all_customers():
    """Get all customers."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.customers ORDER BY created_at DESC")
        return [dict(row) for row in cur.fetchall()]


def get_customer_by_id(customer_id):
    """Get a single customer by ID."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.customers WHERE customer_id = %s", (customer_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_customer_by_phone(phone):
    """Get a customer by phone number."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.customers WHERE phone = %s", (phone,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_customer_by_email(email):
    """Get a customer by email."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT * FROM {SCHEMA}.customers WHERE email = %s", (email,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_customer(name, phone, email, address):
    """Create a new customer. Let SERIAL handle the ID."""
    query = f"""
        INSERT INTO {SCHEMA}.customers (name, phone, email, address)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    result = execute_returning(query, (name, phone, email, address))
    return dict(result) if result else None


def update_customer(customer_id, name=None, phone=None, email=None, address=None):
    """Update an existing customer."""
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = %s")
        params.append(name)
    if phone is not None:
        updates.append("phone = %s")
        params.append(phone)
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    if address is not None:
        updates.append("address = %s")
        params.append(address)
    
    if not updates:
        return get_customer_by_id(customer_id)
    
    params.append(customer_id)
    query = f"""
        UPDATE {SCHEMA}.customers
        SET {', '.join(updates)}
        WHERE customer_id = %s
        RETURNING *
    """
    
    result = execute_returning(query, tuple(params))
    return dict(result) if result else None


def delete_customer(customer_id):
    """Delete a customer (hard delete)."""
    with get_db_cursor() as cur:
        # Check if customer has vehicles first
        cur.execute(f"SELECT COUNT(*) as cnt FROM {SCHEMA}.vehicles WHERE customer_id = %s", (customer_id,))
        count = cur.fetchone()['cnt']
        if count > 0:
            raise ValueError("Cannot delete customer with associated vehicles")
        
        cur.execute(f"DELETE FROM {SCHEMA}.customers WHERE customer_id = %s RETURNING *", (customer_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def customer_exists(customer_id):
    """Check if a customer exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.customers WHERE customer_id = %s", (customer_id,))
        return cur.fetchone() is not None


def search_customers(search_term):
    """Search customers by name, phone, or email."""
    with get_db_cursor() as cur:
        search_pattern = f"%{search_term}%"
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.customers 
            WHERE name ILIKE %s OR phone ILIKE %s OR email ILIKE %s
            ORDER BY name
        """, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in cur.fetchall()]
