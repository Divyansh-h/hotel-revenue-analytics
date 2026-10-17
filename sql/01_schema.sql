-- Schema & Table Definition for Hotel Booking Analytics
-- Database: hotel_analytics, Schema: hotel, Table: bookings

CREATE SCHEMA IF NOT EXISTS hotel;

CREATE TABLE IF NOT EXISTS hotel.bookings (
    booking_id                      integer PRIMARY KEY,
    hotel                           text NOT NULL,
    is_canceled                     smallint NOT NULL,
    is_no_show                      smallint NOT NULL,
    reservation_status              text NOT NULL,
    reservation_status_date         date NOT NULL,
    lead_time                       integer NOT NULL,
    lead_bucket                     text NOT NULL,
    lead_bucket_order               smallint NOT NULL,
    booking_date                    date NOT NULL,
    arrival_date                    date NOT NULL,
    arrival_year                    integer NOT NULL,
    arrival_month_num               smallint NOT NULL,
    arrival_month_start             date NOT NULL,
    checkout_date                   date NOT NULL,
    stays_in_weekend_nights         integer NOT NULL,
    stays_in_week_nights            integer NOT NULL,
    total_nights                    integer NOT NULL,
    adults                          integer NOT NULL,
    children                        integer NOT NULL,
    babies                          integer NOT NULL,
    total_guests                    integer NOT NULL,
    meal                            text NOT NULL,
    country                         text NOT NULL,
    market_segment                  text NOT NULL,
    distribution_channel            text NOT NULL,
    is_repeated_guest               smallint NOT NULL,
    previous_cancellations          integer NOT NULL,
    previous_bookings_not_canceled  integer NOT NULL,
    reserved_room_type              text NOT NULL,
    assigned_room_type              text NOT NULL,
    room_type_mismatch              smallint NOT NULL,
    booking_changes                 integer NOT NULL,
    deposit_type                    text NOT NULL,
    agent                           integer NULL,
    days_in_waiting_list            integer NOT NULL,
    customer_type                   text NOT NULL,
    adr                             numeric(10, 2) NOT NULL,
    required_car_parking_spaces     integer NOT NULL,
    total_of_special_requests       integer NOT NULL,
    room_revenue                    numeric(12, 2) NOT NULL,
    days_cancelled_before_arrival   integer NULL,
    flag_zero_nights                smallint NOT NULL,
    flag_zero_guests                smallint NOT NULL,
    is_duplicate_row                smallint NOT NULL,

    -- Constraints
    CONSTRAINT chk_hotel CHECK (hotel IN ('City Hotel', 'Resort Hotel')),
    CONSTRAINT chk_is_canceled CHECK (is_canceled IN (0, 1)),
    CONSTRAINT chk_is_no_show CHECK (is_no_show IN (0, 1)),
    CONSTRAINT chk_reservation_status CHECK (reservation_status IN ('Check-Out', 'Canceled', 'No-Show')),
    CONSTRAINT chk_lead_bucket CHECK (lead_bucket IN ('0-7', '8-30', '31-90', '91-180', '181+')),
    CONSTRAINT chk_adr CHECK (adr BETWEEN 0 AND 1000),
    CONSTRAINT chk_total_nights CHECK (total_nights = stays_in_weekend_nights + stays_in_week_nights),
    CONSTRAINT chk_flag_zero_nights CHECK (flag_zero_nights IN (0, 1)),
    CONSTRAINT chk_flag_zero_guests CHECK (flag_zero_guests IN (0, 1)),
    CONSTRAINT chk_is_duplicate_row CHECK (is_duplicate_row IN (0, 1)),
    CONSTRAINT chk_room_type_mismatch CHECK (room_type_mismatch IN (0, 1)),
    CONSTRAINT chk_is_repeated_guest CHECK (is_repeated_guest IN (0, 1))
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_bookings_hotel_arrival ON hotel.bookings (hotel, arrival_date);
CREATE INDEX IF NOT EXISTS idx_bookings_arrival_month_start ON hotel.bookings (arrival_month_start);
CREATE INDEX IF NOT EXISTS idx_bookings_market_segment ON hotel.bookings (market_segment);
CREATE INDEX IF NOT EXISTS idx_bookings_is_canceled ON hotel.bookings (is_canceled);
