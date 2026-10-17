-- Phase 1 Analytical Integrity Checks
-- Database: hotel_analytics, Schema: hotel, Table: bookings

-- Check 1a: Total Bookings and Bookings by Hotel
SELECT 
    COALESCE(hotel, 'Total Portfolio') AS metric_label,
    COUNT(*)::bigint AS booking_count
FROM hotel.bookings
GROUP BY GROUPING SETS ((hotel), ())
ORDER BY (hotel IS NULL), hotel;

-- Check 1b: Cancellations, No-Shows, and Cancellation Rate by Hotel
SELECT
    hotel,
    COUNT(*)::bigint AS total_bookings,
    SUM(is_canceled)::bigint AS total_cancellations,
    SUM(is_no_show)::bigint AS total_no_shows,
    ROUND(AVG(is_canceled)::numeric, 4) AS cancellation_rate
FROM hotel.bookings
GROUP BY hotel
ORDER BY hotel;

-- Check 1c: Bookings per Arrival Month Start (Must be 26 months, 2015-07 to 2017-08)
SELECT
    arrival_month_start,
    COUNT(*)::bigint AS bookings_count
FROM hotel.bookings
GROUP BY arrival_month_start
ORDER BY arrival_month_start;

-- Check 1d: Rows per Lead Time Bucket (5 buckets, no NULL)
SELECT
    lead_bucket,
    lead_bucket_order,
    COUNT(*)::bigint AS row_count
FROM hotel.bookings
GROUP BY lead_bucket, lead_bucket_order
ORDER BY lead_bucket_order;

-- Check 1e: Total Nights Integrity Violations (Must be exactly 0)
SELECT
    'total_nights <> weekend + week nights' AS check_name,
    COUNT(*)::bigint AS violation_count
FROM hotel.bookings
WHERE total_nights <> stays_in_weekend_nights + stays_in_week_nights;

-- Check 1f: Non-Cancelled Stays with Positive Nights and Total Stay Nights (Phase 2 inputs)
SELECT
    'Non-Cancelled Stays (total_nights > 0)' AS metric_label,
    COUNT(*)::bigint AS non_cancelled_stays_count,
    SUM(total_nights)::bigint AS sum_total_stay_nights
FROM hotel.bookings
WHERE is_canceled = 0 AND total_nights > 0;
