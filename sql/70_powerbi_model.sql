/*
Purpose: Create Power BI dimensional star schema tables in schema hotel (Phase 4).
Inputs:  hotel.dim_date, hotel.capacity, hotel.bookings, hotel.stay_nights, hotel.window_params, hotel.daily_performance
Outputs: Tables:
  - hotel.dim_date (date_key, year, quarter, month_num, month_short, month_name, month_start, year_month)
  - hotel.dim_hotel (hotel_key, hotel, rooms_capacity)
  - hotel.dim_profile (profile_key, market_segment, distribution_channel, customer_type, deposit_type)
  - hotel.fact_bookings (grain: 1 booking; 24 columns)
  - hotel.fact_stay_nights (grain: 1 booking-night inside window; 5 columns)
  - hotel.fact_capacity (grain: hotel x date inside window; 3 columns)
*/

-- -----------------------------------------------------------------------------
-- 1. Table: hotel.dim_date
-- -----------------------------------------------------------------------------
CREATE TEMP TABLE temp_source_dim_date AS
SELECT
    date_key,
    year,
    quarter,
    month_num,
    month_short,
    month_name,
    month_start,
    year_month
FROM hotel.dim_date;

DROP TABLE IF EXISTS hotel.dim_date CASCADE;

CREATE TABLE hotel.dim_date AS
SELECT * FROM temp_source_dim_date;

ALTER TABLE hotel.dim_date ADD PRIMARY KEY (date_key);

-- -----------------------------------------------------------------------------
-- 2. Table: hotel.dim_hotel
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS hotel.dim_hotel CASCADE;

CREATE TABLE hotel.dim_hotel AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.hotel)::integer AS hotel_key,
    c.hotel,
    c.rooms::integer AS rooms_capacity
FROM hotel.capacity c
ORDER BY hotel_key;

ALTER TABLE hotel.dim_hotel ADD PRIMARY KEY (hotel_key);

-- -----------------------------------------------------------------------------
-- 3. Table: hotel.dim_profile (Junk Dimension)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS hotel.dim_profile CASCADE;

CREATE TABLE hotel.dim_profile AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY market_segment, distribution_channel, customer_type, deposit_type
    )::integer AS profile_key,
    market_segment,
    distribution_channel,
    customer_type,
    deposit_type
FROM (
    SELECT DISTINCT
        market_segment,
        distribution_channel,
        customer_type,
        deposit_type
    FROM hotel.bookings
) sub
ORDER BY profile_key;

ALTER TABLE hotel.dim_profile ADD PRIMARY KEY (profile_key);

-- -----------------------------------------------------------------------------
-- 4. Table: hotel.fact_bookings
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS hotel.fact_bookings CASCADE;

CREATE TABLE hotel.fact_bookings AS
SELECT
    b.booking_id,
    h.hotel_key,
    p.profile_key,
    b.arrival_date,
    b.is_canceled,
    b.is_no_show,
    b.reservation_status,
    b.lead_time,
    b.lead_bucket,
    b.lead_bucket_order,
    b.total_nights,
    b.total_guests,
    b.country,
    b.adr,
    b.room_revenue,
    b.is_repeated_guest,
    b.previous_cancellations,
    b.booking_changes,
    b.total_of_special_requests AS special_requests,
    b.room_type_mismatch,
    b.days_cancelled_before_arrival,
    CASE 
        WHEN b.reservation_status = 'Canceled' THEN
            CASE 
                WHEN b.days_cancelled_before_arrival <= 1 THEN '0-1 days'
                WHEN b.days_cancelled_before_arrival <= 7 THEN '2-7 days'
                WHEN b.days_cancelled_before_arrival <= 14 THEN '8-14 days'
                WHEN b.days_cancelled_before_arrival <= 30 THEN '15-30 days'
                WHEN b.days_cancelled_before_arrival <= 60 THEN '31-60 days'
                WHEN b.days_cancelled_before_arrival <= 90 THEN '61-90 days'
                ELSE '91+ days'
            END
        ELSE NULL
    END AS cancel_timing_bucket,
    CASE 
        WHEN b.reservation_status = 'Canceled' THEN
            CASE 
                WHEN b.days_cancelled_before_arrival <= 1 THEN 1
                WHEN b.days_cancelled_before_arrival <= 7 THEN 2
                WHEN b.days_cancelled_before_arrival <= 14 THEN 3
                WHEN b.days_cancelled_before_arrival <= 30 THEN 4
                WHEN b.days_cancelled_before_arrival <= 60 THEN 5
                WHEN b.days_cancelled_before_arrival <= 90 THEN 6
                ELSE 7
            END
        ELSE NULL
    END::integer AS cancel_timing_order,
    b.is_duplicate_row
FROM hotel.bookings b
JOIN hotel.dim_hotel h 
    ON b.hotel = h.hotel
JOIN hotel.dim_profile p 
    ON b.market_segment = p.market_segment
   AND b.distribution_channel = p.distribution_channel
   AND b.customer_type = p.customer_type
   AND b.deposit_type = p.deposit_type
ORDER BY b.booking_id;

ALTER TABLE hotel.fact_bookings ADD PRIMARY KEY (booking_id);
CREATE INDEX idx_fact_bookings_arrival_date ON hotel.fact_bookings (arrival_date);
CREATE INDEX idx_fact_bookings_hotel_key ON hotel.fact_bookings (hotel_key);
CREATE INDEX idx_fact_bookings_profile_key ON hotel.fact_bookings (profile_key);

-- -----------------------------------------------------------------------------
-- 5. Table: hotel.fact_stay_nights
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS hotel.fact_stay_nights CASCADE;

CREATE TABLE hotel.fact_stay_nights AS
SELECT
    sn.booking_id,
    h.hotel_key,
    p.profile_key,
    sn.stay_date,
    sn.adr
FROM hotel.stay_nights sn
JOIN hotel.bookings b 
    ON sn.booking_id = b.booking_id
JOIN hotel.dim_hotel h 
    ON b.hotel = h.hotel
JOIN hotel.dim_profile p 
    ON b.market_segment = p.market_segment
   AND b.distribution_channel = p.distribution_channel
   AND b.customer_type = p.customer_type
   AND b.deposit_type = p.deposit_type
CROSS JOIN hotel.window_params wp
WHERE sn.stay_date >= wp.window_start 
  AND sn.stay_date <= wp.window_end
ORDER BY sn.booking_id, sn.stay_date;

ALTER TABLE hotel.fact_stay_nights ADD PRIMARY KEY (booking_id, stay_date);
CREATE INDEX idx_fact_stay_nights_stay_date ON hotel.fact_stay_nights (stay_date);
CREATE INDEX idx_fact_stay_nights_hotel_key ON hotel.fact_stay_nights (hotel_key);
CREATE INDEX idx_fact_stay_nights_profile_key ON hotel.fact_stay_nights (profile_key);

-- -----------------------------------------------------------------------------
-- 6. Table: hotel.fact_capacity
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS hotel.fact_capacity CASCADE;

CREATE TABLE hotel.fact_capacity AS
SELECT
    h.hotel_key,
    dp.stay_date AS date_key,
    dp.rooms_available
FROM hotel.daily_performance dp
JOIN hotel.dim_hotel h 
    ON dp.hotel = h.hotel
ORDER BY h.hotel_key, dp.stay_date;

ALTER TABLE hotel.fact_capacity ADD PRIMARY KEY (hotel_key, date_key);

-- -----------------------------------------------------------------------------
-- Integrity Verification Queries
-- -----------------------------------------------------------------------------
SELECT 
    'dim_hotel count' AS check_name, 
    COUNT(*)::bigint AS actual_count, 
    2::bigint AS expected_count,
    CASE WHEN COUNT(*) = 2 THEN 'PASS' ELSE 'FAIL' END AS status 
FROM hotel.dim_hotel
UNION ALL
SELECT 
    'dim_date count', 
    COUNT(*), 
    1096, 
    CASE WHEN COUNT(*) = 1096 THEN 'PASS' ELSE 'FAIL' END 
FROM hotel.dim_date
UNION ALL
SELECT 
    'dim_profile count', 
    COUNT(*), 
    101, 
    CASE WHEN COUNT(*) = 101 THEN 'PASS' ELSE 'FAIL' END 
FROM hotel.dim_profile
UNION ALL
SELECT 
    'fact_bookings count', 
    COUNT(*), 
    (SELECT COUNT(*) FROM hotel.bookings),
    CASE WHEN COUNT(*) = (SELECT COUNT(*) FROM hotel.bookings) THEN 'PASS' ELSE 'FAIL' END 
FROM hotel.fact_bookings
UNION ALL
SELECT 
    'fact_bookings null keys', 
    COUNT(*), 
    0, 
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM hotel.fact_bookings 
WHERE hotel_key IS NULL OR profile_key IS NULL
UNION ALL
SELECT 
    'fact_stay_nights count', 
    COUNT(*), 
    248261, 
    CASE WHEN COUNT(*) = 248261 THEN 'PASS' ELSE 'FAIL' END 
FROM hotel.fact_stay_nights
UNION ALL
SELECT 
    'fact_stay_nights null keys', 
    COUNT(*), 
    0, 
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM hotel.fact_stay_nights 
WHERE hotel_key IS NULL OR profile_key IS NULL
UNION ALL
SELECT 
    'fact_capacity count', 
    COUNT(*), 
    1524, 
    CASE WHEN COUNT(*) = 1524 THEN 'PASS' ELSE 'FAIL' END 
FROM hotel.fact_capacity
UNION ALL
SELECT 
    'fact_capacity null keys', 
    COUNT(*), 
    0, 
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM hotel.fact_capacity 
WHERE hotel_key IS NULL OR date_key IS NULL;
