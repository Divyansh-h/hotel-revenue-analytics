/*
Purpose: Generate individual stay-night records by expanding non-cancelled bookings 
         into calendar dates from arrival_date through checkout_date - 1 day (per K1).
Inputs:  hotel.bookings (where is_canceled = 0 AND total_nights > 0)
Outputs: Table hotel.stay_nights with primary key on (booking_id, stay_date) and index on (hotel, stay_date)
Grain:   One row per booking per calendar night stayed.
*/

DROP TABLE IF EXISTS hotel.stay_nights CASCADE;

CREATE TABLE hotel.stay_nights AS
SELECT
    b.booking_id,
    b.hotel,
    d::date AS stay_date,
    b.adr,
    b.market_segment,
    b.distribution_channel,
    b.customer_type,
    b.country,
    b.is_duplicate_row
FROM hotel.bookings b
CROSS JOIN LATERAL generate_series(b.arrival_date, b.checkout_date - interval '1 day', interval '1 day') AS d
WHERE b.is_canceled = 0 AND b.total_nights > 0;

ALTER TABLE hotel.stay_nights ADD PRIMARY KEY (booking_id, stay_date);
CREATE INDEX idx_stay_nights_hotel_date ON hotel.stay_nights (hotel, stay_date);

-- Check 1: Total stay nights count equals 255,030 (matches Phase 1 check 1f)
SELECT 
    'Total stay-nights count is 255,030' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '255030' AS expected_value,
    CASE WHEN COUNT(*) = 255030 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.stay_nights;

-- Check 2: Distinct booking_ids equals 74,485
SELECT 
    'Distinct bookings count is 74,485' AS check_name,
    COUNT(DISTINCT booking_id)::bigint AS actual_value,
    '74485' AS expected_value,
    CASE WHEN COUNT(DISTINCT booking_id) = 74485 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.stay_nights;

-- Check 3: SUM(adr) matches SUM(room_revenue) from non-cancelled bookings
SELECT 
    'SUM(adr) matches SUM(room_revenue)' AS check_name,
    ROUND(SUM(adr), 2)::text AS actual_value,
    ROUND((SELECT SUM(room_revenue) FROM hotel.bookings WHERE is_canceled = 0 AND total_nights > 0), 2)::text AS expected_value,
    CASE WHEN ROUND(SUM(adr), 2) = ROUND((SELECT SUM(room_revenue) FROM hotel.bookings WHERE is_canceled = 0 AND total_nights > 0), 2) THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.stay_nights;
