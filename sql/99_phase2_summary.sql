/*
Purpose: Return a unified one-page Phase 2 analytical executive summary:
         capacity per hotel, window dates, total room-nights, total room revenue,
         ADR, occupancy %, RevPAR, and overall cancellation rate.
Inputs:  hotel.v_hotel_totals, hotel.bookings, hotel.capacity, hotel.window_params
Outputs: Executive summary result set (3 rows: City Hotel, Resort Hotel, All hotels)
Grain:   One row per hotel plus portfolio total ('All hotels').
*/

WITH hotel_totals AS (
    SELECT 
        hotel,
        room_nights_sold,
        room_revenue,
        occupancy_pct,
        adr,
        revpar
    FROM hotel.v_hotel_totals
),
cancel_rates AS (
    SELECT
        COALESCE(hotel, 'All hotels') AS hotel,
        ROUND(100.0 * SUM(is_canceled)::numeric / COUNT(*), 1) AS overall_cancel_rate_pct
    FROM hotel.bookings
    GROUP BY GROUPING SETS ((hotel), ())
),
capacities AS (
    SELECT 
        COALESCE(hotel, 'All hotels') AS hotel,
        SUM(rooms)::integer AS capacity_rooms
    FROM hotel.capacity
    GROUP BY GROUPING SETS ((hotel), ())
),
wp AS (
    SELECT window_start, window_end FROM hotel.window_params
)
SELECT 
    t.hotel,
    c.capacity_rooms,
    wp.window_start,
    wp.window_end,
    t.room_nights_sold,
    t.room_revenue,
    t.adr,
    t.occupancy_pct,
    t.revpar,
    cr.overall_cancel_rate_pct
FROM hotel_totals t
JOIN cancel_rates cr ON t.hotel = cr.hotel
JOIN capacities c ON t.hotel = c.hotel
CROSS JOIN wp
ORDER BY (t.hotel = 'All hotels'), t.hotel;
