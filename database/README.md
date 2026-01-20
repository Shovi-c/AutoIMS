# Vehicle Service Booking and Inventory Management System

## Database Schema

This repository directory contains the PostgreSQL database schema for the Vehicle Service Booking and Inventory Management System.

The database is designed to manage customers, their vehicles, service requests, service jobs, spare parts inventory, and billing information in a structured and normalized manner.

## Database Overview

The database uses a relational design to ensure data consistency, integrity, and efficient querying. All tables are intended to be created under a logical schema (for example `vehicle_service`) in PostgreSQL.

Key features:
- Proper use of primary keys and foreign keys
- Enforcement of data integrity constraints
- Separation of concerns between customers, vehicles, services, inventory, and billing
- Support for backend API integration through structured SQL tables

---

## Schema Structure

The main entities and relationships:

- customers — customers who own vehicles
- vehicles — vehicles owned by customers
- service_requests — requests opened for a vehicle (type, problem, status)
- service_jobs — actual work performed for a request (timing, labor)
- inventory — spare parts / stock (parts used for jobs)
- job_parts_used — join table for parts used by a service job
- billing — billing records per service job

Relationships:
- vehicles.customer_id -> customers.customer_id
- service_requests.vehicle_id -> vehicles.vehicle_id
- service_jobs.request_id -> service_requests.request_id
- job_parts_used.job_id -> service_jobs.job_id
- job_parts_used.part_id -> inventory.part_id
- billing.job_id -> service_jobs.job_id

---

## Table Definitions (human-readable)

- customers
  - customer_id (PK): integer identifier for the customer
  - name: full name
  - phone: unique contact number
  - email: unique email
  - address: postal address
  - created_at: timestamp the record was created

- vehicles
  - vehicle_id (PK)
  - plate_no: unique plate number
  - brand, model, year, color
  - customer_id (FK -> customers.customer_id)

- service_requests
  - request_id (PK)
  - request_date: date the request was made
  - service_type: e.g., "Maintenance", "Repair"
  - problem_note: description of the problem
  - status: current state (default "Pending")
  - priority: e.g., "Low", "Normal", "High"
  - vehicle_id (FK -> vehicles.vehicle_id)

- service_jobs
  - job_id (PK)
  - start_time, end_time: timestamps for job duration
  - labor_charge: labor cost for the job
  - job_status: current job state (default "In Progress")
  - request_id (FK -> service_requests.request_id)

- job_parts_used
  - job_part_id (PK)
  - quantity_used
  - unit_price_at_time: price recorded at the time of use
  - job_id (FK -> service_jobs.job_id)
  - part_id (FK -> inventory.part_id)

- inventory
  - part_id (PK)
  - part_name
  - part_code: unique code for the part
  - brand
  - unit_price
  - quantity_in_stock
  - reorder_level
  - description
  - last_updated

- billing
  - bill_id (PK)
  - bill_date
  - subtotal_labor
  - subtotal_parts
  - tax
  - total_amount
  - payment_status
  - job_id (FK -> service_jobs.job_id)

---

## Example Queries

- Get all service requests for a customer:
```sql
SELECT sr.*
FROM service_requests sr
JOIN vehicles v ON sr.vehicle_id = v.vehicle_id
JOIN customers c ON v.customer_id = c.customer_id
WHERE c.customer_id = 123;
```

- Calculate total cost of a job (labor + parts):
```sql
SELECT sj.job_id,
       sj.labor_charge,
       COALESCE(SUM(jpu.quantity_used * jpu.unit_price_at_time), 0) AS parts_total,
       sj.labor_charge + COALESCE(SUM(jpu.quantity_used * jpu.unit_price_at_time), 0) AS total
FROM service_jobs sj
LEFT JOIN job_parts_used jpu ON jpu.job_id = sj.job_id
WHERE sj.job_id = 456
GROUP BY sj.job_id, sj.labor_charge;
```

- Low stock parts:
```sql
SELECT * FROM inventory
WHERE quantity_in_stock <= reorder_level
ORDER BY quantity_in_stock ASC;
```

---

## Sample Seed Data (small example)

```sql
INSERT INTO customers (customer_id, name, phone, email, address)
VALUES (1, 'Alice Example', '+1234567890', 'alice@example.com', '123 Main St');

INSERT INTO vehicles (vehicle_id, plate_no, brand, model, year, color, customer_id)
VALUES (1, 'ABC-1234', 'Toyota', 'Corolla', 2018, 'Silver', 1);

INSERT INTO service_requests (request_id, service_type, problem_note, vehicle_id)
VALUES (1, 'Oil Change', 'Regular maintenance', 1);

INSERT INTO service_jobs (job_id, start_time, labor_charge, request_id)
VALUES (1, NOW(), 50.00, 1);

INSERT INTO inventory (part_id, part_name, part_code, brand, unit_price, quantity_in_stock, reorder_level)
VALUES (1, 'Oil Filter', 'OF-123', 'FilterCo', 8.50, 25, 5);

INSERT INTO job_parts_used (job_part_id, quantity_used, unit_price_at_time, job_id, part_id)
VALUES (1, 1, 8.50, 1, 1);

INSERT INTO billing (bill_id, subtotal_labor, subtotal_parts, tax, total_amount, job_id)
VALUES (1, 50.00, 8.50, 5.85, 64.35, 1);
```
