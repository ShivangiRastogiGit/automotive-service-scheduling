# Automotive Service Scheduling System

A web-based automotive service scheduling application built with Flask and SQLite for managing customer vehicles and appointments.

**Live Demo**: https://automotive-service-scheduling.onrender.com

## Technology Stack

- **Backend**: Flask 3.0.0, Python 3.12.5, SQLite
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Analytics**: Plotly 5.17.0, Pandas 2.1.1, NumPy 1.26.4
- **Deployment**: Gunicorn 21.2.0, Render
- **Security**: SHA256 password hashing, session management

## Installation

### Local Development
1. Clone repository:
   ```bash
   git clone https://github.com/ThinkerVerse/automotive-service-scheduling
   cd automotive-service-scheduling
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run application:
   ```bash
   python app.py
   ```

4. Access at: `http://127.0.0.1:5001`

### Production Deployment
Application is deployed on Render with Gunicorn WSGI server running on port 10000.

## Default Login
- Email: john.doe@email.com
- Password: password123

## Database Schema

### Core Tables
- **customers**: User accounts (id, first_name, last_name, email, password, phone, address)
- **vehicles**: Customer vehicles (id, customer_id, make, model, year, vin, license_plate)
- **services**: Available services (id, name, description, duration, price)
- **appointments**: Scheduled services (id, customer_id, vehicle_id, service_id, date, time, status)

## Features

### Customer Portal
- Secure registration and login
- Vehicle management (add, edit, view)
- Appointment scheduling and tracking
- Personal dashboard

### Admin Features
- Customer management
- Vehicle oversight
- Appointment management with status updates
- Service catalog management

### Security
- Password hashing with SHA256
- Session-based authentication
- Input validation and sanitization
- SQL injection protection

## CRUD Operations

Complete Create, Read, Update, Delete operations for:
- Customer management (`/customers/*`)
- Vehicle registration (`/vehicles/*`)
- Appointment scheduling (`/appointments/*`)
- Service catalog (`/services`)

## Project Structure

```
automotive-service-scheduling/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_scripts.sql   # SQL CRUD operations
├── automotive_service.db  # SQLite database
└── templates/            # HTML templates
```

## Requirements

```
Flask==3.0.0
numpy==1.26.4
pandas==2.1.1
plotly==5.17.0
Werkzeug>=3.0.0
gunicorn==21.2.0
```