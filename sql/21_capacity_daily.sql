/*
Purpose: Establish analytical window parameters (W1), derive hotel capacity from peak occupancy 
         with a 10% buffer (W2), and generate the canonical daily performance mart (hotel.daily_performance).
Inputs:  hotel.window_params, hotel.dim_date, hotel.stay_nights
Outputs: Tables hotel.window_params, hotel.capacity_derivation, hotel.capacity, hotel.daily_performance
Grain:   
  - hotel.window_params: One row with global analysis window parameters
  - hotel.capacity_derivation & hotel.capacity: One row per hotel
  - hotel.daily_performance: One row per hotel per calendar date inside the window (2015-08-01 to 2017-08-31)
*/

-- 1. Create hotel.window_params
DROP TABLE IF EXISTS hotel.window_params CASCADE;

CREATE TABLE hotel.window_params AS
SELECT
    '2015-08-01'::date AS window_start,
    '2017-08-31'::date AS window_end,
    1.10::numeric(4, 2) AS capacity_buffer;

-- 2. Create hotel.capacity_derivation
DROP TABLE IF EXISTS hotel.capacity_derivation CASCADE;

CREATE TABLE hotel.capacity_derivation AS
WITH wp AS (
    SELECT window_start, window_end, capacity_buffer FROM hotel.window_params
),
nightly AS (
    SELECT 
        sn.hotel,
        sn.stay_date,
        COUNT(*)::bigint AS rooms_sold
    FROM hotel.stay_nights sn
    CROSS JOIN wp
    WHERE sn.stay_date >= wp.window_start AND sn.stay_date <= wp.window_end
    GROUP BY sn.hotel, sn.stay_date
),
ranked AS (
    SELECT
        hotel,
        stay_date,
        rooms_sold,
        ROW_NUMBER() OVER (PARTITION BY hotel ORDER BY rooms_sold DESC, stay_date ASC) AS rn
    FROM nightly
),
hotel_stats AS (
    SELECT
        hotel,
        ROUND(AVG(rooms_sold)::numeric, 2) AS avg_rooms_sold_per_night
    FROM nightly
    GROUP BY hotel
)
SELECT 
    r.hotel,
    r.rooms_sold::integer AS peak_rooms_sold,
    r.stay_date AS peak_date,
    wp.capacity_buffer,
    (CEIL(r.rooms_sold::numeric * wp.capacity_buffer / 10.0) * 10)::integer AS capacity,
    s.avg_rooms_sold_per_night
FROM ranked r
JOIN hotel_stats s ON r.hotel = s.hotel
CROSS JOIN wp
WHERE r.rn = 1
ORDER BY r.hotel;

-- 3. Create hotel.capacity
DROP TABLE IF EXISTS hotel.capacity CASCADE;

CREATE TABLE hotel.capacity AS
SELECT
    hotel,
    capacity::integer AS rooms
FROM hotel.capacity_derivation
ORDER BY hotel;

ALTER TABLE hotel.capacity ADD PRIMARY KEY (hotel);

-- 4. Create hotel.daily_performance
DROP TABLE IF EXISTS hotel.daily_performance CASCADE;

CREATE TABLE hotel.daily_performance AS
WITH wp AS (
    SELECT window_start, window_end FROM hotel.window_params
),
calendar AS (
    SELECT 
        c.hotel,
        d.date_key AS stay_date,
        d.month_start,
        c.rooms AS rooms_available
    FROM hotel.dim_date d
    CROSS JOIN hotel.capacity c
    CROSS JOIN wp
    WHERE d.date_key >= wp.window_start AND d.date_key <= wp.window_end
),
nightly AS (
    SELECT 
        sn.hotel,
        sn.stay_date,
        COUNT(*)::integer AS rooms_sold,
        ROUND(SUM(sn.adr)::numeric, 2) AS room_revenue
    FROM hotel.stay_nights sn
    CROSS JOIN wp
    WHERE sn.stay_date >= wp.window_start AND sn.stay_date <= wp.window_end
    GROUP BY sn.hotel, sn.stay_date
)
SELECT 
    cal.hotel,
    cal.stay_date,
    cal.month_start,
    cal.rooms_available,
    COALESCE(n.rooms_sold, 0)::integer AS rooms_sold,
    COALESCE(n.room_revenue, 0.00)::numeric(12, 2) AS room_revenue
FROM calendar cal
LEFT JOIN nightly n ON cal.hotel = n.hotel AND cal.stay_date = n.stay_date
ORDER BY cal.hotel, cal.stay_date;

ALTER TABLE hotel.daily_performance ADD PRIMARY KEY (hotel, stay_date);

-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: daily_performance has (window_end - window_start + 1) x 2 rows (1,524 rows)
SELECT 
    'daily_performance row count is 1,524 (762 * 2)' AS check_name,
    COUNT(*)::bigint AS actual_value,
    ((wp.window_end - wp.window_start + 1) * 2)::text AS expected_value,
    CASE WHEN COUNT(*) = ((wp.window_end - wp.window_start + 1) * 2) THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.daily_performance dp
CROSS JOIN hotel.window_params wp
GROUP BY wp.window_start, wp.window_end;

-- Check 2: No row has rooms_sold > rooms_available
SELECT 
    'No row has rooms_sold > rooms_available' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.daily_performance
WHERE rooms_sold > rooms_available;

-- Check 3: Per hotel, MAX(rooms_sold) equals peak_rooms_sold
SELECT 
    dp.hotel || ' MAX(rooms_sold) equals peak_rooms_sold' AS check_name,
    MAX(dp.rooms_sold)::text AS actual_value,
    cd.peak_rooms_sold::text AS expected_value,
    CASE WHEN MAX(dp.rooms_sold) = cd.peak_rooms_sold THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.daily_performance dp
JOIN hotel.capacity_derivation cd ON dp.hotel = cd.hotel
GROUP BY dp.hotel, cd.peak_rooms_sold
ORDER BY dp.hotel;

-- Check 4: No duplicate (hotel, stay_date) in daily_performance
SELECT 
    'No duplicate (hotel, stay_date) in daily_performance' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT hotel, stay_date, COUNT(*) AS cnt
    FROM hotel.daily_performance
    GROUP BY hotel, stay_date
    HAVING COUNT(*) > 1
) sub;

-- Check 5: Per hotel, SUM(rooms_sold) equals stay_nights in window
SELECT 
    dp.hotel || ' SUM(rooms_sold) equals stay_nights in window' AS check_name,
    SUM(dp.rooms_sold)::text AS actual_value,
    sn_agg.stay_nights_count::text AS expected_value,
    CASE WHEN SUM(dp.rooms_sold) = sn_agg.stay_nights_count THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.daily_performance dp
JOIN (
    SELECT 
        sn.hotel,
        COUNT(*)::bigint AS stay_nights_count
    FROM hotel.stay_nights sn
    CROSS JOIN hotel.window_params wp
    WHERE sn.stay_date >= wp.window_start AND sn.stay_date <= wp.window_end
    GROUP BY sn.hotel
) sn_agg ON dp.hotel = sn_agg.hotel
GROUP BY dp.hotel, sn_agg.stay_nights_count
ORDER BY dp.hotel;

-- Display Capacity Derivation and Final Capacity Table
SELECT 
    hotel,
    peak_rooms_sold,
    peak_date,
    capacity_buffer,
    capacity,
    avg_rooms_sold_per_night
FROM hotel.capacity_derivation
ORDER BY hotel;

-- Display Share of Nights at or Above 90% of Capacity
SELECT 
    dp.hotel,
    c.rooms AS capacity,
    ROUND(c.rooms * 0.90, 1) AS threshold_90pct,
    COUNT(*) FILTER (WHERE dp.rooms_sold >= c.rooms * 0.90)::integer AS nights_ge_90pct,
    COUNT(*)::integer AS total_nights,
    ROUND((COUNT(*) FILTER (WHERE dp.rooms_sold >= c.rooms * 0.90)::numeric / COUNT(*)::numeric) * 100, 2) AS pct_nights_ge_90pct
FROM hotel.daily_performance dp
JOIN hotel.capacity c ON dp.hotel = c.hotel
GROUP BY dp.hotel, c.rooms
ORDER BY dp.hotel;
