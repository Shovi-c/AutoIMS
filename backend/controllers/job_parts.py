"""
Job Parts Used controller - Raw SQL operations for tracking parts used in jobs.
"""
from db.connection import get_db_cursor, get_db_connection

SCHEMA = 'vehicle_service'


def get_parts_for_job(job_id):
    """Get all parts used in a specific job."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT jpu.*, i.part_name, i.part_code, i.brand
            FROM {SCHEMA}.job_parts_used jpu
            JOIN {SCHEMA}.inventory i ON jpu.part_id = i.part_id
            WHERE jpu.job_id = %s
            ORDER BY jpu.job_part_id
        """, (job_id,))
        return [dict(row) for row in cur.fetchall()]


def add_part_to_job(job_id, part_id, quantity_used):
    """
    Add a part to a job and update inventory.
    Uses a transaction to ensure both operations succeed or fail together.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get current unit price from inventory
            cur.execute(f"""
                SELECT unit_price, quantity_in_stock 
                FROM {SCHEMA}.inventory WHERE part_id = %s
            """, (part_id,))
            part = cur.fetchone()
            
            if not part:
                return None, "Part not found"
            
            unit_price = part[0]
            current_stock = part[1]
            
            # Check if enough stock
            if current_stock < quantity_used:
                return None, f"Insufficient stock. Available: {current_stock}, Requested: {quantity_used}"
            
            # Insert into job_parts_used
            cur.execute(f"""
                INSERT INTO {SCHEMA}.job_parts_used (job_id, part_id, quantity_used, unit_price_at_time)
                VALUES (%s, %s, %s, %s)
                RETURNING job_part_id
            """, (job_id, part_id, quantity_used, unit_price))
            job_part_id = cur.fetchone()['job_part_id']
            
            # Update inventory quantity
            cur.execute(f"""
                UPDATE {SCHEMA}.inventory
                SET quantity_in_stock = quantity_in_stock - %s, last_updated = CURRENT_TIMESTAMP
                WHERE part_id = %s
            """, (quantity_used, part_id))
            
            conn.commit()
            
            # Fetch the created record with part details
            cur.execute(f"""
                SELECT jpu.*, i.part_name, i.part_code, i.brand
                FROM {SCHEMA}.job_parts_used jpu
                JOIN {SCHEMA}.inventory i ON jpu.part_id = i.part_id
                WHERE jpu.job_part_id = %s
            """, (job_part_id,))
            
            # Build dict manually since we committed the transaction
            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row)), None
            
            return None, "Failed to retrieve created record"


def remove_part_from_job(job_part_id):
    """
    Remove a part from a job and restore inventory.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get the part usage details first
            cur.execute(f"""
                SELECT part_id, quantity_used 
                FROM {SCHEMA}.job_parts_used WHERE job_part_id = %s
            """, (job_part_id,))
            usage = cur.fetchone()
            
            if not usage:
                return False, "Part usage record not found"
            
            part_id, quantity_used = usage
            
            # Delete the usage record
            cur.execute(f"""
                DELETE FROM {SCHEMA}.job_parts_used WHERE job_part_id = %s
            """, (job_part_id,))
            
            # Restore inventory
            cur.execute(f"""
                UPDATE {SCHEMA}.inventory
                SET quantity_in_stock = quantity_in_stock + %s, last_updated = CURRENT_TIMESTAMP
                WHERE part_id = %s
            """, (quantity_used, part_id))
            
            conn.commit()
            return True, None


def get_total_parts_cost(job_id):
    """Calculate total cost of parts used in a job."""
    with get_db_cursor() as cur:
        cur.execute(f"""
            SELECT COALESCE(SUM(quantity_used * unit_price_at_time), 0) as total
            FROM {SCHEMA}.job_parts_used
            WHERE job_id = %s
        """, (job_id,))
        row = cur.fetchone()
        return float(row['total']) if row else 0.0


def job_exists(job_id):
    """Check if a job exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.service_jobs WHERE job_id = %s", (job_id,))
        return cur.fetchone() is not None


def part_exists(part_id):
    """Check if a part exists."""
    with get_db_cursor() as cur:
        cur.execute(f"SELECT 1 FROM {SCHEMA}.inventory WHERE part_id = %s", (part_id,))
        return cur.fetchone() is not None
