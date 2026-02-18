# AutoIMS - Auto Inventory Management System

A comprehensive web-based application for managing vehicle service operations with integrated inventory, billing, and employee management.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Application Workflow](#application-workflow)

---

## Features

| Module                  | Description                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------- |
| **Customer Management** | Store and manage customer details, contact information, and service history            |
| **Vehicle Tracking**    | Maintain detailed records of customer vehicles with specifications                     |
| **Service Requests**    | Create and track service requests with priority levels and status updates              |
| **Job Management**      | Monitor service jobs with labor charges, employee assignments, and completion tracking |
| **Inventory Control**   | Manage parts inventory with automatic reorder alerts and stock levels                  |
| **Billing System**      | Generate invoices with labor and parts costs, including 18% GST tax calculations       |
| **Employee Management** | Track employees, their roles, ratings, and job assignments                             |
| **Dashboard Analytics** | Real-time statistics for revenue, active jobs, customers, and low stock alerts         |
| **Authentication**      | Secure JWT-based login and signup functionality                                        |

---

## Tech Stack

### Frontend

- **React 19** - UI framework
- **Vite 7** - Build tool and development server
- **Tailwind CSS 4** - Utility-first CSS framework
- **React Router 7** - Client-side routing
- **Lucide React** - Icon library

### Backend

- **Python 3.8+** - Programming language
- **Flask 3.0** - Web framework
- **psycopg3** - PostgreSQL adapter (RAW SQL - no ORM)
- **PyJWT** - JSON Web Token authentication
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Werkzeug** - Password hashing

### Database

- **PostgreSQL 13+** - Relational database
- **Schema**: `vehicle_service`

---

## Project Structure

```
AutoIMS/
├── backend/                    # Python Flask REST API
│   ├── app.py                  # Application entry point
│   ├── config.py               # Database & JWT configuration
│   ├── db_password.txt         # PostgreSQL password (gitignored)
│   ├── requirements.txt        # Python dependencies
│   ├── controllers/            # Business logic layer
│   │   ├── billing.py          # Bill generation, payment processing
│   │   ├── customers.py        # Customer CRUD operations
│   │   ├── employees.py        # Employee management
│   │   ├── inventory.py        # Stock management
│   │   ├── job_parts.py        # Parts used in jobs
│   │   ├── service_jobs.py     # Job tracking
│   │   ├── service_requests.py # Service request handling
│   │   └── vehicles.py         # Vehicle management
│   ├── db/                     # Database utilities
│   │   └── connection.py       # psycopg3 connection manager
│   ├── models/                 # Data models
│   │   └── user.py             # User authentication model
│   ├── routes/                 # API endpoint handlers
│   │   ├── auth.py             # Login/Signup endpoints
│   │   ├── billing.py          # Billing API
│   │   ├── customers.py        # Customers API
│   │   ├── dashboard.py        # Dashboard stats API
│   │   ├── employees.py        # Employees API
│   │   ├── inventory.py        # Inventory API
│   │   ├── job_parts.py        # Job parts API
│   │   ├── service_jobs.py     # Service jobs API
│   │   ├── service_requests.py # Service requests API
│   │   └── vehicles.py         # Vehicles API
│   └── utils/
│       └── jwt_utils.py        # JWT token utilities
├── database/
│   └── schema.sql              # PostgreSQL schema definition
├── frontend/                   # React application
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── index.html              # HTML entry point
│   ├── public/                 # Static assets (logo)
│   └── src/
│       ├── App.jsx             # Main app with routing
│       ├── main.jsx            # React entry point
│       ├── index.css           # Global styles (Tailwind)
│       └── components/
│           ├── Dashboard.jsx   # Main dashboard with stats
│           ├── Login.jsx       # Login page
│           ├── Signup.jsx      # Registration page
│           ├── Navbar.jsx      # Top navigation
│           ├── Sidebar.jsx     # Side navigation
│           ├── Billing.jsx     # Billing management
│           ├── Employee.jsx    # Employee management
│           ├── Inventory.jsx   # Inventory management
│           ├── Service_request.jsx # Service requests
│           ├── Home.jsx        # Landing page
│           └── Footer.jsx      # Footer component
└── README.md                   # This file
```

---

## Database Schema

### Tables Overview

| Table              | Purpose                 | Primary Key   |
| ------------------ | ----------------------- | ------------- |
| `customers`        | Customer information    | `customer_id` |
| `vehicles`         | Customer vehicles       | `vehicle_id`  |
| `employees`        | Staff members           | `id`          |
| `service_requests` | Service request records | `request_id`  |
| `service_jobs`     | Job tracking            | `job_id`      |
| `inventory`        | Spare parts stock       | `part_id`     |
| `job_parts_used`   | Parts used in jobs      | `job_part_id` |
| `billing`          | Invoice records         | `bill_id`     |

### Entity Relationships

```
customers (1) ──────< (N) vehicles
vehicles (1) ──────< (N) service_requests
service_requests (1) ──────< (N) service_jobs
service_jobs (1) ──────< (N) job_parts_used
inventory (1) ──────< (N) job_parts_used
service_jobs (1) ──────── (1) billing
employees (1) ──────< (N) service_jobs
```

---

## Installation

### Prerequisites

- Node.js v18+
- Python 3.8+
- PostgreSQL 13+

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AutoIMS
```

### 2. Database Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE vehicle_service_db;
\q

# Run schema
psql -U postgres -d vehicle_service_db -f database/schema.sql
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure database password
echo "your_postgres_password" > db_password.txt

# Start server
python app.py
```

Backend runs at: `http://localhost:5000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Usage

1. **Sign Up**: Create an employee account
2. **Login**: Authenticate with your credentials
3. **Dashboard**: View real-time statistics
4. **Service Requests**: Create requests for customer vehicles
5. **Inventory**: Use parts for service jobs
6. **Billing**: Generate and manage invoices

---

## API Reference

### Authentication

| Method | Endpoint      | Description            |
| ------ | ------------- | ---------------------- |
| POST   | `/api/signup` | Register new employee  |
| POST   | `/api/login`  | Authenticate & get JWT |
| GET    | `/api/me`     | Get current user info  |

### Dashboard

| Method | Endpoint         | Description              |
| ------ | ---------------- | ------------------------ |
| GET    | `/api/dashboard` | Get dashboard statistics |

### Service Requests

| Method | Endpoint                    | Description        |
| ------ | --------------------------- | ------------------ |
| GET    | `/api/service-requests`     | List all requests  |
| POST   | `/api/service-requests`     | Create new request |
| PUT    | `/api/service-requests/:id` | Update request     |
| DELETE | `/api/service-requests/:id` | Delete request     |

### Inventory

| Method | Endpoint             | Description    |
| ------ | -------------------- | -------------- |
| GET    | `/api/inventory`     | List all parts |
| POST   | `/api/inventory`     | Add new part   |
| PUT    | `/api/inventory/:id` | Update part    |
| DELETE | `/api/inventory/:id` | Delete part    |

### Billing

| Method | Endpoint                        | Description           |
| ------ | ------------------------------- | --------------------- |
| GET    | `/api/billing`                  | List all bills        |
| POST   | `/api/billing/generate/:job_id` | Generate bill for job |
| PUT    | `/api/billing/:id/pay`          | Mark bill as paid     |

### Employees

| Method | Endpoint             | Description        |
| ------ | -------------------- | ------------------ |
| GET    | `/api/employees`     | List all employees |
| POST   | `/api/employees`     | Add new employee   |
| PUT    | `/api/employees/:id` | Update employee    |
| DELETE | `/api/employees/:id` | Delete employee    |

---

## Application Workflow

### Complete Service Flow

```
1. CUSTOMER ARRIVES
   └── Customer brings vehicle for service

2. SERVICE REQUEST CREATED
   ├── Frontend: Service_request.jsx → handleAddRequest()
   ├── Backend: POST /api/service-requests
   ├── Controller: service_requests.create_request()
   ├── SQL: INSERT INTO vehicle_service.service_requests
   └── TRIGGER: Auto-creates service_job with assigned employee

3. PARTS USED FROM INVENTORY
   ├── Frontend: Inventory.jsx → handlePopupSubmit()
   ├── Backend: POST /api/job-parts/use-for-vehicle
   ├── Controller: job_parts.add_part_to_job()
   ├── SQL: INSERT INTO vehicle_service.job_parts_used
   └── SQL: UPDATE vehicle_service.inventory (reduce stock)

4. JOB COMPLETED
   ├── Frontend: Update job status to "Completed"
   ├── Backend: PUT /api/service-jobs/:id
   └── SQL: UPDATE vehicle_service.service_jobs SET job_status='Completed'

5. BILL GENERATED
   ├── Frontend: Billing.jsx → handleCreateInvoice()
   ├── Backend: POST /api/billing/generate/:job_id
   ├── Controller: billing.generate_bill()
   ├── SQL: Calculate labor + parts + 18% GST
   └── SQL: INSERT INTO vehicle_service.billing

6. PAYMENT RECEIVED
   ├── Frontend: Billing.jsx → handleMarkAsPaid()
   ├── Backend: PUT /api/billing/:id/pay
   ├── SQL: UPDATE vehicle_service.billing SET payment_status='Paid', payment_date=CURRENT_TIMESTAMP
   └── Dashboard: Total Revenue updates
```

### Dashboard Data Flow

```
Dashboard.jsx
    │
    ├── useEffect() → fetchDashboard()
    │
    ├── GET /api/dashboard (with JWT token)
    │
    ├── Backend: routes/dashboard.py → get_dashboard()
    │       │
    │       └── get_dashboard_stats()
    │           ├── SELECT COUNT(*) FROM vehicle_service.customers
    │           ├── SELECT COUNT(*) FROM vehicle_service.vehicles
    │           ├── SELECT COUNT(*) FROM vehicle_service.service_jobs WHERE job_status IN ('Pending', 'In Progress')
    │           ├── SELECT COALESCE(SUM(total_amount), 0) FROM vehicle_service.billing WHERE payment_status='Paid'
    │           ├── SELECT COALESCE(SUM(total_amount), 0) FROM vehicle_service.billing WHERE payment_status='Unpaid'
    │           └── SELECT TOP 3 employees by rating
    │
    └── setStats(response.stats) → UI updates
```

### Authentication Flow

```
1. User submits login form
2. POST /api/login with {username, password}
3. Backend validates credentials against vehicle_service.employees
4. If valid: Generate JWT token with employee_id
5. Return token to frontend
6. Frontend stores token in localStorage
7. All subsequent API calls include: Authorization: Bearer <token>
8. @token_required decorator validates token on protected routes
```

---

## Environment Variables

| Variable         | Description            | Default            |
| ---------------- | ---------------------- | ------------------ |
| `DB_HOST`        | PostgreSQL host        | localhost          |
| `DB_PORT`        | PostgreSQL port        | 5432               |
| `DB_NAME`        | Database name          | vehicle_service_db |
| `DB_USER`        | Database user          | postgres           |
| `JWT_SECRET_KEY` | Secret for JWT signing | (in config.py)     |

---

## License

This project is for educational purposes.

---

## Contributors

- AutoIMS Development Team

| Method | Endpoint      | Description       |
| ------ | ------------- | ----------------- |
| GET    | `/api/health` | API health status |

## Environment Variables

| Variable         | Description                  | Default                    |
| ---------------- | ---------------------------- | -------------------------- |
| `DATABASE_URL`   | PostgreSQL connection string | `postgresql+psycopg://...` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens    | (set in config.py)         |
| `SECRET_KEY`     | Flask application secret key | (set in config.py)         |

## Development

### Running Both Servers

For development, you need to run both the frontend and backend servers:

**Terminal 1 - Backend:**

```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend:**

```bash
cd frontend
npm run build
```

The production build will be in the `frontend/dist` directory.

## License

This project is for educational purposes.
