#!/usr/bin/env python3
"""
Setup script for Automotive Service Scheduling System
This script initializes the database and starts the Flask application
"""

import sqlite3
import os
import hashlib
from datetime import datetime

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Initialize the database with tables and sample data"""
    print("Setting up database...")
    
    # Database file path
    db_path = 'automotive_service.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating tables...")
    
    # Customers table
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vehicles table
    cursor.execute('''
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            vin TEXT UNIQUE,
            license_plate TEXT,
            color TEXT,
            mileage INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Services table
    cursor.execute('''
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            estimated_duration INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Appointments table
    cursor.execute('''
        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TIME NOT NULL,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
    ''')
    
    # Insert sample services
    print("Inserting sample services...")
    services = [
        ('Oil Change', 'Regular oil and filter change', 30, 49.99),
        ('Brake Inspection', 'Complete brake system inspection', 45, 75.00),
        ('Tire Rotation', 'Rotate tires for even wear', 30, 35.00),
        ('Battery Test', 'Battery and charging system test', 20, 25.00),
        ('General Inspection', 'Comprehensive vehicle inspection', 60, 99.99),
        ('Air Filter Replacement', 'Replace engine air filter', 15, 29.99),
        ('Transmission Service', 'Transmission fluid change and inspection', 90, 149.99),
        ('Cooling System Service', 'Coolant flush and system check', 60, 89.99)
    ]
    
    cursor.executemany('''
        INSERT INTO services (name, description, estimated_duration, price)
        VALUES (?, ?, ?, ?)
    ''', services)
    
    # Insert sample customers
    print("Inserting sample customers...")
    customers = [
        ('John', 'Doe', 'john.doe@email.com', hash_password('password123'), '555-0123', '123 Main St, Anytown, ST 12345'),
        ('Jane', 'Smith', 'jane.smith@email.com', hash_password('password123'), '555-0124', '456 Oak Ave, Somewhere, ST 12346'),
        ('Bob', 'Johnson', 'bob.johnson@email.com', hash_password('password123'), '555-0125', '789 Pine Rd, Elsewhere, ST 12347')
    ]
    
    cursor.executemany('''
        INSERT INTO customers (first_name, last_name, email, password, phone, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', customers)
    
    # Insert sample vehicles
    print("Inserting sample vehicles...")
    vehicles = [
        (1, 'Toyota', 'Camry', 2020, 'JT2BF22K5X0123456', 'ABC-123', 'Silver', 25000),
        (1, 'Honda', 'Civic', 2018, 'JHMFC2F59JX987654', 'XYZ-789', 'Blue', 45000),
        (2, 'Ford', 'F-150', 2021, '1FTFW1E51MFA12345', 'DEF-456', 'Red', 15000),
        (3, 'Chevrolet', 'Malibu', 2019, '1G1ZB5ST8KF123456', 'GHI-012', 'White', 32000)
    ]
    
    cursor.executemany('''
        INSERT INTO vehicles (customer_id, make, model, year, vin, license_plate, color, mileage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', vehicles)
    
    # Insert sample appointments
    print("Inserting sample appointments...")
    appointments = [
        (1, 1, 1, '2025-01-15', '09:00', 'scheduled', 'Regular maintenance'),
        (2, 3, 2, '2025-01-16', '10:30', 'scheduled', 'Customer reported squeaking'),
        (3, 4, 3, '2025-01-17', '14:00', 'scheduled', None)
    ]
    
    cursor.executemany('''
        INSERT INTO appointments (customer_id, vehicle_id, service_id, appointment_date, appointment_time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', appointments)
    
    # Create indexes for performance
    print("Creating indexes...")
    indexes = [
        'CREATE INDEX idx_customers_email ON customers(email)',
        'CREATE INDEX idx_customers_name ON customers(last_name, first_name)',
        'CREATE INDEX idx_vehicles_customer ON vehicles(customer_id)',
        'CREATE INDEX idx_appointments_customer ON appointments(customer_id)',
        'CREATE INDEX idx_appointments_date ON appointments(appointment_date)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("Database setup completed successfully!")
    print(f"Database created: {os.path.abspath(db_path)}")

def main():
    """Main setup function"""
    print("=" * 50)
    print("Automotive Service Scheduling System Setup")
    print("=" * 50)
    
    # Check if Flask is installed
    try:
        import flask
        print(f"✓ Flask {flask.__version__} is installed")
    except ImportError:
        print("✗ Flask is not installed")
        print("Please run: pip install flask")
        return
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nTo start the application:")
    print("1. Run: python app.py")
    print("2. Open your browser to: http://127.0.0.1:5000")
    print("\nSample data has been loaded:")
    print("- 3 customers")
    print("- 4 vehicles")
    print("- 8 services")
    print("- 3 sample appointments")

if __name__ == '__main__':
    main()
