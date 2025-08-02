-- Create temporary table to match CSV structure
CREATE TEMPORARY TABLE temp_vehicles_csv (
    "?" TEXT,          
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

-- Insert vehicles with data transformations and customer assignments
-- Assign row numbers to vehicles and customers
WITH numbered_vehicles AS (
  SELECT *, ROW_NUMBER() OVER (ORDER BY vin) AS vehicle_row_num
  FROM temp_vehicles_csv
  WHERE brand IS NOT NULL 
    AND brand != ''
    AND brand != 'brand'
    AND model IS NOT NULL 
    AND model != ''
    AND model != 'model'
    AND year IS NOT NULL
    AND CAST(year AS INTEGER) > 1980
    AND CAST(year AS INTEGER) <= 2025
    AND vin IS NOT NULL
    AND TRIM(vin) != ''
    AND TRIM(vin) != 'vin'
    AND mileage IS NOT NULL
    AND CAST(mileage AS REAL) >= 0
    AND "?" != '?'
    AND TRIM(vin) NOT IN (SELECT TRIM(vin) FROM vehicles WHERE vin IS NOT NULL)
),
numbered_customers AS (
  SELECT id as customer_id, ROW_NUMBER() OVER (ORDER BY RANDOM()) as customer_row_num
  FROM customers
),
customer_count AS (
  SELECT COUNT(*) as total_customers FROM customers
)
INSERT OR IGNORE INTO vehicles (customer_id, make, model, year, vin, license_plate, color, mileage, created_at)
SELECT 
  nc.customer_id,
  UPPER(SUBSTR(v.brand, 1, 1)) || LOWER(SUBSTR(v.brand, 2)) as make,
  UPPER(SUBSTR(v.model, 1, 1)) || LOWER(SUBSTR(v.model, 2)) as model,
  CAST(v.year AS INTEGER),
  TRIM(v.vin) as vin,
  'LP-' || SUBSTR(v.lot, -6) as license_plate,
  CASE 
    WHEN v.color IS NOT NULL AND v.color != '' THEN
      UPPER(SUBSTR(v.color, 1, 1)) || LOWER(SUBSTR(v.color, 2))
    ELSE 'Unknown'
  END as color,
  CAST(ROUND(CAST(v.mileage AS REAL)) AS INTEGER) as mileage,
  datetime('2024-01-01', '+' || (ABS(RANDOM()) % 365) || ' days', 
           '+' || (ABS(RANDOM()) % 24) || ' hours',
           '+' || (ABS(RANDOM()) % 60) || ' minutes') as created_at
FROM numbered_vehicles v
JOIN customer_count cc
JOIN numbered_customers nc
  ON ((v.vehicle_row_num - 1) % cc.total_customers) + 1 = nc.customer_row_num;
-- Clean up temporary table
DROP TABLE temp_vehicles_csv;