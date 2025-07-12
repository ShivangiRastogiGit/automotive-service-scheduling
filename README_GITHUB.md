# Automotive Service Scheduling System

A comprehensive web-based automotive service scheduling system built with Flask and SQLite.

## Features
- Customer management and registration
- Vehicle tracking and management
- Service catalog and pricing
- Appointment scheduling system
- Admin dashboard with analytics
- Responsive web interface

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Charts**: Plotly.js
- **Authentication**: Flask-Login with password hashing

## Installation
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`

## Database Schema
The system uses a normalized SQLite database with 4 main tables:
- **customers**: Customer information and authentication
- **vehicles**: Vehicle details linked to customers
- **services**: Available automotive services catalog
- **appointments**: Scheduling system linking customers, vehicles, and services

## Usage
1. Access the application at http://localhost:5000
2. Register as a new customer or login with existing credentials
3. Add vehicles to your account
4. Schedule appointments for various services
5. Admin can access analytics dashboard at /admin

## Author
**Shivangi Rastogi**
- Database Design & Implementation
- Full-stack Web Development
- UI/UX Design

## License
This project is for educational purposes.

