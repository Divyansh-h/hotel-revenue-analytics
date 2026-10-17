/*
Purpose: Define booking trend analytics view (hotel.v_booking_trends) computing monthly booking volumes,
         cancellation and no-show rates, stay conversion (K5, K6), lead times, MoM/YoY growth, 3-month rolling 
         cancellation averages, and cumulative volume over all 26 arrival months.
Inputs:  hotel.bookings
Outputs: View hotel.v_booking_trends
Grain:   One row per hotel per arrival month (arrival_month_start)
*/

-- Note: revenue_mom_pct here is by arrival month and differs from stay-month revenue in v_monthly_kpis. Both are valid; they answer different questions.

CREATE OR REPLACE VIEW hotel.v_booking_trends AS
WITH monthly AS (
    SELECT
        hotel,
        arrival_month_start,
        COUNT(*)::bigint AS bookings,
        SUM(is_canceled)::bigint AS cancellations,
        SUM(is_no_show)::bigint AS no_shows,
        ROUND(100.0 * SUM(is_canceled)::numeric / NULLIF(COUNT(*), 0), 1) AS cancel_rate_pct,
        ROUND(100.0 * SUM(is_no_show)::numeric / NULLIF(COUNT(*), 0), 1) AS no_show_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN reservation_status = 'Check-Out' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0), 1) AS stay_conversion_pct,
        ROUND(AVG(lead_time)::numeric, 1) AS avg_lead_time,
        ROUND(SUM(CASE WHEN is_canceled = 0 THEN room_revenue ELSE 0 END)::numeric, 2) AS room_revenue,
        SUM(CASE WHEN is_canceled = 0 THEN total_nights ELSE 0 END)::bigint AS room_nights
    FROM hotel.bookings
    GROUP BY hotel, arrival_month_start
)
SELECT
    hotel,
    arrival_month_start,
    bookings,
    cancellations,
    no_shows,
    cancel_rate_pct,
    no_show_rate_pct,
    stay_conversion_pct,
    avg_lead_time,
    room_revenue,
    room_nights,
    LAG(bookings, 1) OVER (PARTITION BY hotel ORDER BY arrival_month_start) AS bookings_prev_month,
    ROUND(100.0 * (bookings - LAG(bookings, 1) OVER (PARTITION BY hotel ORDER BY arrival_month_start))::numeric 
          / NULLIF(LAG(bookings, 1) OVER (PARTITION BY hotel ORDER BY arrival_month_start), 0), 1) AS bookings_mom_pct,
    ROUND(100.0 * (room_revenue - LAG(room_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_month_start))::numeric 
          / NULLIF(LAG(room_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_month_start), 0), 1) AS revenue_mom_pct,
    ROUND(100.0 * (bookings - LAG(bookings, 12) OVER (PARTITION BY hotel ORDER BY arrival_month_start))::numeric 
          / NULLIF(LAG(bookings, 12) OVER (PARTITION BY hotel ORDER BY arrival_month_start), 0), 1) AS bookings_yoy_pct,
    ROUND(AVG(cancel_rate_pct) OVER (PARTITION BY hotel ORDER BY arrival_month_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS cancel_rate_3m_avg,
    SUM(bookings) OVER (PARTITION BY hotel ORDER BY arrival_month_start ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)::bigint AS cumulative_bookings
FROM monthly
ORDER BY hotel, arrival_month_start;

-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: 52 rows (26 months x 2 hotels) with no missing month per hotel
SELECT 
    '52 rows (26 months x 2 hotels) with no missing months' AS check_name,
    COUNT(v.arrival_month_start)::bigint AS actual_rows,
    '52' AS expected_rows,
    CASE WHEN COUNT(v.arrival_month_start) = 52 AND COUNT(e.m) = 52 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT DISTINCT hotel FROM hotel.bookings
) h
CROSS JOIN generate_series('2015-07-01'::date, '2017-08-01'::date, interval '1 month') AS e(m)
LEFT JOIN hotel.v_booking_trends v 
    ON h.hotel = v.hotel AND e.m::date = v.arrival_month_start;

-- Check 2: SUM(bookings) equals total bookings; SUM(cancellations) equals SUM(is_canceled)
SELECT 
    'SUM(bookings) and SUM(cancellations) match hotel.bookings' AS check_name,
    v.sum_bookings::text || ' bookings | ' || v.sum_canc::text || ' cancellations' AS view_totals,
    b.tot_bookings::text || ' bookings | ' || b.tot_canc::text || ' cancellations' AS base_totals,
    CASE WHEN v.sum_bookings = b.tot_bookings AND v.sum_canc = b.tot_canc THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(bookings)::bigint AS sum_bookings, SUM(cancellations)::bigint AS sum_canc 
    FROM hotel.v_booking_trends
) v
CROSS JOIN (
    SELECT COUNT(*)::bigint AS tot_bookings, SUM(is_canceled)::bigint AS tot_canc 
    FROM hotel.bookings
) b;

-- Check 3: cancel_rate_pct + stay_conversion_pct = 100 on every row (tolerance 0.15)
SELECT 
    'cancel_rate_pct + stay_conversion_pct = 100 on every row' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_booking_trends
WHERE ABS((cancel_rate_pct + stay_conversion_pct) - 100.0) > 0.15;

-- Check 4: MoM is NULL for month 1; YoY is NULL for months 1-12 and non-null for months 13-26
WITH ranked AS (
    SELECT 
        hotel,
        arrival_month_start,
        ROW_NUMBER() OVER (PARTITION BY hotel ORDER BY arrival_month_start) AS month_idx,
        bookings_mom_pct,
        revenue_mom_pct,
        bookings_yoy_pct
    FROM hotel.v_booking_trends
)
SELECT 
    'MoM NULL on month 1, YoY NULL on months 1-12' AS check_name,
    COUNT(*) FILTER (WHERE month_idx = 1 AND (bookings_mom_pct IS NOT NULL OR revenue_mom_pct IS NOT NULL))::bigint AS mom_violations,
    COUNT(*) FILTER (WHERE month_idx <= 12 AND bookings_yoy_pct IS NOT NULL)::bigint AS yoy_null_violations,
    COUNT(*) FILTER (WHERE month_idx > 12 AND bookings_yoy_pct IS NULL)::bigint AS yoy_valid_violations,
    CASE WHEN COUNT(*) FILTER (WHERE month_idx = 1 AND (bookings_mom_pct IS NOT NULL OR revenue_mom_pct IS NOT NULL)) = 0
              AND COUNT(*) FILTER (WHERE month_idx <= 12 AND bookings_yoy_pct IS NOT NULL) = 0
              AND COUNT(*) FILTER (WHERE month_idx > 12 AND bookings_yoy_pct IS NULL) = 0
         THEN 'PASS' ELSE 'FAIL' END AS status
FROM ranked;

-- Check 5: Recompute two hotel-months with a separate plain query and compare against view
WITH plain_recalc AS (
    SELECT 
        hotel,
        arrival_month_start,
        COUNT(*)::bigint AS plain_bookings,
        SUM(is_canceled)::bigint AS plain_cancellations,
        SUM(is_no_show)::bigint AS plain_no_shows,
        ROUND(100.0 * SUM(is_canceled)::numeric / COUNT(*), 1) AS plain_cancel_rate,
        ROUND(100.0 * SUM(CASE WHEN reservation_status = 'Check-Out' THEN 1 ELSE 0 END)::numeric / COUNT(*), 1) AS plain_conversion,
        ROUND(AVG(lead_time)::numeric, 1) AS plain_lead_time,
        ROUND(SUM(CASE WHEN is_canceled = 0 THEN room_revenue ELSE 0 END)::numeric, 2) AS plain_revenue,
        SUM(CASE WHEN is_canceled = 0 THEN total_nights ELSE 0 END)::bigint AS plain_nights
    FROM hotel.bookings
    WHERE (hotel = 'City Hotel' AND arrival_month_start = '2016-09-01')
       OR (hotel = 'Resort Hotel' AND arrival_month_start = '2017-03-01')
    GROUP BY hotel, arrival_month_start
)
SELECT 
    v.hotel,
    v.arrival_month_start,
    v.bookings AS view_bookings,
    p.plain_bookings,
    v.cancellations AS view_cancellations,
    p.plain_cancellations,
    v.cancel_rate_pct AS view_cancel_rate,
    p.plain_cancel_rate,
    v.stay_conversion_pct AS view_conversion,
    p.plain_conversion,
    v.room_revenue AS view_revenue,
    p.plain_revenue,
    v.room_nights AS view_nights,
    p.plain_nights,
    CASE WHEN v.bookings = p.plain_bookings 
              AND v.cancellations = p.plain_cancellations
              AND v.cancel_rate_pct = p.plain_cancel_rate
              AND v.stay_conversion_pct = p.plain_conversion
              AND v.room_revenue = p.plain_revenue
              AND v.room_nights = p.plain_nights
         THEN 'PASS' ELSE 'FAIL' END AS comparison_status
FROM hotel.v_booking_trends v
JOIN plain_recalc p ON v.hotel = p.hotel AND v.arrival_month_start = p.arrival_month_start
ORDER BY v.hotel;
