# Automotive Service Scheduling - Authentication Guide

This guide explains the authentication and authorization system implemented in the automotive service scheduling application.

## Overview

The application implements a secure customer authentication system where:
- Each customer can only access their own data
- Session-based authentication
- Password hashing for security
- Protected routes for customer-specific operations

## Authentication Features

### Customer Registration
- Secure password validation (minimum 6 characters)
- Email uniqueness enforcement
- Password confirmation matching
- Automatic login after successful registration

### Customer Login
- Email and password authentication
- SHA256 password hashing
- Session management with Flask sessions
- Secure logout functionality

### Session Management
- Customer ID stored in session
- Customer name stored for display
- Session-based route protection
- Automatic session cleanup on logout

## Authorization System

### Customer Data Isolation
Each customer can only access their own:
- Vehicles
- Appointments
- Profile information
- Service history

### Protected Routes
All customer-specific routes require authentication:
- `/dashboard` - Personal dashboard
- `/my-vehicles` - Customer's vehicles only
- `/my-appointments` - Customer's appointments only
- `/profile` - Account management
- `/vehicles/add` - Add vehicle to customer's account
- `/appointments/add` - Schedule appointment for customer's vehicles

## Implementation Details

### Password Security
```python
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()
```

### Login Required Decorator
```python
def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
```

### Customer Data Queries
All customer-specific queries include customer_id filter:
```sql
-- Example: Get customer's vehicles only
SELECT * FROM vehicles WHERE customer_id = ?

-- Example: Get customer's appointments only
SELECT a.*, v.make, v.model, s.name as service_name
FROM appointments a
JOIN vehicles v ON a.vehicle_id = v.id
JOIN services s ON a.service_id = s.id
WHERE a.customer_id = ?
```

## Security Best Practices

1. **Password Hashing**: All passwords are hashed using SHA256
2. **Session Security**: Flask sessions with secret key
3. **Input Validation**: Form validation on all user inputs
4. **SQL Injection Prevention**: Parameterized queries
5. **Data Isolation**: Customer-specific data access only
6. **Route Protection**: Authentication required for sensitive routes

## Usage Examples

### Customer Registration
1. User fills registration form
2. System validates email uniqueness
3. Password is hashed and stored
4. User is automatically logged in
5. Session is created with customer information

### Customer Login
1. User provides email and password
2. System looks up customer with hashed password
3. If valid, session is created
4. User is redirected to dashboard

### Accessing Protected Data
1. User must be logged in
2. All database queries filter by customer_id from session
3. User can only see/modify their own data

## Error Handling

- Invalid login credentials show error message
- Unauthorized access redirects to login page
- Form validation errors are displayed to user
- Database errors are handled gracefully

## Demo Accounts

For testing purposes, the application includes demo accounts:
- Email: john.doe@email.com | Password: password123
- Email: jane.smith@email.com | Password: password123
- Email: bob.johnson@email.com | Password: password123

## Future Enhancements

- Email verification for new accounts
- Password reset functionality
- Two-factor authentication
- Admin role management
- Account lockout after failed attempts
- Password strength requirements
