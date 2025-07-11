-- ===================================
-- COMPLETE DATABASE RESET AND RELOAD
-- Automotive Service Scheduling System
-- ===================================
--
-- This script:
-- 1. Wipes all data from all tables
-- 2. Reloads customers from Data/customers_DataSet.csv
-- 3. Reloads services from Data/Service_Type.csv
-- 4. Reloads vehicles from Data/USA_cars_datasets.csv (1-to-1 with customers)
--
-- Run this directly: sqlite3 automotive_service.db < reset_and_reload_all.sql
-- ===================================

-- Enable CSV mode
.mode csv
.headers on

-- ===================================
-- STEP 1: WIPE ALL DATA
-- ===================================

-- Disable foreign key constraints temporarily
PRAGMA foreign_keys = OFF;

-- Delete all records from all tables (in proper order)
DELETE FROM appointments;
DELETE FROM vehicles;
DELETE FROM customers;
DELETE FROM services;

-- Reset auto-increment counters for all tables
DELETE FROM sqlite_sequence WHERE name IN ('customers', 'vehicles', 'services', 'appointments');

-- Re-enable foreign key constraints
PRAGMA foreign_keys = ON;

SELECT 'STEP 1: Database wiped successfully!' as step1_complete;

-- ===================================
-- STEP 2: LOAD CUSTOMERS
-- ===================================

-- Create temporary table for customer CSV data
DROP TABLE IF EXISTS temp_customers;
CREATE TEMPORARY TABLE temp_customers (
    customer_id INTEGER,
    name TEXT,
    email TEXT,
    phone_number TEXT,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    sales_rep TEXT,
    subscription TEXT
);

-- Import customer CSV data
.import Data/customers_DataSet.csv temp_customers

-- Insert customers with data mapping
INSERT INTO customers (first_name, last_name, email, password, phone, address, created_at)
SELECT 
    -- Split name into first_name and last_name
    CASE 
        WHEN INSTR(TRIM(name), ' ') > 0 THEN 
            TRIM(SUBSTR(TRIM(name), 1, INSTR(TRIM(name), ' ') - 1))
        ELSE TRIM(name)
    END as first_name,
    
    CASE 
        WHEN INSTR(TRIM(name), ' ') > 0 THEN 
            TRIM(SUBSTR(TRIM(name), INSTR(TRIM(name), ' ') + 1))
        ELSE ''
    END as last_name,
    
    -- Clean email
    LOWER(TRIM(email)) as email,
    
    -- Default password hash for '123456'
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f' as password,
    
    -- Clean phone number
    TRIM(phone_number) as phone,
    
    -- Combine address fields
    TRIM(street_address) || ', ' || TRIM(city) || ', ' || TRIM(state) || ' ' || TRIM(zip_code) as address,
    
    -- Random creation date in the last year
    datetime('now', '-' || (ABS(RANDOM()) % 365) || ' days') as created_at
    
FROM temp_customers 
WHERE name IS NOT NULL 
  AND TRIM(name) != ''
  AND TRIM(name) != 'Name'
  AND email IS NOT NULL 
  AND TRIM(email) != ''
  AND TRIM(email) != 'Email'
  AND phone_number IS NOT NULL
  AND TRIM(phone_number) != ''
  AND street_address IS NOT NULL
  AND TRIM(street_address) != ''
GROUP BY LOWER(TRIM(email))  -- This ensures only unique emails are kept
HAVING MIN(customer_id) = customer_id;  -- Keep the first occurrence of each email

-- Clean up customers temp table
DROP TABLE IF EXISTS temp_customers;

SELECT 'STEP 2: ' || COUNT(*) || ' customers loaded successfully!' as step2_complete FROM customers;

-- ===================================
-- STEP 3: LOAD SERVICES
-- ===================================

-- Create temporary table for service CSV data
DROP TABLE IF EXISTS temp_service_data;
CREATE TEMPORARY TABLE temp_service_data (
    vehicle_id TEXT,
    repair_date TEXT,
    repair_description TEXT,
    cost REAL,
    parts_replaced TEXT,
    repair_shop TEXT,
    mechanic TEXT,
    warranty_expiry TEXT
);

-- Import service CSV data
.import Data/Service_Type.csv temp_service_data

-- Insert distinct services with auto-generated descriptions and durations
INSERT INTO services (name, description, estimated_duration, price, is_active)
SELECT DISTINCT
    -- Map Repair Description to name
    repair_description as name,
    
    -- Auto-generate description based on service type
    CASE 
        WHEN repair_description = 'Oil Change' THEN 'Complete engine oil and filter replacement service'
        WHEN repair_description = 'Brake Service' THEN 'Comprehensive brake system inspection, adjustment, and repair'
        WHEN repair_description = 'Brake Inspection' THEN 'Thorough brake system safety inspection and assessment'
        WHEN repair_description = 'Transmission Repair' THEN 'Professional transmission diagnosis, repair, and maintenance'
        WHEN repair_description = 'Engine Repair' THEN 'Complete engine diagnostic and repair services'
        WHEN repair_description = 'AC Repair' THEN 'Air conditioning system diagnosis, repair, and recharge'
        WHEN repair_description = 'Suspension Repair' THEN 'Suspension system inspection, repair, and alignment'
        WHEN repair_description = 'Tire Replacement' THEN 'Professional tire installation and balancing service'
        WHEN repair_description = 'Battery Replacement' THEN 'Battery testing, replacement, and electrical system check'
        WHEN repair_description = 'Clutch Replacement' THEN 'Complete clutch system replacement and adjustment'
        WHEN repair_description = 'Fuel System Repair' THEN 'Fuel system cleaning, repair, and optimization'
        WHEN repair_description = 'Tire Rotation' THEN 'Tire rotation and pressure check for even wear'
        WHEN repair_description = 'Battery Test' THEN 'Comprehensive battery and charging system testing'
        WHEN repair_description = 'General Inspection' THEN 'Complete vehicle safety and maintenance inspection'
        WHEN repair_description = 'Air Filter Replacement' THEN 'Engine and cabin air filter replacement service'
        WHEN repair_description = 'Transmission Service' THEN 'Transmission fluid change and system maintenance'
        WHEN repair_description = 'Cooling System Service' THEN 'Coolant system flush and radiator maintenance'
        ELSE 'Professional automotive ' || LOWER(repair_description) || ' service'
    END as description,
    
    -- Auto-generate estimated_duration based on service complexity
    CASE 
        WHEN repair_description IN ('Oil Change', 'Battery Test', 'Air Filter Replacement') THEN 30
        WHEN repair_description IN ('Tire Rotation', 'Battery Replacement', 'Brake Inspection') THEN 45
        WHEN repair_description IN ('Brake Service', 'Tire Replacement', 'Cooling System Service') THEN 60
        WHEN repair_description IN ('AC Repair', 'Suspension Repair', 'General Inspection') THEN 90
        WHEN repair_description IN ('Fuel System Repair', 'Transmission Service') THEN 120
        WHEN repair_description IN ('Engine Repair', 'Transmission Repair', 'Clutch Replacement') THEN 180
        ELSE 60
    END as estimated_duration,
    
    -- Map cost to price (use average cost for each service type)
    ROUND(AVG(cost), 2) as price,
    
    -- Set all services as active
    1 as is_active
    
FROM temp_service_data 
WHERE repair_description IS NOT NULL 
  AND TRIM(repair_description) != ''
  AND TRIM(repair_description) != 'Repair Description'
  AND cost IS NOT NULL
  AND cost > 0
GROUP BY repair_description
ORDER BY repair_description;

-- Clean up services temp table
DROP TABLE IF EXISTS temp_service_data;

SELECT 'STEP 3: ' || COUNT(*) || ' services loaded successfully!' as step3_complete FROM services;

-- ===================================
-- STEP 4: LOAD VEHICLES
-- ===================================

-- Create temporary table for vehicle CSV data
DROP TABLE IF EXISTS temp_csv_vehicles;
CREATE TEMPORARY TABLE temp_csv_vehicles (
    csv_index INTEGER,
    price REAL,
    brand TEXT,
    model TEXT,
    year INTEGER,
    title_status TEXT,
    mileage REAL,
    color TEXT,
    vin TEXT,
    lot TEXT,
    state TEXT,
    country TEXT,
    condition TEXT
);

-- Import vehicle CSV data
.import Data/USA_cars_datasets.csv temp_csv_vehicles

-- Insert vehicles with automatic 1-to-1 customer assignment
INSERT INTO vehicles (customer_id, make, model, year, license_plate, color, mileage, vin, created_at)
SELECT 
    c.id as customer_id,
    UPPER(SUBSTR(v.brand, 1, 1)) || LOWER(SUBSTR(v.brand, 2)) as make,
    UPPER(SUBSTR(v.model, 1, 1)) || LOWER(SUBSTR(v.model, 2)) as model,
    v.year,
    CASE 
        WHEN v.vin IS NOT NULL AND TRIM(v.vin) != '' THEN 
            'VIN' || SUBSTR(REPLACE(TRIM(v.vin), ' ', ''), -7)
        ELSE 'LIC' || SUBSTR(CAST(ABS(RANDOM()) AS TEXT), 1, 6)
    END as license_plate,
    CASE 
        WHEN v.color IS NOT NULL AND TRIM(v.color) != '' THEN 
            UPPER(SUBSTR(TRIM(v.color), 1, 1)) || LOWER(SUBSTR(TRIM(v.color), 2))
        ELSE 'Unknown'
    END as color,
    CAST(COALESCE(v.mileage, 0) AS INTEGER) as mileage,
    'LOT-' || v.lot as vin,
    datetime('now', '-' || (ABS(RANDOM()) % 365) || ' days') as created_at
FROM (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY csv_index) as row_num,
        brand, model, year, vin, color, mileage, lot
    FROM temp_csv_vehicles 
    WHERE brand IS NOT NULL 
      AND model IS NOT NULL 
      AND year IS NOT NULL
      AND year BETWEEN 1990 AND 2025
) v
JOIN (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY id) as row_num,
        id
    FROM customers
) c ON v.row_num = c.row_num;

-- Clean up vehicles temp table
DROP TABLE IF EXISTS temp_csv_vehicles;

SELECT 'STEP 4: ' || COUNT(*) || ' vehicles loaded successfully!' as step4_complete FROM vehicles;

-- ===================================
-- FINAL SUMMARY
-- ===================================

SELECT '========================================' as separator;
SELECT 'DATABASE RESET AND RELOAD COMPLETE!' as final_title;
SELECT '========================================' as separator;

-- Show final counts
SELECT 'Final Database Summary:' as summary_title;
SELECT 'Customers: ' || COUNT(*) as customers_total FROM customers;
SELECT 'Services: ' || COUNT(*) as services_total FROM services;
SELECT 'Vehicles: ' || COUNT(*) as vehicles_total FROM vehicles;
SELECT 'Appointments: ' || COUNT(*) as appointments_total FROM appointments;

-- Show sample data
SELECT 'Sample Customer-Vehicle Assignments:' as sample_title;
SELECT 
    c.first_name || ' ' || c.last_name as customer,
    c.email,
    v.year || ' ' || v.make || ' ' || v.model as vehicle,
    v.license_plate
FROM customers c
JOIN vehicles v ON c.id = v.customer_id
ORDER BY c.id
LIMIT 5;

-- Show sample services
SELECT 'Sample Services:' as services_sample_title;
SELECT 
    name,
    '$' || price as price_formatted,
    estimated_duration || ' min' as duration
FROM services 
ORDER BY price
LIMIT 5;

SELECT '========================================' as separator;
SELECT 'All data loaded successfully!' as success_message;
SELECT 'Default customer password: 123456' as password_info;
SELECT '========================================' as separator;
