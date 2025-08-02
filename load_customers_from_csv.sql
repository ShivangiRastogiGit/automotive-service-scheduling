-- Description: Load customer data from customers_DataSet.csv 

PRAGMA foreign_keys = ON;

-- Display current customer count before loading
SELECT 'Current customers in database before loading:' as message;
SELECT COUNT(*) as count FROM customers;

-- Create temporary table to match CSV structure
CREATE TEMPORARY TABLE temp_customers_csv (
    customer_id_csv TEXT,
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

-- Insert customers with data transformations, skipping duplicates
INSERT OR IGNORE INTO customers (first_name, last_name, email, password, phone, address, created_at)
SELECT 
    -- Split name into first and last name
    CASE 
        WHEN name LIKE '% %' THEN TRIM(SUBSTR(name, 1, INSTR(name, ' ') - 1))
        ELSE TRIM(name)
    END as first_name,
    CASE 
        WHEN name LIKE '% %' THEN TRIM(SUBSTR(name, INSTR(name, ' ') + 1))
        ELSE ''
    END as last_name,
    email,
    -- Password hash for '123456' 
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' as password,
    phone_number as phone,
    -- Concatenate address fields
    street_address || ', ' || city || ', ' || state || ' ' || zip_code as address,
    -- Generate random created_at dates within last year
    datetime('2024-01-01', '+' || (ABS(RANDOM()) % 365) || ' days', 
             '+' || (ABS(RANDOM()) % 24) || ' hours',
             '+' || (ABS(RANDOM()) % 60) || ' minutes') as created_at
FROM temp_customers_csv
WHERE email IS NOT NULL 
  AND email != ''
  AND email != 'Email'  -- Skip header row
  AND name != 'Name'     -- Additional header check
  AND email NOT IN (SELECT email FROM customers);

-- Display results
SELECT 'Customer loading completed!' as message;
SELECT COUNT(*) as total_customers_after FROM customers;

-- Show sample of loaded customers
SELECT 'Sample of recent customers:' as sample_header;
SELECT first_name, last_name, email, phone 
FROM customers 
ORDER BY id DESC 
LIMIT 5;

-- Clean up temporary table
DROP TABLE temp_customers_csv;