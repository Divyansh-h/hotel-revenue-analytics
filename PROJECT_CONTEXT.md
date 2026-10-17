# PROJECT_CONTEXT: Hotel Booking Revenue & Occupancy Analytics

## Goal
Act as the analyst for a hotel group's revenue team. Pipeline: clean (Python) -> analyse (PostgreSQL) -> summarise (Excel) -> visualise (Power BI) -> recommend (written insights).

## Dataset
Hotel Booking Demand: 119,390 rows, 32 columns. City Hotel (Lisbon) and Resort Hotel (Algarve). Arrival dates 2015-07-01 to 2017-08-31. Raw file data/raw/hotel_bookings.csv is read-only: never edit or overwrite it. There is no booking id and no room inventory.

## GLOBAL RULES (apply to every task)
R1. Never invent, estimate or hardcode a result. Every number in any report must come from a script or query output saved on disk.
R2. Never delete rows silently. Removed rows go to data/processed/excluded_rows.csv with a reason column.
R3. Every script is re-runnable (idempotent) and runs from the repo root.
R4. After writing a script or SQL file, RUN it and show me the real output. Never say done without running it.
R5. If a check fails or a number differs from what I expect, STOP and report. Never loosen or edit a check just to make it pass.
R6. Log every analytical decision in docs/decision_log.md.
R7. Use snake_case. Database: PostgreSQL, database hotel_analytics, schema hotel. Credentials only through .env, never in code.
R8. Ask before installing anything not in requirements.txt and before editing this file.
R9. Do not drop or truncate database objects without telling me, except objects created by the current task.
R10. SQL files live in sql/ and are run with src/run_sql.py. Python scripts live in src/ and run from the repo root.

## Cleaning decisions (authoritative)
D1. booking_id = 1-based row number in the raw file (primary key).
D2. arrival_date is built from arrival_date_year, arrival_date_month (month name) and arrival_date_day_of_month.
D3. children NaN -> 0. country NaN -> 'Unknown'. agent kept as a nullable integer. The company column is dropped (about 94 percent missing) and logged.
D4. total_nights = stays_in_weekend_nights + stays_in_week_nights. total_guests = adults + children + babies. checkout_date = arrival_date + total_nights days. booking_date = arrival_date - lead_time days. room_revenue = adr * total_nights.
D5. Rows with adr < 0 or adr > 1000 are EXCLUDED from the analytical table (expected: exactly 2 rows, one negative and one around 5400) and written to excluded_rows.csv. If the count is not 2, STOP.
D6. Rows with total_nights = 0 or total_guests = 0 are KEPT and flagged (flag_zero_nights, flag_zero_guests). They count as bookings but add no room-nights.
D7. Duplicate rows (identical on all 32 raw columns; later copies flagged, first copy not) are KEPT and flagged is_duplicate_row, because there is no booking id and they may be real separate bookings. A sensitivity analysis with and without duplicates is reported.
D8. reservation_status values: Check-Out, Canceled, No-Show. is_canceled = 1 covers both Canceled and No-Show. is_no_show = 1 only for No-Show.
D9. lead_bucket labels: '0-7', '8-30', '31-90', '91-180', '181+' with lead_bucket_order 1 to 5.
D10. room_type_mismatch = 1 when assigned_room_type <> reserved_room_type, else 0.
D11. days_cancelled_before_arrival = arrival_date - reservation_status_date, only when reservation_status = 'Canceled', otherwise NULL.
D12. All flag and boolean columns are stored as integers 0/1, never True/False.

## Final columns of hotel.bookings (exact names and order)
booking_id, hotel, is_canceled, is_no_show, reservation_status, reservation_status_date, lead_time, lead_bucket, lead_bucket_order, booking_date, arrival_date, arrival_year, arrival_month_num, arrival_month_start, checkout_date, stays_in_weekend_nights, stays_in_week_nights, total_nights, adults, children, babies, total_guests, meal, country, market_segment, distribution_channel, is_repeated_guest, previous_cancellations, previous_bookings_not_canceled, reserved_room_type, assigned_room_type, room_type_mismatch, booking_changes, deposit_type, agent, days_in_waiting_list, customer_type, adr, required_car_parking_spaces, total_of_special_requests, room_revenue, days_cancelled_before_arrival, flag_zero_nights, flag_zero_guests, is_duplicate_row
(arrival_date_week_number, arrival_date_year, arrival_date_month, arrival_date_day_of_month and company are intentionally not in the final table.)

## KPI definitions (authoritative)
K1. Room-night sold = one non-cancelled booking x one night stayed (from arrival_date through checkout_date minus 1 day). Bookings with total_nights = 0 give none.
K2. Room revenue = sum of adr over room-nights sold. Cancelled bookings earn no revenue (no deposit data exists).
K3. ADR = room revenue / room-nights sold. Never use AVG(adr).
K4. Occupancy % = room-nights sold / room-nights available. RevPAR = room revenue / room-nights available and must equal ADR x Occupancy (verify it).
K5. Cancellation rate = bookings with is_canceled = 1 / all bookings, attributed to the arrival month. No-show rate is reported separately.
K6. Stay conversion (proxy) = bookings with reservation_status 'Check-Out' / all bookings. This is exactly 1 minus the cancellation rate. The dataset has no website or enquiry funnel, and every report must say so.
K7. Occupancy and RevPAR exist only at hotel level. By segment or channel use room-night share, revenue share and ADR. If a visual shows them sliced by segment, label them as contribution to the hotel total.

## Reliable window and capacity
W1. Stay-night KPIs (occupancy, ADR, RevPAR) are reported only for stay dates 2015-08-01 to 2017-08-31, because stays that began before 2015-07-01 and arrivals after 2017-08-31 are missing from the data. Booking KPIs use all arrival dates.
W2. Capacity is not in the data. For each hotel: peak = maximum rooms sold on any night in the window; capacity = CEIL(peak * 1.10 / 10) * 10 (rounded up to the next ten, with a 10 percent buffer). It is stored in hotel.capacity and config/assumptions.yml. It is an assumption and must be stated in every deliverable.
