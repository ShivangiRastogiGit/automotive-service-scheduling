-- Automotive Service Scheduling System - SQL Scripts
-- This file contains all SQL operations for CRUD functionality

-- ===================================
-- DATABASE SCHEMA CREATION
-- ===================================

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
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
);

-- Create services table
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    estimated_duration INTEGER NOT NULL, -- in minutes
    price DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
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
);

-- ===================================
-- SAMPLE DATA INSERTION
-- ===================================

-- Insert sample services
INSERT OR IGNORE INTO services (name, description, estimated_duration, price) VALUES
('Oil Change', 'Regular oil and filter change', 30, 49.99),
('Brake Inspection', 'Complete brake system inspection', 45, 75.00),
('Tire Rotation', 'Rotate tires for even wear', 30, 35.00),
('Battery Test', 'Battery and charging system test', 20, 25.00),
('General Inspection', 'Comprehensive vehicle inspection', 60, 99.99),
('Air Filter Replacement', 'Replace engine air filter', 15, 29.99),
('Transmission Service', 'Transmission fluid change and inspection', 90, 149.99),
('Cooling System Service', 'Coolant flush and system check', 60, 89.99);

-- ===================================
-- CUSTOMERS CRUD OPERATIONS
-- ===================================

-- CREATE - Insert new customer
-- Example:
-- INSERT INTO customers (first_name, last_name, email, phone, address)
-- VALUES ('John', 'Doe', 'john.doe@email.com', '555-0123', '123 Main St, City, State');

-- READ - Select all customers
SELECT * FROM customers ORDER BY last_name, first_name;

-- READ - Select customer by ID
-- SELECT * FROM customers WHERE id = ?;

-- READ - Select customer with their vehicles and appointments
SELECT 
    c.*,
    COUNT(DISTINCT v.id) as vehicle_count,
    COUNT(DISTINCT a.id) as appointment_count
FROM customers c
LEFT JOIN vehicles v ON c.id = v.customer_id
LEFT JOIN appointments a ON c.id = a.customer_id
GROUP BY c.id
ORDER BY c.last_name, c.first_name;

-- UPDATE - Update customer information
-- UPDATE customers 
-- SET first_name = ?, last_name = ?, email = ?, phone = ?, address = ?
-- WHERE id = ?;

-- DELETE - Delete customer (only if no appointments exist)
-- DELETE FROM customers WHERE id = ? AND id NOT IN (SELECT DISTINCT customer_id FROM appointments);

-- ===================================
-- VEHICLES CRUD OPERATIONS
-- ===================================

-- CREATE - Insert new vehicle
-- INSERT INTO vehicles (customer_id, make, model, year, vin, license_plate, color, mileage)
-- VALUES (?, ?, ?, ?, ?, ?, ?, ?);

-- READ - Select all vehicles with customer information
SELECT 
    v.*,
    c.first_name,
    c.last_name,
    c.email
FROM vehicles v
JOIN customers c ON v.customer_id = c.id
ORDER BY c.last_name, c.first_name, v.year DESC;

-- READ - Select vehicles by customer ID
-- SELECT * FROM vehicles WHERE customer_id = ? ORDER BY year DESC;

-- READ - Select vehicle by ID with customer info
-- SELECT 
--     v.*,
--     c.first_name,
--     c.last_name
-- FROM vehicles v
-- JOIN customers c ON v.customer_id = c.id
-- WHERE v.id = ?;

-- UPDATE - Update vehicle information
-- UPDATE vehicles 
-- SET make = ?, model = ?, year = ?, vin = ?, license_plate = ?, color = ?, mileage = ?
-- WHERE id = ?;

-- DELETE - Delete vehicle
-- DELETE FROM vehicles WHERE id = ?;

-- ===================================
-- SERVICES CRUD OPERATIONS
-- ===================================

-- CREATE - Insert new service
-- INSERT INTO services (name, description, estimated_duration, price, is_active)
-- VALUES (?, ?, ?, ?, ?);

-- READ - Select all active services
SELECT * FROM services WHERE is_active = 1 ORDER BY name;

-- READ - Select all services
SELECT * FROM services ORDER BY name;

-- READ - Select service by ID
-- SELECT * FROM services WHERE id = ?;

-- UPDATE - Update service information
-- UPDATE services 
-- SET name = ?, description = ?, estimated_duration = ?, price = ?, is_active = ?
-- WHERE id = ?;

-- UPDATE - Deactivate service
-- UPDATE services SET is_active = 0 WHERE id = ?;

-- DELETE - Delete service (not recommended, use deactivate instead)
-- DELETE FROM services WHERE id = ?;

-- ===================================
-- APPOINTMENTS CRUD OPERATIONS
-- ===================================

-- CREATE - Insert new appointment
-- INSERT INTO appointments (customer_id, vehicle_id, service_id, appointment_date, appointment_time, notes)
-- VALUES (?, ?, ?, ?, ?, ?);

-- READ - Select all appointments with full details
SELECT 
    a.*,
    c.first_name,
    c.last_name,
    c.email,
    c.phone,
    v.make,
    v.model,
    v.year,
    v.license_plate,
    s.name as service_name,
    s.description as service_description,
    s.estimated_duration,
    s.price
FROM appointments a
JOIN customers c ON a.customer_id = c.id
JOIN vehicles v ON a.vehicle_id = v.id
JOIN services s ON a.service_id = s.id
ORDER BY a.appointment_date DESC, a.appointment_time DESC;

-- READ - Select appointments by customer ID
-- SELECT 
--     a.*,
--     v.make,
--     v.model,
--     s.name as service_name,
--     s.price
-- FROM appointments a
-- JOIN vehicles v ON a.vehicle_id = v.id
-- JOIN services s ON a.service_id = s.id
-- WHERE a.customer_id = ?
-- ORDER BY a.appointment_date DESC, a.appointment_time DESC;

-- READ - Select appointments by date range
-- SELECT 
--     a.*,
--     c.first_name,
--     c.last_name,
--     v.make,
--     v.model,
--     s.name as service_name
-- FROM appointments a
-- JOIN customers c ON a.customer_id = c.id
-- JOIN vehicles v ON a.vehicle_id = v.id
-- JOIN services s ON a.service_id = s.id
-- WHERE a.appointment_date BETWEEN ? AND ?
-- ORDER BY a.appointment_date, a.appointment_time;

-- READ - Select upcoming appointments
SELECT 
    a.*,
    c.first_name,
    c.last_name,
    v.make,
    v.model,
    s.name as service_name
FROM appointments a
JOIN customers c ON a.customer_id = c.id
JOIN vehicles v ON a.vehicle_id = v.id
JOIN services s ON a.service_id = s.id
WHERE a.appointment_date >= date('now') AND a.status != 'cancelled'
ORDER BY a.appointment_date, a.appointment_time;

-- UPDATE - Update appointment status
-- UPDATE appointments SET status = ? WHERE id = ?;

-- UPDATE - Update appointment details
-- UPDATE appointments 
-- SET appointment_date = ?, appointment_time = ?, notes = ?
-- WHERE id = ?;

-- UPDATE - Update appointment details (full update for customer edit)
-- UPDATE appointments 
-- SET vehicle_id = ?, service_id = ?, appointment_date = ?, appointment_time = ?, notes = ?
-- WHERE id = ? AND customer_id = ?;

-- UPDATE - Reschedule appointment
-- UPDATE appointments 
-- SET appointment_date = ?, appointment_time = ?, status = 'scheduled'
-- WHERE id = ?;

-- DELETE - Cancel appointment (update status instead of delete)
-- UPDATE appointments SET status = 'cancelled' WHERE id = ?;

-- DELETE - Actually delete appointment (use with caution)
-- DELETE FROM appointments WHERE id = ?;

-- ===================================
-- REPORTING QUERIES
-- ===================================

-- Get customer statistics
SELECT 
    COUNT(*) as total_customers,
    COUNT(CASE WHEN created_at >= date('now', '-30 days') THEN 1 END) as new_customers_30_days
FROM customers;

-- Get appointment statistics
SELECT 
    COUNT(*) as total_appointments,
    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
FROM appointments;

-- Get revenue by service
SELECT 
    s.name,
    COUNT(a.id) as appointment_count,
    SUM(s.price) as total_revenue,
    AVG(s.price) as avg_price
FROM services s
LEFT JOIN appointments a ON s.id = a.service_id AND a.status = 'completed'
GROUP BY s.id, s.name
ORDER BY total_revenue DESC;

-- Get customer appointment history with totals
SELECT 
    c.first_name,
    c.last_name,
    c.email,
    COUNT(a.id) as total_appointments,
    SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as total_spent,
    MAX(a.appointment_date) as last_appointment
FROM customers c
LEFT JOIN appointments a ON c.id = a.customer_id
LEFT JOIN services s ON a.service_id = s.id
GROUP BY c.id
ORDER BY total_spent DESC;

-- Get monthly appointment trends
SELECT 
    strftime('%Y-%m', appointment_date) as month,
    COUNT(*) as appointment_count,
    SUM(s.price) as revenue
FROM appointments a
JOIN services s ON a.service_id = s.id
WHERE a.status = 'completed'
GROUP BY strftime('%Y-%m', appointment_date)
ORDER BY month DESC;

-- Get busiest appointment times
SELECT 
    strftime('%H', appointment_time) as hour,
    COUNT(*) as appointment_count
FROM appointments
GROUP BY strftime('%H', appointment_time)
ORDER BY appointment_count DESC;

-- ===================================
-- MAINTENANCE QUERIES
-- ===================================

-- Find customers without vehicles
SELECT c.* 
FROM customers c
LEFT JOIN vehicles v ON c.id = v.customer_id
WHERE v.id IS NULL;

-- Find vehicles without appointments
SELECT 
    v.*,
    c.first_name,
    c.last_name
FROM vehicles v
JOIN customers c ON v.customer_id = c.id
LEFT JOIN appointments a ON v.id = a.vehicle_id
WHERE a.id IS NULL;

-- Find duplicate customers by email
SELECT email, COUNT(*) as count
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;

-- Clean up cancelled appointments older than 1 year
-- DELETE FROM appointments 
-- WHERE status = 'cancelled' AND appointment_date < date('now', '-1 year');

-- ===================================
-- INDEXES FOR PERFORMANCE
-- ===================================

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_vehicles_customer ON vehicles(customer_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_vin ON vehicles(vin);
CREATE INDEX IF NOT EXISTS idx_appointments_customer ON appointments(customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_vehicle ON appointments(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_appointments_service ON appointments(service_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
