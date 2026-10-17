/*
Purpose: Define stay-night KPI views (v_monthly_kpis, v_hotel_totals, v_yearly_kpis)
         computing room-nights sold, room-nights available, room revenue, occupancy %, ADR, and RevPAR (K1 to K4).
Inputs:  hotel.daily_performance
Outputs: Views hotel.v_monthly_kpis, hotel.v_hotel_totals, hotel.v_yearly_kpis
Grain:   
  - hotel.v_monthly_kpis: One row per hotel per stay month (month_start)
  - hotel.v_hotel_totals: One row per hotel across reliable window plus 'All hotels' total
  - hotel.v_yearly_kpis: One row per hotel per calendar year with coverage notes
*/

-- 1. View: hotel.v_monthly_kpis
CREATE OR REPLACE VIEW hotel.v_monthly_kpis AS
SELECT
    hotel,
    month_start,
    SUM(rooms_sold)::bigint AS room_nights_sold,
    SUM(rooms_available)::bigint AS room_nights_available,
    ROUND(SUM(room_revenue), 2) AS room_revenue,
    ROUND(100.0 * SUM(rooms_sold)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS occupancy_pct,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_sold), 0), 2) AS adr,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS revpar
FROM hotel.daily_performance
GROUP BY hotel, month_start
ORDER BY hotel, month_start;

-- 2. View: hotel.v_hotel_totals
CREATE OR REPLACE VIEW hotel.v_hotel_totals AS
SELECT
    COALESCE(hotel, 'All hotels') AS hotel,
    SUM(rooms_sold)::bigint AS room_nights_sold,
    SUM(rooms_available)::bigint AS room_nights_available,
    ROUND(SUM(room_revenue), 2) AS room_revenue,
    ROUND(100.0 * SUM(rooms_sold)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS occupancy_pct,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_sold), 0), 2) AS adr,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS revpar
FROM hotel.daily_performance
GROUP BY GROUPING SETS ((hotel), ())
ORDER BY (hotel IS NULL), hotel;

-- 3. View: hotel.v_yearly_kpis
CREATE OR REPLACE VIEW hotel.v_yearly_kpis AS
SELECT
    hotel,
    EXTRACT(YEAR FROM stay_date)::integer AS year,
    CASE 
        WHEN EXTRACT(YEAR FROM stay_date) = 2015 THEN 'Partial year (Aug-Dec)'
        WHEN EXTRACT(YEAR FROM stay_date) = 2016 THEN 'Full year'
        WHEN EXTRACT(YEAR FROM stay_date) = 2017 THEN 'Partial year (Jan-Aug)'
    END AS coverage_note,
    SUM(rooms_sold)::bigint AS room_nights_sold,
    SUM(rooms_available)::bigint AS room_nights_available,
    ROUND(SUM(room_revenue), 2) AS room_revenue,
    ROUND(100.0 * SUM(rooms_sold)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS occupancy_pct,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_sold), 0), 2) AS adr,
    ROUND(SUM(room_revenue)::numeric / NULLIF(SUM(rooms_available), 0), 2) AS revpar
FROM hotel.daily_performance
GROUP BY hotel, EXTRACT(YEAR FROM stay_date)
ORDER BY hotel, year;

-- ============================================================================
-- VALIDATION CHECKS
-- ============================================================================

-- Check 1: v_monthly_kpis has 50 rows (25 months x 2 hotels)
SELECT 
    'v_monthly_kpis row count is 50' AS check_name,
    COUNT(*)::bigint AS actual_value,
    '50' AS expected_value,
    CASE WHEN COUNT(*) = 50 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_monthly_kpis;

-- Check 2: RevPAR identity on every row: ABS(revpar - adr * occupancy_pct / 100) < 0.05
SELECT 
    'RevPAR identity check: ABS(revpar - adr * occupancy_pct / 100) < 0.05' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_monthly_kpis
WHERE ABS(revpar - (adr * occupancy_pct / 100.0)) >= 0.05;

-- List any violating rows (empty if PASS)
SELECT 
    hotel,
    month_start,
    occupancy_pct,
    adr,
    revpar,
    ROUND(ABS(revpar - (adr * occupancy_pct / 100.0)), 4) AS identity_diff
FROM hotel.v_monthly_kpis
WHERE ABS(revpar - (adr * occupancy_pct / 100.0)) >= 0.05;

-- Check 3: occupancy_pct is between 0 and 100 on every row
SELECT 
    'occupancy_pct between 0 and 100 on every row' AS check_name,
    COUNT(*)::bigint AS violation_count,
    '0' AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM hotel.v_monthly_kpis
WHERE occupancy_pct < 0 OR occupancy_pct > 100;

-- Check 4: SUM(room_nights_sold) and SUM(room_revenue) match daily_performance
SELECT 
    'SUM(room_nights_sold) and SUM(room_revenue) match daily_performance' AS check_name,
    v.sum_sold::text || ' sold | $' || v.sum_rev::text AS view_values,
    d.sum_sold::text || ' sold | $' || d.sum_rev::text AS daily_values,
    CASE WHEN v.sum_sold = d.sum_sold AND v.sum_rev = d.sum_rev THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(room_nights_sold)::bigint AS sum_sold, ROUND(SUM(room_revenue), 2) AS sum_rev 
    FROM hotel.v_monthly_kpis
) v
CROSS JOIN (
    SELECT SUM(rooms_sold)::bigint AS sum_sold, ROUND(SUM(room_revenue), 2) AS sum_rev 
    FROM hotel.daily_performance
) d;

-- Check 5a: Top 10 highest hotel-months by revpar
SELECT 
    hotel,
    month_start,
    occupancy_pct,
    adr,
    revpar
FROM hotel.v_monthly_kpis
ORDER BY revpar DESC
LIMIT 10;

-- Check 5b: Top 10 lowest hotel-months by revpar
SELECT 
    hotel,
    month_start,
    occupancy_pct,
    adr,
    revpar
FROM hotel.v_monthly_kpis
ORDER BY revpar ASC
LIMIT 10;
