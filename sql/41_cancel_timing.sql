/*
Purpose: Define cancellation timing, lead-deposit interaction, and late-cancellation revenue risk views
         (v_cancel_timing, v_lead_deposit_matrix, v_late_cancel_revenue_at_risk) per D11 and K5.
Inputs:  hotel.bookings
Outputs: Views:
  - hotel.v_cancel_timing
  - hotel.v_lead_deposit_matrix
  - hotel.v_late_cancel_revenue_at_risk
Grain:   
  - hotel.v_cancel_timing: One row per hotel ('All', 'City Hotel', 'Resort Hotel') per timing bucket of days_cancelled_before_arrival
  - hotel.v_lead_deposit_matrix: One row per hotel per lead_bucket per deposit_type
  - hotel.v_late_cancel_revenue_at_risk: One row per hotel per arrival_month_start
*/

-- 1. View: hotel.v_cancel_timing
CREATE OR REPLACE VIEW hotel.v_cancel_timing AS
WITH timed AS (
    SELECT
        hotel,
        CASE 
            WHEN days_cancelled_before_arrival <= 1 THEN '0-1 days'
            WHEN days_cancelled_before_arrival <= 7 THEN '2-7 days'
            WHEN days_cancelled_before_arrival <= 14 THEN '8-14 days'
            WHEN days_cancelled_before_arrival <= 30 THEN '15-30 days'
            WHEN days_cancelled_before_arrival <= 60 THEN '31-60 days'
            WHEN days_cancelled_before_arrival <= 90 THEN '61-90 days'
            ELSE '91+ days'
        END AS timing_bucket,
        CASE 
            WHEN days_cancelled_before_arrival <= 1 THEN 1
            WHEN days_cancelled_before_arrival <= 7 THEN 2
            WHEN days_cancelled_before_arrival <= 14 THEN 3
            WHEN days_cancelled_before_arrival <= 30 THEN 4
            WHEN days_cancelled_before_arrival <= 60 THEN 5
            WHEN days_cancelled_before_arrival <= 90 THEN 6
            ELSE 7
        END AS sort_order,
        days_cancelled_before_arrival,
        lead_time,
        room_revenue
    FROM hotel.bookings
    WHERE reservation_status = 'Canceled'
),
agg AS (
    SELECT
        COALESCE(hotel, 'All') AS hotel,
        timing_bucket,
        sort_order,
        COUNT(*)::bigint AS cancellations,
        ROUND(AVG(lead_time)::numeric, 1) AS avg_lead_time,
        ROUND(AVG(days_cancelled_before_arrival)::numeric, 1) AS avg_days_cancelled_before_arrival,
        ROUND(SUM(room_revenue)::numeric, 2) AS room_revenue_at_risk
    FROM timed
    GROUP BY GROUPING SETS ((hotel, timing_bucket, sort_order), (timing_bucket, sort_order))
)
SELECT
    hotel,
    timing_bucket,
    sort_order,
    cancellations,
    ROUND(100.0 * cancellations::numeric / SUM(cancellations) OVER (PARTITION BY hotel), 1) AS share_of_cancellations_pct,
    avg_lead_time,
    avg_days_cancelled_before_arrival,
    room_revenue_at_risk
FROM agg
ORDER BY (hotel = 'All') DESC, hotel, sort_order;

-- 2. View: hotel.v_lead_deposit_matrix
CREATE OR REPLACE VIEW hotel.v_lead_deposit_matrix AS
SELECT
    COALESCE(hotel, 'All') AS hotel,
    lead_bucket,
    lead_bucket_order,
    deposit_type,
    COUNT(*)::bigint AS bookings,
    SUM(is_canceled)::bigint AS cancellations,
    ROUND(100.0 * SUM(is_canceled)::numeric / NULLIF(COUNT(*), 0), 1) AS cancel_rate_pct,
    ROUND(100.0 * COUNT(*)::numeric / SUM(COUNT(*)) OVER (PARTITION BY COALESCE(hotel, 'All')), 1) AS share_of_hotel_bookings_pct
FROM hotel.bookings
GROUP BY GROUPING SETS ((hotel, lead_bucket, lead_bucket_order, deposit_type), (lead_bucket, lead_bucket_order, deposit_type))
ORDER BY (COALESCE(hotel, 'All') = 'All') DESC, hotel, lead_bucket_order, deposit_type;

-- 3. View: hotel.v_late_cancel_revenue_at_risk
CREATE OR REPLACE VIEW hotel.v_late_cancel_revenue_at_risk AS
SELECT
    COALESCE(hotel, 'All') AS hotel,
    arrival_month_start,
    COUNT(*)::bigint AS total_bookings,
    SUM(is_canceled)::bigint AS cancellations,
    COUNT(*) FILTER (WHERE is_canceled = 1 AND days_cancelled_before_arrival <= 7)::bigint AS late_cancellations_7d,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1 AND days_cancelled_before_arrival <= 7)::numeric / NULLIF(COUNT(*), 0), 1) AS late_cancel_rate_pct,
    ROUND(SUM(CASE WHEN is_canceled = 1 AND days_cancelled_before_arrival <= 7 THEN room_revenue ELSE 0 END)::numeric, 2) AS late_cancel_revenue_at_risk,
    ROUND(SUM(room_revenue)::numeric, 2) AS total_potential_revenue,
    ROUND(100.0 * SUM(CASE WHEN is_canceled = 1 AND days_cancelled_before_arrival <= 7 THEN room_revenue ELSE 0 END)::numeric / NULLIF(SUM(room_revenue), 0), 1) AS pct_revenue_at_risk
FROM hotel.bookings
GROUP BY GROUPING SETS ((hotel, arrival_month_start), (arrival_month_start))
ORDER BY (COALESCE(hotel, 'All') = 'All') DESC, hotel, arrival_month_start;
