# AutoIMS - Auto Inventory Management System

## Complete Project Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Database Schema](#4-database-schema)
5. [Backend Implementation](#5-backend-implementation)
6. [Frontend Implementation](#6-frontend-implementation)
7. [API Endpoints Reference](#7-api-endpoints-reference)
8. [Installation & Setup](#8-installation--setup)
9. [Current Implementation Status](#9-current-implementation-status)

---

## 1. Project Overview

### 1.1 Project Title

**AutoIMS - Auto Inventory Management System**

### 1.2 Project Description

AutoIMS is a comprehensive web-based application designed for managing vehicle service operations. It provides an integrated system for handling customer information, vehicle details, service requests, inventory management, job tracking, billing, and employee management.

### 1.3 Key Features

- **Customer Management**: Store and manage customer details including contact information and service history
- **Vehicle Tracking**: Maintain detailed records of customer vehicles with specifications
- **Service Requests**: Create and track service requests with priority levels and status updates
- **Job Management**: Monitor service jobs with labor charges and completion tracking
- **Inventory Control**: Manage parts inventory with automatic reorder alerts and stock levels
- **Billing System**: Generate invoices with labor and parts costs, including tax calculations
- **Employee Management**: Track employees, their roles, ratings, and job assignments
- **User Authentication**: Secure JWT-based login and signup functionality
- **Responsive UI**: Modern, mobile-friendly interface built with React

---

## 2. Technology Stack

### 2.1 Frontend Technologies

| Technology       | Version  | Purpose                   |
| ---------------- | -------- | ------------------------- |
| React            | ^19.2.0  | Core UI framework         |
| React Router DOM | ^7.12.0  | Client-side routing       |
| Tailwind CSS     | ^4.1.18  | CSS framework for styling |
| Lucide React     | ^0.563.0 | Icon library              |
| Vite             | ^7.2.4   | Build tool                |
| ESLint           | ^9.39.1  | Linting utility           |

### 2.2 Backend Technologies

| Technology | Version | Purpose                      |
| ---------- | ------- | ---------------------------- |
| Python     | 3.8+    | Programming language         |
| Flask      | 3.0.0   | Web framework for REST API   |
| Werkzeug   | 3.0.1   | Password hashing             |
| psycopg    | >=3.1.0 | PostgreSQL adapter (raw SQL) |
| PyJWT      | 2.8.0   | JWT authentication           |
| Flask-CORS | 4.0.0   | CORS support                 |

### 2.3 Database

| Technology | Version | Purpose             |
| ---------- | ------- | ------------------- |
| PostgreSQL | 13+     | Relational database |

---

## 3. Project Structure

### 3.1 Directory Overview

| Directory                  | Description                     |
| -------------------------- | ------------------------------- |
| `backend/`                 | Python Flask REST API server    |
| `backend/controllers/`     | Business logic for each feature |
| `backend/db/`              | Database connection utilities   |
| `backend/models/`          | User model with authentication  |
| `backend/routes/`          | API endpoint handlers           |
| `backend/utils/`           | JWT token utilities             |
| `database/`                | SQL schema file                 |
| `frontend/`                | React application               |
| `frontend/src/components/` | React UI components             |
| `frontend/public/`         | Static assets (logo)            |

### 3.2 Key Files

| File                       | Purpose                                                   |
| -------------------------- | --------------------------------------------------------- |
| `backend/app.py`           | Flask application entry point with blueprint registration |
| `backend/config.py`        | Database and JWT configuration settings                   |
| `backend/requirements.txt` | Python dependencies list                                  |
| `database/schema.sql`      | PostgreSQL table definitions                              |
| `frontend/src/App.jsx`     | Main React component with routing                         |
| `frontend/package.json`    | Frontend dependencies                                     |
| `frontend/vite.config.js`  | Vite build configuration                                  |

---

## 4. Database Schema

### 4.1 Database Information

- **Database Name**: vehicle_service_db
- **Schema Name**: vehicle_service
- **Database Type**: PostgreSQL

### 4.2 Tables Summary

| Table              | Purpose                 | Key Columns                                                                               |
| ------------------ | ----------------------- | ----------------------------------------------------------------------------------------- |
| `customers`        | Customer information    | customer_id, name, phone, email, address                                                  |
| `vehicles`         | Vehicle details         | vehicle_id, plate_no, brand, model, year, customer_id (FK)                                |
| `service_requests` | Service request records | request_id, service_type, problem_note, status, priority, vehicle_id (FK)                 |
| `service_jobs`     | Job tracking            | job_id, start_time, end_time, labor_charge, job_status, request_id (FK), employee_id (FK) |
| `inventory`        | Spare parts stock       | part_id, part_name, part_code, unit_price, quantity_in_stock, reorder_level               |
| `job_parts_used`   | Parts used in jobs      | job_part_id, quantity_used, unit_price_at_time, job_id (FK), part_id (FK)                 |
| `billing`          | Billing records         | bill_id, subtotal_labor, subtotal_parts, tax, total_amount, payment_status, job_id (FK)   |
| `employees`        | Employee management     | id, name, position, salary                                                                |
| `users`            | User authentication     | user_id, name, username, email, password_hash                                             |

### 4.3 Entity Relationships

- One customer can have multiple vehicles
- One vehicle can have multiple service requests
- One service request can have multiple service jobs
- One service job can use multiple parts (job_parts_used)
- One service job has one billing record
- One employee can be assigned to multiple jobs
- One inventory part can be used in multiple jobs

---

## 5. Backend Implementation

### 5.1 Application Architecture

The backend follows a layered architecture:

- **Routes Layer**: API endpoints that receive HTTP requests
- **Controllers Layer**: Business logic and data processing
- **Models Layer**: Data access and database operations
- **Database Layer**: PostgreSQL connection management

### 5.2 Main Application (app.py)

Uses Flask application factory pattern with:

- CORS enabled for frontend at localhost:5173
- 7 registered blueprints for different features
- Health check endpoint at `/api/health`
- Error handlers for 404 and 500

### 5.3 Configuration (config.py)

Manages:

- Database connection settings (host, port, database name, user, password)
- Schema name: vehicle_service
- JWT secret key and token expiration (12 hours)
- Password read from db_password.txt file

### 5.4 Database Connection Module (db/connection.py)

Provides:

- Context manager for database connections with auto-commit/rollback
- Dictionary cursor support for row-to-dict conversion
- Helper functions for executing queries with RETURNING clause
- Uses psycopg3 (modern PostgreSQL adapter)

### 5.5 User Model (models/user.py)

Handles:

- Password hashing using Werkzeug
- User creation with hashed passwords
- User lookup by email, username, or ID
- Password verification
- Safe user dictionary conversion (excludes password)

### 5.6 JWT Utilities (utils/jwt_utils.py)

Provides:

- Token generation with user_id payload
- Token decoding and validation
- `@token_required` decorator for protecting routes
- 12-hour token expiration using HS256 algorithm

### 5.7 Routes Implementation

#### Authentication Routes (routes/auth.py) - Prefix: `/api`

- **POST /signup**: User registration with validation, password hashing, returns JWT
- **POST /login**: Email/password authentication, returns JWT
- **GET /me**: Returns current user info (protected)

#### Dashboard Routes (routes/dashboard.py) - Prefix: `/api`

- **GET /dashboard**: Dashboard statistics (counts, revenue, pending items)
- **GET /dashboard/customers**: All customers list
- **GET /dashboard/vehicles**: All vehicles with customer info
- **GET /dashboard/service-requests**: All service requests with vehicle info
- **GET /dashboard/service-jobs**: All jobs with employee info
- **GET /dashboard/inventory**: All inventory items
- **GET /dashboard/billing**: All billing records

#### Employee Routes (routes/employees.py) - Prefix: `/api/employees`

- **GET /**: List all employees (optional include inactive)
- **GET /:id**: Single employee details
- **POST /**: Create new employee
- **PUT /:id**: Update employee
- **DELETE /:id**: Soft delete (sets status to Inactive)

#### Service Jobs Routes (routes/service_jobs.py) - Prefix: `/api/jobs`

- **GET /**: List all jobs (optional status filter)
- **GET /:id**: Job details with employee and vehicle info
- **POST /**: Create new job from service request
- **PUT /:id/assign**: Assign employee to job
- **PUT /:id/status**: Update job status (In Progress/Completed)
- **PUT /:id/labor**: Update labor charge

#### Inventory Routes (routes/inventory.py) - Prefix: `/api/inventory`

- **GET /**: List all inventory items
- **GET /low-stock**: Items at or below reorder level
- **GET /:id**: Single item details
- **POST /**: Add new inventory item
- **PUT /:id**: Update item details
- **PUT /:id/stock**: Update stock quantity (add/subtract or set)

#### Job Parts Routes (routes/job_parts.py) - Prefix: `/api/job-parts`

- **GET /job/:id**: Parts used in specific job
- **POST /**: Add part to job (auto-deducts from inventory)
- **DELETE /:id**: Remove part from job (restores inventory)
- **GET /job/:id/total**: Calculate total parts cost for job

#### Billing Routes (routes/billing.py) - Prefix: `/api/billing`

- **GET /**: List all bills with customer info
- **GET /:id**: Single bill details
- **GET /job/:id**: Bill for specific job with parts breakdown
- **POST /generate**: Generate bill (calculates labor + parts + tax)
- **PUT /:id/pay**: Mark bill as paid
- **PUT /:id**: Update bill amounts

### 5.8 Controllers Implementation

#### Employees Controller (controllers/employees.py)

- Get all/active employees
- CRUD operations for employees
- Soft delete by setting status to Inactive

#### Inventory Controller (controllers/inventory.py)

- Stock management (add, subtract, set quantity)
- Low stock detection
- Part existence validation
- Stock availability checking

#### Service Jobs Controller (controllers/service_jobs.py)

- Job creation with auto start time
- Employee assignment
- Status updates with auto end time on completion
- Jobs filtering by status

#### Job Parts Controller (controllers/job_parts.py)

- Transaction-based part addition (ensures inventory update)
- Captures unit price at time of use
- Automatic inventory deduction
- Inventory restoration on part removal

#### Billing Controller (controllers/billing.py)

- Automatic bill calculation: Labor + Parts + Tax (18% default)
- Prevents duplicate bills for same job
- Payment status management

---

## 6. Frontend Implementation

### 6.1 Application Structure

Uses React with Vite build tool. Main entry point renders App component which handles all routing.

### 6.2 Layouts

| Layout        | Description                                |
| ------------- | ------------------------------------------ |
| PublicLayout  | Navbar + Footer wrapper for public pages   |
| SidebarLayout | Sidebar navigation for authenticated pages |

### 6.3 Routing

| Path                        | Component       | Layout  | Description          |
| --------------------------- | --------------- | ------- | -------------------- |
| `/`                         | Home            | Public  | Landing page         |
| `/signup`                   | Signup          | Public  | Registration         |
| `/login`                    | Login           | Public  | Authentication       |
| `/sidebar/dashboard`        | Dashboard       | Sidebar | Main dashboard       |
| `/sidebar/employees`        | Employee        | Sidebar | Employee management  |
| `/sidebar/service_requests` | Service_request | Sidebar | Service requests     |
| `/sidebar/inventory`        | Inventory       | Sidebar | Inventory management |
| `/sidebar/billing`          | Billing         | Sidebar | Billing management   |

### 6.4 Components Overview

#### Navigation Components

| Component   | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| Navbar.jsx  | Top navigation with logo, Overview link, Login/Signup links        |
| Footer.jsx  | Footer with Help, Privacy Policy, Terms links                      |
| Sidebar.jsx | Collapsible sidebar with navigation icons, user menu, logout popup |

#### Public Pages

| Component  | Description                                            |
| ---------- | ------------------------------------------------------ |
| Home.jsx   | Landing page with hero section and "Get Started" CTA   |
| Login.jsx  | Email/password login form with forgot password link    |
| Signup.jsx | Registration form with name, username, email, password |

#### Dashboard Components

| Component     | Description                                                                                                                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Dashboard.jsx | Statistics cards (revenue, low stock, active jobs), key metrics (customers, vehicles, pending requests, unpaid bills), top employees section, recent activity feed, system status, quick actions |

#### Management Components

| Component           | Description                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| Employee.jsx        | Employee table with search, add/edit/delete popups, ranked employees sidebar showing top performers |
| Service_request.jsx | Service requests table with search, add/edit/delete, multi-employee assignment with chips           |
| Inventory.jsx       | Grid of inventory cards with images, add/edit/use popups, quantity tracking                         |
| Billing.jsx         | Customer billing list with status indicators, invoice generation with print preview                 |

### 6.5 Component Features

#### Dashboard Features

- Total revenue display
- Low stock items count with alert
- Active jobs counter
- Customer and vehicle counts
- Pending requests indicator
- Unpaid bills total
- Top 3 employees with ratings
- Recent activity timeline
- Database connection status
- Quick action buttons

#### Employee Management Features

- Searchable employee table
- Working status badges (Working/Not Working)
- Multiple vehicle ID assignment
- Rating display
- Add employee popup form
- Edit employee popup
- Delete with confirmation
- Ranked employees sidebar sorted by rating

#### Service Request Features

- Customer and vehicle info display
- Multi-employee assignment with searchable dropdown
- Assigned employees shown as chips
- Problem description and assignment tracking
- CRUD operations with popups

#### Inventory Features

- Grid layout with item images
- Price and quantity display
- Search by name or model
- Add item form with image upload
- Edit item popup
- "Use Item" popup for recording usage (customer/vehicle/quantity)
- Choice popup (Edit or Use)

#### Billing Features

- Customer list with amount and status
- Vehicle status indicator (Completed/In Progress/Not Started)
- Payment status (Paid/Unpaid)
- Invoice print preview in new window
- Random invoice number generation
- Itemized charges display

---

## 7. API Endpoints Reference

### 7.1 Authentication Endpoints

| Method | Endpoint    | Description       | Auth |
| ------ | ----------- | ----------------- | ---- |
| POST   | /api/signup | Register new user | No   |
| POST   | /api/login  | Login and get JWT | No   |
| GET    | /api/me     | Get current user  | Yes  |

### 7.2 Dashboard Endpoints

| Method | Endpoint                        | Description          |
| ------ | ------------------------------- | -------------------- |
| GET    | /api/dashboard                  | Dashboard statistics |
| GET    | /api/dashboard/customers        | All customers        |
| GET    | /api/dashboard/vehicles         | All vehicles         |
| GET    | /api/dashboard/service-requests | All service requests |
| GET    | /api/dashboard/service-jobs     | All service jobs     |
| GET    | /api/dashboard/inventory        | All inventory        |
| GET    | /api/dashboard/billing          | All bills            |

### 7.3 Employee Endpoints

| Method | Endpoint           | Description     |
| ------ | ------------------ | --------------- |
| GET    | /api/employees     | List employees  |
| GET    | /api/employees/:id | Get employee    |
| POST   | /api/employees     | Create employee |
| PUT    | /api/employees/:id | Update employee |
| DELETE | /api/employees/:id | Soft delete     |

### 7.4 Service Jobs Endpoints

| Method | Endpoint             | Description         |
| ------ | -------------------- | ------------------- |
| GET    | /api/jobs            | List jobs           |
| GET    | /api/jobs/:id        | Get job details     |
| POST   | /api/jobs            | Create job          |
| PUT    | /api/jobs/:id/assign | Assign employee     |
| PUT    | /api/jobs/:id/status | Update status       |
| PUT    | /api/jobs/:id/labor  | Update labor charge |

### 7.5 Inventory Endpoints

| Method | Endpoint                 | Description     |
| ------ | ------------------------ | --------------- |
| GET    | /api/inventory           | List items      |
| GET    | /api/inventory/low-stock | Low stock items |
| GET    | /api/inventory/:id       | Get item        |
| POST   | /api/inventory           | Add item        |
| PUT    | /api/inventory/:id       | Update item     |
| PUT    | /api/inventory/:id/stock | Update stock    |

### 7.6 Job Parts Endpoints

| Method | Endpoint                     | Description      |
| ------ | ---------------------------- | ---------------- |
| GET    | /api/job-parts/job/:id       | Parts for job    |
| POST   | /api/job-parts               | Add part to job  |
| DELETE | /api/job-parts/:id           | Remove part      |
| GET    | /api/job-parts/job/:id/total | Parts total cost |

### 7.7 Billing Endpoints

| Method | Endpoint              | Description   |
| ------ | --------------------- | ------------- |
| GET    | /api/billing          | List bills    |
| GET    | /api/billing/:id      | Get bill      |
| GET    | /api/billing/job/:id  | Bill by job   |
| POST   | /api/billing/generate | Generate bill |
| PUT    | /api/billing/:id/pay  | Mark as paid  |
| PUT    | /api/billing/:id      | Update bill   |

### 7.8 Utility Endpoints

| Method | Endpoint    | Description  |
| ------ | ----------- | ------------ |
| GET    | /api/health | Health check |
| GET    | /           | API info     |

---

## 8. Installation & Setup

### 8.1 Prerequisites

| Requirement | Version |
| ----------- | ------- |
| Node.js     | v18+    |
| npm         | v9+     |
| Python      | v3.8+   |
| PostgreSQL  | v13+    |

### 8.2 Database Setup

1. Install PostgreSQL
2. Create database named `vehicle_service_db`
3. Run `database/schema.sql` to create tables

### 8.3 Backend Setup

1. Navigate to `backend/` directory
2. Create Python virtual environment
3. Activate virtual environment
4. Install dependencies from `requirements.txt`
5. Configure database password in `db_password.txt`
6. Run `python app.py`
7. Server starts at `http://localhost:5000`

### 8.4 Frontend Setup

1. Navigate to `frontend/` directory
2. Run `npm install`
3. Run `npm run dev`
4. Server starts at `http://localhost:5173`

---

## 9. Current Implementation Status

### 9.1 Backend Status ✅ COMPLETE

| Component            | Status      |
| -------------------- | ----------- |
| Application Factory  | ✅ Complete |
| Database Connection  | ✅ Complete |
| Database Integration | ✅ Complete |
| User Authentication  | ✅ Complete |
| Dashboard API        | ✅ Complete |
| Employee API         | ✅ Complete |
| Service Jobs API     | ✅ Complete |
| Inventory API        | ✅ Complete |
| Job Parts API        | ✅ Complete |
| Billing API          | ✅ Complete |
| Customers API        | ✅ Complete |
| Vehicles API         | ✅ Complete |
| Service Requests API | ✅ Complete |
| Error Handling       | ✅ Complete |
| CORS Configuration   | ✅ Complete |

### 9.2 Frontend Status ⚠️ PARTIAL

| Component            | Status      | Notes                     |
| -------------------- | ----------- | ------------------------- |
| Routing Setup        | ✅ Complete | All routes configured     |
| Landing Page         | ✅ Complete | Home with CTA             |
| Navigation           | ✅ Complete | Navbar and Sidebar        |
| Login Page           | ⚠️ Partial  | UI done, simulated auth   |
| Signup Page          | ⚠️ Partial  | UI done, no backend call  |
| Dashboard            | ⚠️ Partial  | UI done, static data      |
| Employee Management  | ⚠️ Partial  | UI done, local state only |
| Service Requests     | ⚠️ Partial  | UI done, local state only |
| Inventory            | ⚠️ Partial  | UI done, local state only |
| Billing              | ⚠️ Partial  | UI done, local state only |
| **API Integration**  | ❌ Not Done | No fetch calls to backend |
| **State Management** | ❌ Not Done | No Context/Redux          |
| **Protected Routes** | ❌ Not Done | No route guards           |

### 9.3 What's Complete

**Backend:**

- Full REST API with all CRUD operations
- JWT authentication system
- Database connection with psycopg3 using dictionary cursor for clean data access
- All 10 route modules implemented (auth, dashboard, employees, service_jobs, inventory, job_parts, billing, customers, vehicles, service_requests)
- All controller modules implemented with proper database persistence
- Data is properly saved to PostgreSQL database and persists across server restarts
- Error handling and validation
- CORS ready for frontend

**Frontend:**

- Complete UI for all pages
- Responsive design with Tailwind CSS
- Navigation and layout components
- All form popups and modals
- Search and filter functionality
- Print invoice feature

### 9.4 What's Needed

**Frontend Integration Required:**

1. Replace simulated login/signup with actual API calls
2. Fetch dashboard data from `/api/dashboard`
3. Connect Employee component to `/api/employees`
4. Connect Inventory to `/api/inventory`
5. Connect Billing to `/api/billing`
6. Add proper JWT token storage and management
7. Implement protected routes (redirect if not authenticated)
8. Add loading states and error handling

### 9.5 Recent Bug Fixes (February 17, 2026)

**Database Integration Fix:**

- Fixed dictionary cursor access pattern in all controller modules
- Controllers were incorrectly using index-based access on dictionary results
- Updated employees, job_parts, service_requests, vehicles, and customers controllers
- All CRUD operations now properly persist data to the PostgreSQL database

---

## Document Information

| Field                     | Value             |
| ------------------------- | ----------------- |
| Document Version          | 1.1               |
| Last Updated              | February 17, 2026 |
| Total Backend Routes      | 40+ endpoints     |
| Total Frontend Components | 11 components     |
| Database Tables           | 9 tables          |
