-- Description: Wipe existing data and reload from all CSV files

PRAGMA foreign_keys = ON;

-- Display current data counts
SELECT 'Current data counts before wiping:' as message;
SELECT 'Customers:' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 'Services:', COUNT(*) FROM services
UNION ALL
SELECT 'Vehicles:', COUNT(*) FROM vehicles
UNION ALL
SELECT 'Appointments:', COUNT(*) FROM appointments;

-- Delete in correct order to respect foreign key constraints
DELETE FROM appointments;
DELETE FROM vehicles;
DELETE FROM services;
DELETE FROM customers;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('customers', 'services', 'vehicles', 'appointments');

SELECT 'All data wiped successfully!' as message;

-- Create temporary table to match CSV structure
CREATE TEMPORARY TABLE temp_customers_csv (
    csv_index TEXT,
    Name TEXT,
    Email TEXT,
    "Phone Number" TEXT,
    Address TEXT,
    City TEXT,
    State TEXT,
    "Zip Code" TEXT
);

-- Import customers CSV data
-- Insert customers with data transformations
INSERT OR IGNORE INTO customers (first_name, last_name, email, phone, address, password, created_at)
SELECT 
    -- Split name into first and last name
    CASE 
        WHEN INSTR(TRIM(c.Name), ' ') > 0 THEN 
            TRIM(SUBSTR(TRIM(c.Name), 1, INSTR(TRIM(c.Name), ' ') - 1))
        ELSE TRIM(c.Name)
    END as first_name,
    
    CASE 
        WHEN INSTR(TRIM(c.Name), ' ') > 0 THEN 
            TRIM(SUBSTR(TRIM(c.Name), INSTR(TRIM(c.Name), ' ') + 1))
        ELSE ''
    END as last_name,
    
    -- Clean email
    LOWER(TRIM(c.Email)) as email,
    
    -- Clean phone number
    TRIM(c."Phone Number") as phone,
    
    -- Concatenate full address
    TRIM(c.Address || ', ' || c.City || ', ' || c.State || ' ' || c."Zip Code") as address,
    
    -- Generate password hash for default password '123456'
    'e10adc3949ba59abbe56e057f20f883e' as password,
    
    -- Generate random created_at dates within last 2 years
    datetime('2023-01-01', '+' || (ABS(RANDOM()) % 730) || ' days', 
             '+' || (ABS(RANDOM()) % 24) || ' hours',
             '+' || (ABS(RANDOM()) % 60) || ' minutes') as created_at
FROM temp_customers_csv c
WHERE c.Name IS NOT NULL 
  AND c.Name != ''
  AND c.Email IS NOT NULL 
  AND c.Email != ''
  AND c.Email LIKE '%@%';

SELECT 'Customers loaded: ' || COUNT(*) as message FROM customers;

-- Create temporary table to match CSV structure
CREATE TEMPORARY TABLE temp_services_csv (
    csv_index TEXT,
    "Repair Description" TEXT,
    Cost REAL
);

-- Import services CSV data
-- Insert services with data transformations
INSERT OR IGNORE INTO services (name, description, price, estimated_duration)
SELECT 
    -- Use repair description as service name (capitalize first letter)
    UPPER(SUBSTR(TRIM(s."Repair Description"), 1, 1)) || LOWER(SUBSTR(TRIM(s."Repair Description"), 2)) as name,
    
    -- Generate a description based on the service name
    'Professional ' || LOWER(TRIM(s."Repair Description")) || ' service for your vehicle. Our certified technicians ensure quality work.' as description,
    
    -- Use cost as price, ensuring it's reasonable
    CASE 
        WHEN s.Cost <= 0 THEN 50.00
        WHEN s.Cost > 5000 THEN 5000.00
        ELSE ROUND(s.Cost, 2)
    END as price,
    
    -- Generate estimated duration based on cost (higher cost = longer duration)
    CASE 
        WHEN s.Cost <= 100 THEN 60
        WHEN s.Cost <= 500 THEN 120
        WHEN s.Cost <= 1000 THEN 180
        ELSE 240
    END as estimated_duration
FROM temp_services_csv s
WHERE s."Repair Description" IS NOT NULL 
  AND TRIM(s."Repair Description") != ''
  AND s.Cost IS NOT NULL;

SELECT 'Services loaded: ' || COUNT(*) as message FROM services;

-- Create temporary table to match CSV structure
CREATE TEMPORARY TABLE temp_vehicles_csv (
    csv_index TEXT,
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

-- Import vehicles CSV data
-- Create a temporary table to assign customers randomly but ensure no duplicate assignments
CREATE TEMPORARY TABLE temp_customer_assignment AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY RANDOM()) as row_num,
    id as customer_id
FROM customers;

-- Insert vehicles with data transformations and customer assignments
INSERT OR IGNORE INTO vehicles (customer_id, make, model, year, vin, license_plate, color, mileage, created_at)
SELECT 
    -- Assign customers cyclically using a simple approach
    (ABS(RANDOM()) % (SELECT COUNT(*) FROM customers)) + 1 as customer_id,
    -- Map brand to make (capitalize first letter)
    UPPER(SUBSTR(v.brand, 1, 1)) || LOWER(SUBSTR(v.brand, 2)) as make,
    -- Map model to model (capitalize first letter)
    UPPER(SUBSTR(v.model, 1, 1)) || LOWER(SUBSTR(v.model, 2)) as model,
    -- Map year to year
    v.year,
    -- Map vin to vin (clean up whitespace)
    TRIM(v.vin) as vin,
    -- Map lot to license_plate (format as license plate)
    'LP-' || SUBSTR(v.lot, -6) as license_plate,
    -- Map color to color (capitalize first letter)
    CASE 
        WHEN v.color IS NOT NULL AND v.color != '' THEN
            UPPER(SUBSTR(v.color, 1, 1)) || LOWER(SUBSTR(v.color, 2))
        ELSE 'Unknown'
    END as color,
    -- Map mileage to mileage (convert to integer)
    CAST(ROUND(v.mileage) AS INTEGER) as mileage,
    -- Generate random created_at dates within last year
    datetime('2024-01-01', '+' || (ABS(RANDOM()) % 365) || ' days', 
             '+' || (ABS(RANDOM()) % 24) || ' hours',
             '+' || (ABS(RANDOM()) % 60) || ' minutes') as created_at
FROM temp_vehicles_csv v
WHERE v.brand IS NOT NULL 
  AND v.brand != ''
  AND v.model IS NOT NULL 
  AND v.model != ''
  AND v.year IS NOT NULL
  AND v.year > 1980
  AND v.year <= 2025
  AND v.vin IS NOT NULL
  AND TRIM(v.vin) != ''
  AND v.mileage IS NOT NULL
  AND v.mileage >= 0;

SELECT 'Vehicles loaded: ' || COUNT(*) as message FROM vehicles;

SELECT 'Final data counts after reload:' as message;
SELECT 'Customers:' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 'Services:', COUNT(*) FROM services
UNION ALL
SELECT 'Vehicles:', COUNT(*) FROM vehicles
UNION ALL
SELECT 'Appointments:', COUNT(*) FROM appointments;

-- Show sample data
SELECT 'Sample customers:' as sample_header;
SELECT first_name, last_name, email FROM customers LIMIT 3;

SELECT 'Sample services:' as sample_header;
SELECT name, price FROM services LIMIT 3;

SELECT 'Sample vehicles with owners:' as sample_header;
SELECT 
    v.make, v.model, v.year, 
    c.first_name || ' ' || c.last_name as owner
FROM vehicles v
JOIN customers c ON v.customer_id = c.id
LIMIT 3;

-- Clean up temporary tables
DROP TABLE temp_customers_csv;
DROP TABLE temp_services_csv;
DROP TABLE temp_vehicles_csv;
DROP TABLE temp_customer_assignment;

SELECT 'All data reloaded successfully!' as completion_message;
