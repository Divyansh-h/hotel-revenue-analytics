/*
Purpose: Define views for seasonal demand tiers, daily cancellation rates, overbooking buffers, 
         and operational room-type mismatch rates (K5, K6).
Inputs:  hotel.v_monthly_kpis, hotel.bookings
Outputs: Views:
  - hotel.v_seasonality
  - hotel.v_daily_cancel_rates
  - hotel.v_overbooking_buffer
  - hotel.v_room_mismatch
Grain:   
  - hotel.v_seasonality: One row per hotel per calendar month number (1 to 12)
  - hotel.v_daily_cancel_rates: One row per hotel per arrival date (with arrivals >= 20)
  - hotel.v_overbooking_buffer: One row per hotel per arrival month number (1 to 12)
  - hotel.v_room_mismatch: One row per hotel per arrival month (arrival_month_start)
*/

-- ============================================================================
-- 1. View: hotel.v_seasonality
-- ============================================================================
-- Season assignment rule: NTILE(3) over avg_revpar descending within each hotel
-- partitions the 12 calendar months into 3 equal tiers of 4 months each:
-- 1 = 'Peak' (top 4 RevPAR months), 2 = 'Shoulder' (middle 4 RevPAR months), 3 = 'Low' (bottom 4 RevPAR months).

CREATE OR REPLACE VIEW hotel.v_seasonality AS
WITH monthly AS (
    SELECT
        hotel,
        EXTRACT(MONTH FROM month_start)::integer AS month_num,
        ROUND(AVG(occupancy_pct)::numeric, 2) AS avg_occupancy_pct,
        ROUND(AVG(adr)::numeric, 2) AS avg_adr,
        ROUND(AVG(revpar)::numeric, 2) AS avg_revpar,
        COUNT(*)::integer AS n_years_available
    FROM hotel.v_monthly_kpis
    GROUP BY hotel, EXTRACT(MONTH FROM month_start)
)
SELECT
    hotel,
    month_num,
    avg_occupancy_pct,
    avg_adr,
    avg_revpar,
    n_years_available,
    CASE NTILE(3) OVER (PARTITION BY hotel ORDER BY avg_revpar DESC)
        WHEN 1 THEN 'Peak'
        WHEN 2 THEN 'Shoulder'
        WHEN 3 THEN 'Low'
    END AS season
FROM monthly
ORDER BY hotel, month_num;


-- ============================================================================
-- 2. View: hotel.v_daily_cancel_rates
-- ============================================================================

CREATE OR REPLACE VIEW hotel.v_daily_cancel_rates AS
SELECT 
    hotel,
    arrival_date,
    COUNT(*)::bigint AS arrivals,
    SUM(is_canceled)::bigint AS cancelled_or_no_show,
    ROUND(SUM(is_canceled)::numeric / COUNT(*), 4) AS daily_cancel_rate
FROM hotel.bookings
GROUP BY hotel, arrival_date
HAVING COUNT(*) >= 20
ORDER BY hotel, arrival_date;


-- ============================================================================
-- 3. View: hotel.v_overbooking_buffer
-- ============================================================================
-- Note: This is a heuristic for discussion, not a policy, because cancellations
-- are only known after the fact and the dataset has no walk or compensation data.

CREATE OR REPLACE VIEW hotel.v_overbooking_buffer AS
WITH daily AS (
    SELECT 
        hotel,
        arrival_date,
        EXTRACT(MONTH FROM arrival_date)::integer AS month_num,
        daily_cancel_rate
    FROM hotel.v_daily_cancel_rates
)
SELECT 
    hotel,
    month_num,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY daily_cancel_rate)::numeric, 4) AS median_daily_cancel_rate,
    ROUND(PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY daily_cancel_rate)::numeric, 4) AS conservative_rate,
    COUNT(*)::integer AS days_observed
FROM daily
GROUP BY hotel, month_num
ORDER BY hotel, month_num;


-- ============================================================================
-- 4. View: hotel.v_room_mismatch
-- ============================================================================

CREATE OR REPLACE VIEW hotel.v_room_mismatch AS
SELECT
    hotel,
    arrival_month_start,
    COUNT(*)::bigint AS non_cancelled_bookings,
    SUM(room_type_mismatch)::bigint AS mismatched_rooms,
    ROUND(100.0 * SUM(room_type_mismatch)::numeric / NULLIF(COUNT(*), 0), 2) AS mismatch_pct
FROM hotel.bookings
WHERE is_canceled = 0
GROUP BY hotel, arrival_month_start
ORDER BY hotel, arrival_month_start;


-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: v_seasonality has exactly 24 rows
SELECT 
    'v_seasonality row count is 24' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '24' AS expected_value,
    CASE WHEN COUNT(*) = 24 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_seasonality;

-- Check 2: n_years_available matches real distinct years from daily_performance
WITH perf_years AS (
    SELECT 
        hotel,
        EXTRACT(MONTH FROM stay_date)::integer AS month_num,
        COUNT(DISTINCT EXTRACT(YEAR FROM stay_date))::integer AS expected_years
    FROM hotel.daily_performance
    GROUP BY hotel, EXTRACT(MONTH FROM stay_date)
)
SELECT 
    'n_years_available matches distinct years in daily_performance' AS check_name,
    COUNT(*)::bigint AS mismatch_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_seasonality s
JOIN perf_years p ON s.hotel = p.hotel AND s.month_num = p.month_num
WHERE s.n_years_available <> p.expected_years;

-- Check 3: Season labels split exactly 4/4/4 per hotel
SELECT 
    'Season labels split 4/4/4 per hotel' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT hotel, season, COUNT(*) AS tier_count
    FROM hotel.v_seasonality
    GROUP BY hotel, season
    HAVING COUNT(*) <> 4
) sub;

-- Check 4: Percentile values lie between 0 and 1
SELECT 
    'PERCENTILE values lie between 0 and 1' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_overbooking_buffer
WHERE median_daily_cancel_rate < 0 OR median_daily_cancel_rate > 1
   OR conservative_rate < 0 OR conservative_rate > 1;

-- Check 5: Mismatch counts reconcile with hotel.bookings
SELECT 
    'Room mismatch totals reconcile with hotel.bookings' AS check_name,
    v.sum_non_cancelled::text || ' non-canc | ' || v.sum_mismatched::text || ' mismatched' AS view_totals,
    b.tot_non_cancelled::text || ' non-canc | ' || b.tot_mismatched::text || ' mismatched' AS base_totals,
    CASE WHEN v.sum_non_cancelled = b.tot_non_cancelled AND v.sum_mismatched = b.tot_mismatched THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(non_cancelled_bookings)::bigint AS sum_non_cancelled, SUM(mismatched_rooms)::bigint AS sum_mismatched
    FROM hotel.v_room_mismatch
) v
CROSS JOIN (
    SELECT COUNT(*)::bigint AS tot_non_cancelled, SUM(room_type_mismatch)::bigint AS tot_mismatched
    FROM hotel.bookings
    WHERE is_canceled = 0
) b;

-- Output 1: First 30 rows of hotel.v_seasonality (all 24 rows)
SELECT * FROM hotel.v_seasonality ORDER BY hotel, month_num LIMIT 30;

-- Output 2: First 30 rows of hotel.v_daily_cancel_rates
SELECT * FROM hotel.v_daily_cancel_rates ORDER BY hotel, arrival_date LIMIT 30;

-- Output 3: First 30 rows of hotel.v_overbooking_buffer (all 24 rows)
SELECT * FROM hotel.v_overbooking_buffer ORDER BY hotel, month_num LIMIT 30;

-- Output 4: First 30 rows of hotel.v_room_mismatch
SELECT * FROM hotel.v_room_mismatch ORDER BY hotel, arrival_month_start LIMIT 30;
