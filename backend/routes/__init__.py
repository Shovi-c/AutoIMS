# Routes package
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.employees import employees_bp
from routes.service_jobs import service_jobs_bp
from routes.inventory import inventory_bp
from routes.job_parts import job_parts_bp
from routes.billing import billing_bp
from routes.customers import customers_bp
from routes.vehicles import vehicles_bp
from routes.service_requests import service_requests_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'employees_bp',
    'service_jobs_bp',
    'inventory_bp',
    'job_parts_bp',
    'billing_bp',
    'customers_bp',
    'vehicles_bp',
    'service_requests_bp'
]
