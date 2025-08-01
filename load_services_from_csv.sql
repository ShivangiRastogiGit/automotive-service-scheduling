-- Description: Load service data from Service_Type.csv

PRAGMA foreign_keys = ON;

-- Display current service count before loading
SELECT 'Current services in database before loading:' as message;
SELECT COUNT(*) as count FROM services;

-- First get unique repair descriptions with their average cost
INSERT OR IGNORE INTO services (name, description, estimated_duration, price, is_active)
SELECT 
    -- Map Repair Description to name
    repair_description as name,
    -- Auto-generate description based on repair type and parts
    CASE 
        WHEN parts_replaced IS NOT NULL AND parts_replaced != '' THEN
            'Professional ' || repair_description || ' service including parts replacement. Quality parts and expert workmanship guaranteed.'
        ELSE
            'Professional ' || repair_description || ' service with thorough inspection and quality workmanship. All work comes with warranty.'
    END as description,
    -- Auto-generate estimated_duration based on service type (in minutes)
    CASE 
        WHEN repair_description LIKE '%Oil%' OR repair_description LIKE '%Filter%' THEN 30
        WHEN repair_description LIKE '%Tire%' OR repair_description LIKE '%Wheel%' THEN 45
        WHEN repair_description LIKE '%Battery%' OR repair_description LIKE '%Spark%' THEN 30
        WHEN repair_description LIKE '%Brake%' THEN 90
        WHEN repair_description LIKE '%Transmission%' OR repair_description LIKE '%Engine%' THEN 240
        WHEN repair_description LIKE '%Suspension%' OR repair_description LIKE '%Steering%' THEN 120
        WHEN repair_description LIKE '%AC%' OR repair_description LIKE '%Air%' THEN 60
        WHEN repair_description LIKE '%Exhaust%' OR repair_description LIKE '%Muffler%' THEN 75
        WHEN repair_description LIKE '%Alignment%' THEN 60
        WHEN repair_description LIKE '%Inspection%' OR repair_description LIKE '%Diagnostic%' THEN 45
        ELSE 
            CASE 
                WHEN AVG(cost) < 100 THEN 30
                WHEN AVG(cost) BETWEEN 100 AND 500 THEN 60
                WHEN AVG(cost) BETWEEN 500 AND 1000 THEN 90
                WHEN AVG(cost) BETWEEN 1000 AND 2000 THEN 150
                ELSE 180
            END
    END as estimated_duration,
    -- Map Cost to price (use average cost for duplicate repair types)
    ROUND(AVG(cost), 2) as price,
    -- Set all services as active
    1 as is_active
FROM temp_services_csv
WHERE repair_description IS NOT NULL 
  AND repair_description != ''
  AND repair_description != 'Repair Description'  -- Skip header row
  AND cost IS NOT NULL
  AND cost > 0
GROUP BY repair_description;

-- Display results
SELECT 'Service loading completed!' as message;
SELECT COUNT(*) as total_services_after FROM services;

-- Show sample of loaded services
SELECT 'Sample of recent services:' as sample_header;
SELECT name, description, estimated_duration, price 
FROM services 
ORDER BY id DESC 
LIMIT 5;

-- Show service statistics by type
SELECT 'Service statistics:' as stats_header;
SELECT 
    CASE 
        WHEN name LIKE '%Oil%' THEN 'Oil Change Services'
        WHEN name LIKE '%Tire%' THEN 'Tire Services'
        WHEN name LIKE '%Brake%' THEN 'Brake Services'
        WHEN name LIKE '%Transmission%' THEN 'Transmission Services'
        WHEN name LIKE '%Engine%' THEN 'Engine Services'
        WHEN name LIKE '%Suspension%' THEN 'Suspension Services'
        WHEN name LIKE '%Battery%' THEN 'Battery Services'
        ELSE 'Other Services'
    END as service_category,
    COUNT(*) as service_count,
    AVG(price) as avg_price,
    AVG(estimated_duration) as avg_duration
FROM services
GROUP BY service_category
ORDER BY service_count DESC;

-- Clean up temporary table
DROP TABLE temp_services_csv;