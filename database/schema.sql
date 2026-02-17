-- 1. Kill the old tables in PUBLIC so they stop distracting us
DROP TABLE IF EXISTS public.users, public.employees, public.customers, public.vehicles, 
public.service_requests, public.service_jobs, public.inventory, 
public.job_parts_used, public.billing CASCADE;

-- 2. Wipe and recreate the SCHEMA
DROP SCHEMA IF EXISTS vehicle_service CASCADE;
CREATE SCHEMA vehicle_service;

-- 3. Create the table WITH the schema prefix (Absolute Path)
CREATE TABLE vehicle_service.users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create the employees table in the schema
CREATE TABLE vehicle_service.employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    phone VARCHAR(20),
    email VARCHAR(100),
    working_status VARCHAR(20) DEFAULT 'Working',
    rating DECIMAL(3, 1) DEFAULT 0.0,
    jobs_done INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. CUSTOMER
CREATE TABLE vehicle_service.customers(
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. VEHICLE
CREATE TABLE vehicle_service.vehicles(
    vehicle_id SERIAL PRIMARY KEY,
    plate_no VARCHAR(20) UNIQUE NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(30) NOT NULL,
    customer_id INT REFERENCES vehicle_service.customers(customer_id)
);

-- 7. SERVICE REQUEST
CREATE TABLE vehicle_service.service_requests(
    request_id SERIAL PRIMARY KEY,
    request_date DATE NOT NULL DEFAULT CURRENT_DATE,
    service_type VARCHAR(30) NOT NULL,
    problem_note TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'Normal',
    vehicle_id INT REFERENCES vehicle_service.vehicles(vehicle_id)
);

-- 8. SERVICE JOB
CREATE TABLE vehicle_service.service_jobs(
    job_id SERIAL PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    labor_charge NUMERIC(10,2),
    job_status VARCHAR(20) NOT NULL DEFAULT 'In Progress',
    request_id INT REFERENCES vehicle_service.service_requests(request_id),
    employee_id INT REFERENCES vehicle_service.employees(id)
);

-- 9. INVENTORY
CREATE TABLE vehicle_service.inventory(
    part_id SERIAL PRIMARY KEY,
    part_name VARCHAR(100) NOT NULL,
    part_code VARCHAR(50) UNIQUE NOT NULL,
    brand VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    quantity_in_stock INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL,
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 10. JOB PARTS USED
CREATE TABLE vehicle_service.job_parts_used(
    job_part_id SERIAL PRIMARY KEY,
    quantity_used INT NOT NULL,
    unit_price_at_time NUMERIC(10,2) NOT NULL,
    job_id INT REFERENCES vehicle_service.service_jobs(job_id),
    part_id INT REFERENCES vehicle_service.inventory(part_id)
);

-- 11. BILLING
CREATE TABLE vehicle_service.billing(
    bill_id SERIAL PRIMARY KEY,
    bill_date DATE NOT NULL DEFAULT CURRENT_DATE,
    subtotal_labor NUMERIC(10,2) NOT NULL,
    subtotal_parts NUMERIC(10,2) NOT NULL,
    tax NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    total_amount NUMERIC(10,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Unpaid',
    job_id INT REFERENCES vehicle_service.service_jobs(job_id)
);