"""
PostgreSQL database connection using psycopg3.
Provides context manager for safe connection handling.
"""
import logging
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_connection():
    """Create and return a new database connection with search_path set."""
    conn = psycopg.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        sslmode='require',
        options='-c search_path=vehicle_service'
    )
    return conn


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically commits on success, rolls back on error, and closes connection.
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM table")
                rows = cur.fetchall()
    """
    conn = None
    try:
        logger.debug("==> Opening database connection")
        conn = get_connection()
        yield conn
        conn.commit()
        logger.debug("==> Transaction COMMITTED successfully")
    except Exception as e:
        logger.error(f"==> Transaction ROLLED BACK due to error: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
            logger.debug("==> Database connection closed")


@contextmanager
def get_db_cursor(dict_cursor=True):
    """
    Context manager that provides a database cursor directly.
    Uses dict_row by default for dict-like row access.
    
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM table")
            rows = cur.fetchall()  # Returns list of dicts
    """
    with get_db_connection() as conn:
        row_factory = dict_row if dict_cursor else None
        with conn.cursor(row_factory=row_factory) as cur:
            yield cur


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query and optionally fetch results.
    
    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters for the query
        fetch_one: Return single row
        fetch_all: Return all rows
    
    Returns:
        Query results or None for non-SELECT queries
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        if fetch_one:
            return cur.fetchone()
        if fetch_all:
            return cur.fetchall()
        return None


def execute_returning(query, params=None):
    """
    Execute an INSERT/UPDATE with RETURNING clause.
    
    Args:
        query: SQL query with RETURNING clause
        params: Tuple of parameters
    
    Returns:
        The returned row as dict
    """
    logger.debug(f"==> execute_returning: {query[:100]}...")
    logger.debug(f"==> params: {params}")
    with get_db_cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        logger.debug(f"==> execute_returning result: {result}")
        return result
