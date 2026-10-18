/*
Purpose: Define market segment and distribution channel performance and cross-tabulation views
         (v_segment_performance, v_channel_performance, v_segment_channel_matrix) adhering to K7 and W1.
Inputs:  hotel.stay_nights, hotel.window_params, hotel.bookings
Outputs: Views:
  - hotel.v_segment_performance
  - hotel.v_channel_performance
  - hotel.v_segment_channel_matrix
Grain:   
  - hotel.v_segment_performance: One row per hotel ('All', 'City Hotel', 'Resort Hotel') per market_segment
  - hotel.v_channel_performance: One row per hotel per distribution_channel
  - hotel.v_segment_channel_matrix: One row per hotel per market_segment per distribution_channel
*/

-- 1. View: hotel.v_segment_performance
CREATE OR REPLACE VIEW hotel.v_segment_performance AS
WITH wp AS (
    SELECT window_start, window_end FROM hotel.window_params
),
stay_agg AS (
    SELECT
        sn.hotel,
        sn.market_segment,
        COUNT(*)::bigint AS room_nights_sold,
        ROUND(SUM(sn.adr)::numeric, 2) AS room_revenue
    FROM hotel.stay_nights sn
    CROSS JOIN wp
    WHERE sn.stay_date >= wp.window_start AND sn.stay_date <= wp.window_end
    GROUP BY sn.hotel, sn.market_segment
),
booking_agg AS (
    SELECT
        hotel,
        market_segment,
        COUNT(*)::bigint AS bookings,
        SUM(is_canceled)::bigint AS cancellations
    FROM hotel.bookings
    GROUP BY hotel, market_segment
),
combined AS (
    SELECT
        COALESCE(b.hotel, 'All') AS hotel,
        b.market_segment,
        SUM(b.bookings)::bigint AS bookings,
        SUM(b.cancellations)::bigint AS cancellations,
        COALESCE(SUM(s.room_nights_sold), 0)::bigint AS room_nights_sold,
        COALESCE(SUM(s.room_revenue), 0.00)::numeric(12, 2) AS room_revenue
    FROM booking_agg b
    LEFT JOIN stay_agg s ON b.hotel = s.hotel AND b.market_segment = s.market_segment
    GROUP BY GROUPING SETS ((b.hotel, b.market_segment), (b.market_segment))
),
base_metrics AS (
    SELECT
        hotel,
        market_segment,
        bookings,
        cancellations,
        ROUND(100.0 * cancellations::numeric / NULLIF(bookings, 0), 1) AS cancel_rate_pct,
        room_nights_sold,
        room_revenue,
        ROUND(room_revenue / NULLIF(room_nights_sold, 0), 2) AS adr,
        ROUND(100.0 * room_nights_sold::numeric / NULLIF(SUM(room_nights_sold) OVER (PARTITION BY hotel), 0), 1) AS room_night_share_pct,
        ROUND(100.0 * room_revenue / NULLIF(SUM(room_revenue) OVER (PARTITION BY hotel), 0), 1) AS revenue_share_pct,
        DENSE_RANK() OVER (PARTITION BY hotel ORDER BY room_revenue DESC)::integer AS revenue_rank,
        CASE WHEN COALESCE(room_revenue, 0) = 0 THEN 1 ELSE 0 END::smallint AS is_zero_revenue_segment
    FROM combined
),
hotel_benchmarks AS (
    SELECT
        hotel,
        ROUND(100.0 * SUM(cancellations)::numeric / NULLIF(SUM(bookings), 0), 1) AS hotel_cancel_rate_pct,
        ROUND(SUM(room_revenue) / NULLIF(SUM(room_nights_sold), 0), 2) AS hotel_adr
    FROM combined
    GROUP BY hotel
)
SELECT
    b.hotel,
    b.market_segment,
    b.bookings,
    b.cancellations,
    b.cancel_rate_pct,
    b.room_nights_sold,
    b.room_revenue,
    b.adr,
    b.room_night_share_pct,
    b.revenue_share_pct,
    b.revenue_rank,
    b.is_zero_revenue_segment,
    CASE
        WHEN b.cancel_rate_pct > h.hotel_cancel_rate_pct AND b.adr < h.hotel_adr THEN 1
        ELSE 0
    END::smallint AS is_underperformer
FROM base_metrics b
JOIN hotel_benchmarks h ON b.hotel = h.hotel
ORDER BY (b.hotel = 'All') DESC, b.hotel, b.revenue_rank;

-- 2. View: hotel.v_channel_performance
CREATE OR REPLACE VIEW hotel.v_channel_performance AS
WITH wp AS (
    SELECT window_start, window_end FROM hotel.window_params
),
stay_agg AS (
    SELECT
        sn.hotel,
        sn.distribution_channel,
        COUNT(*)::bigint AS room_nights_sold,
        ROUND(SUM(sn.adr)::numeric, 2) AS room_revenue
    FROM hotel.stay_nights sn
    CROSS JOIN wp
    WHERE sn.stay_date >= wp.window_start AND sn.stay_date <= wp.window_end
    GROUP BY sn.hotel, sn.distribution_channel
),
booking_agg AS (
    SELECT
        hotel,
        distribution_channel,
        COUNT(*)::bigint AS bookings,
        SUM(is_canceled)::bigint AS cancellations
    FROM hotel.bookings
    GROUP BY hotel, distribution_channel
),
combined AS (
    SELECT
        COALESCE(b.hotel, 'All') AS hotel,
        b.distribution_channel,
        SUM(b.bookings)::bigint AS bookings,
        SUM(b.cancellations)::bigint AS cancellations,
        COALESCE(SUM(s.room_nights_sold), 0)::bigint AS room_nights_sold,
        COALESCE(SUM(s.room_revenue), 0.00)::numeric(12, 2) AS room_revenue
    FROM booking_agg b
    LEFT JOIN stay_agg s ON b.hotel = s.hotel AND b.distribution_channel = s.distribution_channel
    GROUP BY GROUPING SETS ((b.hotel, b.distribution_channel), (b.distribution_channel))
)
SELECT
    hotel,
    distribution_channel,
    bookings,
    cancellations,
    ROUND(100.0 * cancellations::numeric / NULLIF(bookings, 0), 1) AS cancel_rate_pct,
    room_nights_sold,
    room_revenue,
    ROUND(room_revenue / NULLIF(room_nights_sold, 0), 2) AS adr,
    ROUND(100.0 * room_nights_sold::numeric / NULLIF(SUM(room_nights_sold) OVER (PARTITION BY hotel), 0), 1) AS room_night_share_pct,
    ROUND(100.0 * room_revenue / NULLIF(SUM(room_revenue) OVER (PARTITION BY hotel), 0), 1) AS revenue_share_pct
FROM combined
ORDER BY (hotel = 'All') DESC, hotel, room_revenue DESC;

-- 3. View: hotel.v_segment_channel_matrix
CREATE OR REPLACE VIEW hotel.v_segment_channel_matrix AS
SELECT
    COALESCE(hotel, 'All') AS hotel,
    market_segment,
    distribution_channel,
    COUNT(*)::bigint AS bookings,
    SUM(is_canceled)::bigint AS cancellations,
    ROUND(100.0 * SUM(is_canceled)::numeric / NULLIF(COUNT(*), 0), 1) AS cancel_rate_pct,
    SUM(CASE WHEN is_canceled = 0 THEN total_nights ELSE 0 END)::bigint AS room_nights,
    ROUND(SUM(CASE WHEN is_canceled = 0 THEN room_revenue ELSE 0 END)::numeric, 2) AS room_revenue,
    ROUND(SUM(CASE WHEN is_canceled = 0 THEN room_revenue ELSE 0 END)::numeric / NULLIF(SUM(CASE WHEN is_canceled = 0 THEN total_nights ELSE 0 END), 0), 2) AS adr
FROM hotel.bookings
GROUP BY GROUPING SETS ((hotel, market_segment, distribution_channel), (market_segment, distribution_channel))
ORDER BY (COALESCE(hotel, 'All') = 'All') DESC, hotel, market_segment, distribution_channel;
