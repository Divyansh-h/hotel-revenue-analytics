/*
Purpose: (Re)create the canonical calendar date dimension table (hotel.dim_date) 
         for daily occupancy, arrival, and checkout reporting.
Inputs:  generate_series('2015-01-01'::date, '2017-12-31'::date, interval '1 day')
Outputs: Table hotel.dim_date with primary key on date_key.
Grain:   One row per calendar day.
*/

DROP TABLE IF EXISTS hotel.dim_date CASCADE;

CREATE TABLE hotel.dim_date AS
SELECT
    d::date AS date_key,
    EXTRACT(YEAR FROM d)::integer AS year,
    EXTRACT(QUARTER FROM d)::integer AS quarter,
    EXTRACT(MONTH FROM d)::integer AS month_num,
    TO_CHAR(d, 'Mon') AS month_short,
    TO_CHAR(d, 'FMMonth') AS month_name,
    DATE_TRUNC('month', d)::date AS month_start,
    TO_CHAR(d, 'YYYY-MM') AS year_month,
    EXTRACT(DAY FROM d)::integer AS day_of_month,
    EXTRACT(ISODOW FROM d)::integer AS iso_weekday
FROM generate_series('2015-01-01'::date, '2017-12-31'::date, interval '1 day') AS d;

ALTER TABLE hotel.dim_date ADD PRIMARY KEY (date_key);

-- Check 1: Total row count is 1,096 (365 + 366 + 365)
SELECT 
    'Total row count is 1,096' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '1096' AS expected_value,
    CASE WHEN COUNT(*) = 1096 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.dim_date;

-- Check 2: No gaps in date range
SELECT 
    'No gaps in date range' AS check_name,
    (MAX(date_key) - MIN(date_key) + 1)::bigint AS actual_value,
    COUNT(*)::text AS expected_value,
    CASE WHEN (MAX(date_key) - MIN(date_key) + 1) = COUNT(*) THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.dim_date;

-- Check 3: 2016 leap year has 366 rows
SELECT 
    '2016 has 366 rows' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '366' AS expected_value,
    CASE WHEN COUNT(*) = 366 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.dim_date
WHERE year = 2016;

-- Check 4: Every arrival_date and checkout_date in hotel.bookings exists in dim_date
SELECT 
    'All arrival and checkout dates exist in dim_date' AS check_name,
    COUNT(*)::bigint AS missing_rows,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.bookings b
WHERE NOT EXISTS (SELECT 1 FROM hotel.dim_date d WHERE d.date_key = b.arrival_date)
   OR NOT EXISTS (SELECT 1 FROM hotel.dim_date d WHERE d.date_key = b.checkout_date);
