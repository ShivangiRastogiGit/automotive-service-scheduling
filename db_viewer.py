#!/usr/bin/env python3
"""
Database Viewer for Automotive Service Scheduling System
Simple script to view database contents
"""

import sqlite3
import sys
from datetime import datetime

DATABASE = 'automotive_service.db'

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        return None

def view_customers():
    """View all customers"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        customers = conn.execute('''
            SELECT 
                c.*,
                COUNT(DISTINCT v.id) as vehicle_count,
                COUNT(DISTINCT a.id) as appointment_count
            FROM customers c
            LEFT JOIN vehicles v ON c.id = v.customer_id
            LEFT JOIN appointments a ON c.id = a.customer_id
            GROUP BY c.id
            ORDER BY c.last_name, c.first_name
        ''').fetchall()
        
        print("\n=== CUSTOMERS ===")
        print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15} {'Vehicles':<8} {'Appointments':<12}")
        print("-" * 95)
        
        for customer in customers:
            name = f"{customer['first_name']} {customer['last_name']}"
            print(f"{customer['id']:<5} {name:<25} {customer['email']:<30} {customer['phone']:<15} {customer['vehicle_count']:<8} {customer['appointment_count']:<12}")
        
        print(f"\nTotal customers: {len(customers)}")
        
    except sqlite3.Error as e:
        print(f"Error viewing customers: {e}")
    finally:
        conn.close()

def view_vehicles():
    """View all vehicles"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        vehicles = conn.execute('''
            SELECT 
                v.*,
                c.first_name,
                c.last_name,
                COUNT(a.id) as appointment_count
            FROM vehicles v
            JOIN customers c ON v.customer_id = c.id
            LEFT JOIN appointments a ON v.id = a.vehicle_id
            GROUP BY v.id
            ORDER BY c.last_name, c.first_name, v.year DESC
        ''').fetchall()
        
        print("\n=== VEHICLES ===")
        print(f"{'ID':<5} {'Owner':<25} {'Vehicle':<30} {'Year':<6} {'VIN':<10} {'Appointments':<12}")
        print("-" * 88)
        
        for vehicle in vehicles:
            owner = f"{vehicle['first_name']} {vehicle['last_name']}"
            vehicle_info = f"{vehicle['make']} {vehicle['model']}"
            vin = vehicle['vin'][:10] if vehicle['vin'] else 'N/A'
            print(f"{vehicle['id']:<5} {owner:<25} {vehicle_info:<30} {vehicle['year']:<6} {vin:<10} {vehicle['appointment_count']:<12}")
        
        print(f"\nTotal vehicles: {len(vehicles)}")
        
    except sqlite3.Error as e:
        print(f"Error viewing vehicles: {e}")
    finally:
        conn.close()

def view_appointments():
    """View all appointments"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        appointments = conn.execute('''
            SELECT 
                a.*,
                c.first_name,
                c.last_name,
                v.make,
                v.model,
                v.year,
                s.name as service_name,
                s.price
            FROM appointments a
            JOIN customers c ON a.customer_id = c.id
            JOIN vehicles v ON a.vehicle_id = v.id
            JOIN services s ON a.service_id = s.id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT 20
        ''').fetchall()
        
        print("\n=== RECENT APPOINTMENTS (Last 20) ===")
        print(f"{'ID':<5} {'Customer':<20} {'Vehicle':<25} {'Service':<20} {'Date':<12} {'Status':<12} {'Price':<8}")
        print("-" * 102)
        
        for appt in appointments:
            customer = f"{appt['first_name']} {appt['last_name']}"
            vehicle = f"{appt['year']} {appt['make']} {appt['model']}"
            print(f"{appt['id']:<5} {customer:<20} {vehicle:<25} {appt['service_name']:<20} {appt['appointment_date']:<12} {appt['status']:<12} ${appt['price']:<7.2f}")
        
        print(f"\nShowing recent 20 appointments")
        
    except sqlite3.Error as e:
        print(f"Error viewing appointments: {e}")
    finally:
        conn.close()

def view_services():
    """View all services"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        services = conn.execute('''
            SELECT 
                s.*,
                COUNT(a.id) as appointment_count,
                SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as total_revenue
            FROM services s
            LEFT JOIN appointments a ON s.id = a.service_id
            GROUP BY s.id
            ORDER BY s.name
        ''').fetchall()
        
        print("\n=== SERVICES ===")
        print(f"{'ID':<5} {'Service Name':<25} {'Duration':<10} {'Price':<10} {'Active':<8} {'Appointments':<12} {'Revenue':<10}")
        print("-" * 80)
        
        for service in services:
            active = "Yes" if service['is_active'] else "No"
            duration = f"{service['estimated_duration']} min"
            print(f"{service['id']:<5} {service['name']:<25} {duration:<10} ${service['price']:<9.2f} {active:<8} {service['appointment_count']:<12} ${service['total_revenue']:<9.2f}")
        
        print(f"\nTotal services: {len(services)}")
        
    except sqlite3.Error as e:
        print(f"Error viewing services: {e}")
    finally:
        conn.close()

def view_statistics():
    """View database statistics"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Customer stats
        customer_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_customers,
                COUNT(CASE WHEN created_at >= date('now', '-30 days') THEN 1 END) as new_customers_30_days
            FROM customers
        ''').fetchone()
        
        # Appointment stats
        appointment_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_appointments,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
            FROM appointments
        ''').fetchone()
        
        # Revenue stats
        revenue_stats = conn.execute('''
            SELECT 
                SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as total_revenue,
                COUNT(CASE WHEN a.status = 'completed' THEN 1 END) as completed_appointments
            FROM appointments a
            JOIN services s ON a.service_id = s.id
        ''').fetchone()
        
        print("\n=== DATABASE STATISTICS ===")
        print(f"Total Customers: {customer_stats['total_customers']}")
        print(f"New Customers (30 days): {customer_stats['new_customers_30_days']}")
        print(f"Total Appointments: {appointment_stats['total_appointments']}")
        print(f"  - Scheduled: {appointment_stats['scheduled']}")
        print(f"  - In Progress: {appointment_stats['in_progress']}")
        print(f"  - Completed: {appointment_stats['completed']}")
        print(f"  - Cancelled: {appointment_stats['cancelled']}")
        print(f"Total Revenue: ${revenue_stats['total_revenue']:.2f}")
        print(f"Completed Services: {revenue_stats['completed_appointments']}")
        
    except sqlite3.Error as e:
        print(f"Error viewing statistics: {e}")
    finally:
        conn.close()

def main():
    """Main function"""
    print("=== Automotive Service Scheduling - Database Viewer ===")
    print(f"Database: {DATABASE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if database exists
    try:
        conn = sqlite3.connect(DATABASE)
        conn.close()
    except sqlite3.Error:
        print(f"Error: Database '{DATABASE}' not found or cannot be accessed.")
        print("Please run setup.py first to create the database.")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        if option == 'customers':
            view_customers()
        elif option == 'vehicles':
            view_vehicles()
        elif option == 'appointments':
            view_appointments()
        elif option == 'services':
            view_services()
        elif option == 'stats':
            view_statistics()
        else:
            print("Invalid option. Use: customers, vehicles, appointments, services, or stats")
    else:
        # Show all by default
        view_statistics()
        view_customers()
        view_vehicles()
        view_services()
        view_appointments()

if __name__ == "__main__":
    main()
