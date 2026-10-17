/*
Purpose: Create view hotel.v_cancellation_drivers in long format across 12 analytical dimensions 
         evaluating cancellation rates, booking shares, and deviations from hotel averages (K5).
Inputs:  hotel.bookings
Outputs: View hotel.v_cancellation_drivers
Grain:   One row per hotel ('All', 'City Hotel', 'Resort Hotel') per dimension per category.

Design Choice Note on 'All' Hotel Rows:
We chose GROUPING SETS ((hotel, <category_cols>), (<category_cols>)) within each dimension block 
instead of UNION ALL. GROUPING SETS evaluates the individual hotel partitions and the portfolio total 
in a single aggregation pass over the table without duplicating scan/filter logic or maintaining 
redundant query copies for portfolio aggregates.
*/

CREATE OR REPLACE VIEW hotel.v_cancellation_drivers AS
WITH top_15_countries AS (
    SELECT country
    FROM hotel.bookings
    GROUP BY country
    ORDER BY COUNT(*) DESC
    LIMIT 15
),
base AS (
    SELECT
        hotel,
        is_canceled,
        is_no_show,
        lead_bucket,
        lead_bucket_order,
        deposit_type,
        market_segment,
        distribution_channel,
        customer_type,
        CASE 
            WHEN previous_cancellations = 0 THEN '0'
            WHEN previous_cancellations = 1 THEN '1'
            ELSE '2+'
        END AS previous_cancellations_bucket,
        CASE 
            WHEN is_repeated_guest = 1 THEN 'repeat guest'
            ELSE 'new guest'
        END AS is_repeated_guest,
        CASE 
            WHEN booking_changes = 0 THEN '0'
            WHEN booking_changes = 1 THEN '1'
            ELSE '2+'
        END AS booking_changes_bucket,
        CASE 
            WHEN required_car_parking_spaces > 0 THEN 'at least one'
            ELSE 'none'
        END AS required_car_parking,
        CASE 
            WHEN total_of_special_requests = 0 THEN '0'
            WHEN total_of_special_requests = 1 THEN '1'
            ELSE '2+'
        END AS special_requests_bucket,
        CASE 
            WHEN country IN (SELECT country FROM top_15_countries) THEN country
            ELSE 'Other'
        END AS country_top15,
        CASE 
            WHEN room_type_mismatch = 1 THEN 'different room type'
            ELSE 'same room type'
        END AS room_type_mismatch
    FROM hotel.bookings
),
blocks AS (
    -- 1. lead_bucket
    SELECT 
        COALESCE(hotel, 'All') AS hotel, 
        'lead_bucket' AS dimension, 
        lead_bucket AS category, 
        lead_bucket_order AS sort_order, 
        COUNT(*)::bigint AS bookings, 
        SUM(is_canceled)::bigint AS cancellations, 
        SUM(is_no_show)::bigint AS no_shows
    FROM base 
    GROUP BY GROUPING SETS ((hotel, lead_bucket, lead_bucket_order), (lead_bucket, lead_bucket_order))
    
    UNION ALL
    
    -- 2. deposit_type
    SELECT 
        COALESCE(hotel, 'All'), 
        'deposit_type', 
        deposit_type, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, deposit_type), (deposit_type))
    
    UNION ALL
    
    -- 3. market_segment
    SELECT 
        COALESCE(hotel, 'All'), 
        'market_segment', 
        market_segment, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, market_segment), (market_segment))
    
    UNION ALL
    
    -- 4. distribution_channel
    SELECT 
        COALESCE(hotel, 'All'), 
        'distribution_channel', 
        distribution_channel, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, distribution_channel), (distribution_channel))
    
    UNION ALL
    
    -- 5. customer_type
    SELECT 
        COALESCE(hotel, 'All'), 
        'customer_type', 
        customer_type, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, customer_type), (customer_type))
    
    UNION ALL
    
    -- 6. previous_cancellations_bucket
    SELECT 
        COALESCE(hotel, 'All'), 
        'previous_cancellations_bucket', 
        previous_cancellations_bucket, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, previous_cancellations_bucket), (previous_cancellations_bucket))
    
    UNION ALL
    
    -- 7. is_repeated_guest
    SELECT 
        COALESCE(hotel, 'All'), 
        'is_repeated_guest', 
        is_repeated_guest, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, is_repeated_guest), (is_repeated_guest))
    
    UNION ALL
    
    -- 8. booking_changes_bucket
    SELECT 
        COALESCE(hotel, 'All'), 
        'booking_changes_bucket', 
        booking_changes_bucket, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, booking_changes_bucket), (booking_changes_bucket))
    
    UNION ALL
    
    -- 9. required_car_parking
    SELECT 
        COALESCE(hotel, 'All'), 
        'required_car_parking', 
        required_car_parking, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, required_car_parking), (required_car_parking))
    
    UNION ALL
    
    -- 10. special_requests_bucket
    SELECT 
        COALESCE(hotel, 'All'), 
        'special_requests_bucket', 
        special_requests_bucket, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, special_requests_bucket), (special_requests_bucket))
    
    UNION ALL
    
    -- 11. country_top15
    SELECT 
        COALESCE(hotel, 'All'), 
        'country_top15', 
        country_top15, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, country_top15), (country_top15))
    
    UNION ALL
    
    -- 12. room_type_mismatch
    SELECT 
        COALESCE(hotel, 'All'), 
        'room_type_mismatch', 
        room_type_mismatch, 
        NULL::integer, 
        COUNT(*)::bigint, 
        SUM(is_canceled)::bigint, 
        SUM(is_no_show)::bigint 
    FROM base 
    GROUP BY GROUPING SETS ((hotel, room_type_mismatch), (room_type_mismatch))
)
SELECT
    hotel,
    dimension,
    category,
    sort_order,
    bookings,
    cancellations,
    no_shows,
    ROUND(100.0 * cancellations::numeric / NULLIF(bookings, 0), 1) AS cancel_rate_pct,
    ROUND(100.0 * bookings::numeric / SUM(bookings) OVER (PARTITION BY hotel, dimension), 1) AS share_of_bookings_pct,
    ROUND(
        (100.0 * cancellations::numeric / NULLIF(bookings, 0)) -
        (100.0 * SUM(cancellations) OVER (PARTITION BY hotel, dimension)::numeric / SUM(bookings) OVER (PARTITION BY hotel, dimension)),
        1
    ) AS cancel_rate_vs_hotel_avg_pp
FROM blocks;

-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: For every hotel and dimension, SUM(bookings) equals hotel total bookings (must return 0 rows)
SELECT 
    v.hotel,
    v.dimension,
    SUM(v.bookings)::bigint AS sum_bookings,
    b.expected_bookings,
    'VIOLATION' AS status
FROM hotel.v_cancellation_drivers v
JOIN (
    SELECT 'All' AS hotel, COUNT(*)::bigint AS expected_bookings FROM hotel.bookings
    UNION ALL
    SELECT hotel, COUNT(*)::bigint AS expected_bookings FROM hotel.bookings GROUP BY hotel
) b ON v.hotel = b.hotel
GROUP BY v.hotel, v.dimension, b.expected_bookings
HAVING SUM(v.bookings) <> b.expected_bookings;

-- Summary row for Check 1
SELECT 
    'Check 1: SUM(bookings) equals hotel total across all 36 (hotel, dim) slices' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT v.hotel, v.dimension
    FROM hotel.v_cancellation_drivers v
    JOIN (
        SELECT 'All' AS hotel, COUNT(*)::bigint AS expected_bookings FROM hotel.bookings
        UNION ALL
        SELECT hotel, COUNT(*)::bigint AS expected_bookings FROM hotel.bookings GROUP BY hotel
    ) b ON v.hotel = b.hotel
    GROUP BY v.hotel, v.dimension, b.expected_bookings
    HAVING SUM(v.bookings) <> b.expected_bookings
) sub;

-- Check 2: SUM(cancellations) per hotel and dimension equals hotel total cancellations (must return 0 rows)
SELECT 
    v.hotel,
    v.dimension,
    SUM(v.cancellations)::bigint AS sum_cancellations,
    b.expected_cancellations,
    'VIOLATION' AS status
FROM hotel.v_cancellation_drivers v
JOIN (
    SELECT 'All' AS hotel, SUM(is_canceled)::bigint AS expected_cancellations FROM hotel.bookings
    UNION ALL
    SELECT hotel, SUM(is_canceled)::bigint AS expected_cancellations FROM hotel.bookings GROUP BY hotel
) b ON v.hotel = b.hotel
GROUP BY v.hotel, v.dimension, b.expected_cancellations
HAVING SUM(v.cancellations) <> b.expected_cancellations;

-- Summary row for Check 2
SELECT 
    'Check 2: SUM(cancellations) equals hotel total across all 36 (hotel, dim) slices' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT v.hotel, v.dimension
    FROM hotel.v_cancellation_drivers v
    JOIN (
        SELECT 'All' AS hotel, SUM(is_canceled)::bigint AS expected_cancellations FROM hotel.bookings
        UNION ALL
        SELECT hotel, SUM(is_canceled)::bigint AS expected_cancellations FROM hotel.bookings GROUP BY hotel
    ) b ON v.hotel = b.hotel
    GROUP BY v.hotel, v.dimension, b.expected_cancellations
    HAVING SUM(v.cancellations) <> b.expected_cancellations
) sub;

-- Check 3: share_of_bookings_pct sums to 100 (tolerance 0.2) per hotel and dimension
SELECT 
    'Check 3: share_of_bookings_pct sums to 100 per hotel and dimension' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT hotel, dimension, SUM(share_of_bookings_pct) AS sum_share
    FROM hotel.v_cancellation_drivers
    GROUP BY hotel, dimension
    HAVING ABS(SUM(share_of_bookings_pct) - 100.0) > 0.2
) sub;

-- Check 4a: Top 5 categories by cancel_rate_pct (bookings >= 500, hotel = 'All')
SELECT 
    dimension,
    category,
    bookings,
    cancellations,
    cancel_rate_pct,
    share_of_bookings_pct,
    cancel_rate_vs_hotel_avg_pp
FROM hotel.v_cancellation_drivers
WHERE hotel = 'All' AND bookings >= 500
ORDER BY cancel_rate_pct DESC
LIMIT 5;

-- Check 4b: Bottom 5 categories by cancel_rate_pct (bookings >= 500, hotel = 'All')
SELECT 
    dimension,
    category,
    bookings,
    cancellations,
    cancel_rate_pct,
    share_of_bookings_pct,
    cancel_rate_vs_hotel_avg_pp
FROM hotel.v_cancellation_drivers
WHERE hotel = 'All' AND bookings >= 500
ORDER BY cancel_rate_pct ASC
LIMIT 5;
