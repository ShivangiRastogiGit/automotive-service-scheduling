# 🚗 Automotive Service Scheduling System

A comprehensive web-based automotive service scheduling application built with Flask, SQLite, and modern web technologies. This system allows customers to manage their vehicles and appointments while providing administrators with powerful tools for business management and analytics.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Admin Features](#admin-features)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔐 Customer Portal
- **User Authentication**
  - Secure registration and login system
  - Password hashing with SHA256
  - Session management
  - Profile management

- **Vehicle Management**
  - Add multiple vehicles per customer
  - Edit vehicle details (make, model, year, VIN, license plate, color, mileage)
  - View vehicle history
  - Delete vehicles

- **Appointment Scheduling**
  - Book appointments for registered vehicles
  - Select from available services
  - Choose appointment date and time
  - Add special notes/requests
  - View appointment history
  - Cancel or reschedule appointments
  - Track appointment status (scheduled, in-progress, completed, cancelled)

- **Dashboard**
  - Personal dashboard with overview
  - Upcoming appointments
  - Quick access to vehicles and services
  - Profile information

### 👨‍💼 Admin Portal
- **Admin Authentication**
  - Secure admin login system
  - Session-based access control
  - Admin-only routes protection

- **Customer Management**
  - View all customers
  - Customer statistics (vehicles, appointments)
  - Delete customers and related data
  - Customer search and filtering

- **Vehicle Management**
  - View all vehicles in system
  - Vehicle ownership tracking
  - Delete vehicles and related appointments
  - Vehicle statistics

- **Appointment Management**
  - View all appointments
  - Appointment details with customer/vehicle info
  - Filter by status and date
  - Appointment analytics

- **Service Management**
  - View all services
  - Service popularity tracking
  - Revenue analysis per service
  - Service status management

- **Analytics Dashboard**
  - Interactive charts powered by Plotly
  - Service popularity analysis
  - Vehicle brand distribution
  - Clean, responsive visualizations

### 📊 Analytics & Reporting
- **Business Intelligence**
  - Service popularity charts
  - Customer vehicle brand distribution
  - Real-time data visualization
  - Interactive charts with no toolbar clutter

- **Data Management**
  - SQLite database with proper relationships
  - Data integrity with foreign keys
  - Efficient queries for analytics
  - Sample data for testing

## 🛠 Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Lightweight database
- **Python 3.7+** - Programming language

### Frontend
- **HTML5** - Markup language
- **Bootstrap 5** - CSS framework
- **JavaScript** - Client-side scripting
- **Jinja2** - Template engine

### Analytics
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **JSON** - Data exchange

### Security
- **SHA256** - Password hashing
- **Session Management** - User authentication
- **CSRF Protection** - Form security

## � Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd "Automotive Service Scheduling"
```

### Step 2: Install Dependencies
```bash
pip install flask sqlite3 hashlib plotly pandas
```

### Step 3: Set Up Database
```bash
python setup.py
```

This will create the SQLite database with:
- Database schema (customers, vehicles, appointments, services)
- Sample data for testing
- Proper relationships and constraints

### Step 4: Verify Installation
```bash
python -c "import plotly, pandas; print('✅ All dependencies installed successfully')"
```

## 🗄 Database Setup

The application uses SQLite with the following tables:

### Tables Structure
- **customers** - User accounts and profiles
- **vehicles** - Customer vehicles information
- **appointments** - Scheduled service appointments
- **services** - Available automotive services

### Sample Data
The setup script loads comprehensive sample data:
- 1000+ customers from CSV dataset
- 28,000+ vehicles from USA cars dataset
- Various automotive services with pricing
- Sample appointments for testing

## 🚀 Running the Application

### Start the Server
```bash
python app.py
```

The application will be available at: **http://127.0.0.1:5005**

### Default Login Credentials

**Admin Access:**
- Username: `admin`
- Password: `admin123`

**Customer Access:**
- Any customer from the sample data
- Default password: `123456`

## 📱 Usage

### For Customers
1. **Register/Login** - Create account or login with existing credentials
2. **Add Vehicles** - Register your vehicles in the system
3. **Book Appointments** - Schedule service appointments
4. **Manage Profile** - Update personal information
5. **Track Appointments** - Monitor appointment status

### For Administrators
1. **Admin Login** - Access admin portal
2. **Dashboard** - View business overview
3. **Manage Data** - Handle customers, vehicles, appointments
4. **Analytics** - View business insights and charts
5. **Service Management** - Manage available services

## 🔧 Admin Features

### Dashboard
- Business statistics overview
- Recent appointments
- Quick access to all modules
- System health indicators

### Customer Management
- Complete customer database
- Vehicle and appointment counts
- Customer activity tracking
- Data export capabilities

### Analytics
- **Service Popularity Chart** - Bar chart showing most requested services
- **Vehicle Brand Distribution** - Pie chart of customer vehicle makes
- Interactive visualizations with Plotly
- Real-time data updates

## 🔗 API Endpoints

### Customer Routes
- `GET /` - Home page
- `GET /login` - Customer login
- `POST /register` - Customer registration
- `GET /dashboard` - Customer dashboard
- `GET /my-vehicles` - Customer vehicles
- `GET /my-appointments` - Customer appointments

### Admin Routes
- `GET /admin/login` - Admin login
- `GET /admin` - Admin dashboard
- `GET /admin/customers` - Customer management
- `GET /admin/vehicles` - Vehicle management
- `GET /admin/appointments` - Appointment management
- `GET /admin/analytics` - Analytics dashboard

### API Endpoints
- `GET /api/my-vehicles` - Customer vehicles (JSON)
- `GET /admin/api/chart-data` - Analytics data (JSON)

## 📁 Project Structure

```
Automotive Service Scheduling/
├── app.py                 # Main Flask application
├── setup.py              # Database setup script
├── automotive_service.db  # SQLite database
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── admin_analytics.html
│   └── ...
│
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
└── Data/               # Sample data files
    ├── customers_DataSet.csv
    ├── USA_cars_datasets.csv
    └── Service_Type.csv
```

## 🔒 Security Features

- **Password Hashing** - All passwords are hashed with SHA256
- **Session Management** - Secure session handling
- **Access Control** - Role-based access (customer/admin)
- **Input Validation** - Form validation and sanitization
- **SQL Injection Protection** - Parameterized queries
- **CSRF Protection** - Built-in Flask security

## 🎨 UI/UX Features

- **Responsive Design** - Mobile-friendly interface
- **Modern Bootstrap UI** - Clean, professional appearance
- **Interactive Charts** - Plotly-powered visualizations
- **Flash Messages** - User feedback system
- **Intuitive Navigation** - Easy-to-use interface
- **Clean Analytics** - No toolbar clutter on charts

## 📊 Analytics Features

### Service Popularity Chart
- Bar chart showing most requested services
- Real-time data from appointments
- Color-coded for easy reading
- Responsive design

### Vehicle Brand Distribution
- Pie chart of customer vehicle makes
- Shows market share by brand
- Interactive hover effects
- Clean, professional styling

## 🔧 Configuration

### Database Configuration
- SQLite database file: `automotive_service.db`
- Connection pooling enabled
- Foreign key constraints enforced

### Flask Configuration
- Debug mode enabled for development
- Secret key for session security
- Host: 127.0.0.1 (localhost)
- Port: 5005

## 🚨 Troubleshooting

### Common Issues

**Database not found:**
```bash
python setup.py
```

**Charts not displaying:**
```bash
pip install plotly pandas
```

**Port already in use:**
- Change port in `app.py` (line with `app.run()`)
- Or kill existing process: `lsof -i :5005`

**Permission errors:**
- Ensure write permissions in project directory
- Check SQLite file permissions

## 📈 Future Enhancements

- Email notifications for appointments
- SMS reminders
- Payment integration
- Service technician assignment
- Inventory management
- Customer feedback system
- Mobile app development
- Advanced reporting features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions:
- Check the troubleshooting section
- Review the code documentation
- Create an issue in the repository

---

**Made with ❤️ for automotive service businesses**

*This application provides a complete solution for managing automotive service scheduling with modern web technologies and user-friendly interfaces.*
Automotive Service Scheduling/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_scripts.sql   # Complete SQL CRUD operations
├── automotive_service.db  # SQLite database (created automatically)
└── templates/            # HTML templates
    ├── base.html         # Base template with navigation
    ├── index.html        # Dashboard/home page
    ├── customers.html    # Customer list
    ├── add_customer.html # Add customer form
    ├── edit_customer.html# Edit customer form
    ├── view_customer.html# Customer details view
    ├── vehicles.html     # Vehicle list
    ├── add_vehicle.html  # Add vehicle form
    ├── appointments.html # Appointment list
    ├── add_appointment.html # Schedule appointment form
    └── services.html     # Service catalog
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd "/Users/shivangirastogi/Automotive Service Scheduling"
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your web browser and go to: `http://127.0.0.1:5001` (or `http://127.0.0.1:5000` if port 5000 is available)

5. **Login with demo account:**
   - Email: john.doe@email.com
   - Password: password123

### Security Features
- **Password Hashing**: Secure SHA256 password hashing
- **Session Management**: Flask session-based authentication
- **Data Isolation**: Customers can only access their own data
- **Route Protection**: Protected routes require authentication
- **Input Validation**: Comprehensive form validation and sanitization

### User Roles
- **Customer**: Can manage their own vehicles and appointments only
- **Public**: Can view services and register for an account

### Protected Routes
All customer-specific routes require authentication:
- `/dashboard` - Personal dashboard
- `/my-vehicles` - Customer's vehicles only  
- `/my-appointments` - Customer's appointments only
- `/profile` - Account management

## 💾 Database Schema

### Customers Table
- `id` (Primary Key)
- `first_name` (Required)
- `last_name` (Required)
- `email` (Required, Unique)
- `password` (Required, Hashed with SHA256)
- `phone` (Required)
- `address` (Optional)
- `created_at` (Timestamp)

### Vehicles Table
- `id` (Primary Key)
- `customer_id` (Foreign Key → customers.id)
- `make` (Required)
- `model` (Required)
- `year` (Required)
- `vin` (Optional, Unique)
- `license_plate` (Optional)
- `color` (Optional)
- `mileage` (Optional)
- `created_at` (Timestamp)

### Services Table
- `id` (Primary Key)
- `name` (Required)
- `description` (Optional)
- `estimated_duration` (Required, in minutes)
- `price` (Required, Decimal)
- `is_active` (Boolean, default True)

### Appointments Table
- `id` (Primary Key)
- `customer_id` (Foreign Key → customers.id)
- `vehicle_id` (Foreign Key → vehicles.id)
- `service_id` (Foreign Key → services.id)
- `appointment_date` (Required)
- `appointment_time` (Required)
- `status` (Default: 'scheduled')
- `notes` (Optional)
- `created_at` (Timestamp)

## CRUD Operations

The application implements full CRUD (Create, Read, Update, Delete) operations for all entities:

### Customer CRUD
- **Create**: `/customers/add` - Add new customer
- **Read**: `/customers` - List all customers, `/customers/<id>` - View customer details
- **Update**: `/customers/<id>/edit` - Edit customer information
- **Delete**: `/customers/<id>/delete` - Delete customer (with validation)

### Vehicle CRUD
- **Create**: `/vehicles/add` - Register new vehicle
- **Read**: `/vehicles` - List all vehicles
- **Update**: Via edit forms (can be extended)
- **Delete**: Via customer management (can be extended)

### Appointment CRUD
- **Create**: `/appointments/add` - Schedule new appointment
- **Read**: `/appointments` - List all appointments
- **Update**: Status updates via dropdown on appointments page
- **Delete**: Status change to 'cancelled' (soft delete)

### Service Management
- **Read**: `/services` - View service catalog
- Services are pre-loaded during database initialization

## SQL Operations

The `database_scripts.sql` file contains comprehensive SQL operations including:

- Database schema creation
- Sample data insertion
- Complete CRUD operations for all tables
- Advanced reporting queries
- Performance optimization indexes
- Data maintenance queries

## Key Features

### Dashboard
- Overview statistics (total customers, appointments)
- Recent appointments display
- Quick action buttons for common tasks

### Customer Management
- Complete customer profiles
- Vehicle history per customer
- Appointment history per customer
- Search and filter capabilities

### Appointment Scheduling
- Dynamic vehicle loading based on selected customer
- Service selection with pricing information
- Status management (scheduled, in-progress, completed, cancelled)
- Date/time validation

### Responsive Design
- Mobile-friendly interface using Bootstrap
- Intuitive navigation
- Modern UI with icons and consistent styling

## Usage Examples

### Adding a New Customer
1. Navigate to Customers → Add Customer
2. Fill in required fields (name, email, phone)
3. Optionally add address
4. Submit form

### Scheduling an Appointment
1. Navigate to Appointments → Schedule Appointment
2. Select customer (vehicles load automatically)
3. Choose vehicle and service
4. Select date and time
5. Add any notes
6. Submit form

### Managing Appointment Status
1. Go to Appointments page
2. Use the status dropdown for each appointment
3. Status automatically updates on selection

## Sample Data

The application comes pre-loaded with sample services:
- Oil Change ($49.99, 30 min)
- Brake Inspection ($75.00, 45 min)
- Tire Rotation ($35.00, 30 min)
- Battery Test ($25.00, 20 min)
- General Inspection ($99.99, 60 min)

## Security Considerations

- Input validation on all forms
- SQL injection prevention using parameterized queries
- Email uniqueness enforcement
- Referential integrity with foreign key constraints

## Future Enhancements

Potential improvements that could be added:
- User authentication and authorization
- Email notifications for appointments
- Reporting and analytics dashboard
- Invoice generation
- Inventory management for parts
- Technician assignment and scheduling
- Customer portal for self-service

## Troubleshooting

### Common Issues

1. **Flask not found error**
   ```bash
   pip install Flask
   ```

2. **Database creation issues**
   - Delete `automotive_service.db` file and restart the application
   - Check file permissions in the project directory

3. **Port already in use**
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

## License

This project is created for educational purposes as part of a database course final project.

## Contact

For questions or issues, please refer to the course documentation or contact your instructor.
