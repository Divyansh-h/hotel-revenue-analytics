# Data Dictionary: Hotel Booking Demand (Raw Dataset)

**Source File**: `data/raw/hotel_bookings.csv`  
**Observations**: 119,390 rows  
**Attributes**: 32 columns  
**Reference Codebook**: Antonio, N., de Almeida, A., & Nunes, L. (2019). *Hotel booking demand datasets*. Data in Brief, 22, 41–49.

| Column Name | Pandas Dtype | Example Value | Distinct Values | % Missing | Plain-English Meaning |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `hotel` | `object` (`str`) | `Resort Hotel` | 2 | 0.00% | Type of property: `City Hotel` (Lisbon) or `Resort Hotel` (Algarve). |
| `is_canceled` | `int64` | `0` | 2 | 0.00% | Binary flag indicating if the booking was canceled (`1`) or not (`0`). Covers both cancellations and no-shows. |
| `lead_time` | `int64` | `342` | 479 | 0.00% | Number of days elapsed between booking entry into PMS and customer arrival date. |
| `arrival_date_year` | `int64` | `2015` | 3 | 0.00% | Calendar year of customer arrival (2015, 2016, or 2017). |
| `arrival_date_month` | `object` (`str`) | `July` | 12 | 0.00% | Calendar month name of customer arrival date. |
| `arrival_date_week_number` | `int64` | `27` | 53 | 0.00% | Calendar week number of arrival date (ISO-8601 week 1 to 53). |
| `arrival_date_day_of_month` | `int64` | `1` | 31 | 0.00% | Day of the month of customer arrival date (1 to 31). |
| `stays_in_weekend_nights` | `int64` | `0` | 17 | 0.00% | Number of weekend nights (Saturday or Sunday) booked or stayed. |
| `stays_in_week_nights` | `int64` | `0` | 35 | 0.00% | Number of weekday nights (Monday through Friday) booked or stayed. |
| `adults` | `int64` | `2` | 14 | 0.00% | Number of adult occupants registered on the booking. |
| `children` | `float64` | `0.0` | 6 | 0.00% (4 rows) | Number of children registered on the booking (0.0 if none). |
| `babies` | `int64` | `0` | 5 | 0.00% | Number of infant babies registered on the booking. |
| `meal` | `object` (`str`) | `BB` | 5 | 0.00% | Type of booked meal plan: `BB` (Bed & Breakfast), `HB` (Half Board), `FB` (Full Board), `SC`/`Undefined` (Self Catering / No meal). |
| `country` | `object` (`str`) | `PRT` | 178 | 0.41% (488 rows) | Country of origin of guest in ISO 3166-1 alpha-3 format. |
| `market_segment` | `object` (`str`) | `Direct` | 8 | 0.00% | Market segment designation (e.g., `Direct`, `Corporate`, `Online TA`, `Offline TA/TO`, `Groups`, `Complementary`, `Aviation`). |
| `distribution_channel` | `object` (`str`) | `Direct` | 5 | 0.00% | Booking distribution channel through which reservation was made (`Direct`, `Corporate`, `TA/TO`, `GDS`, `Undefined`). |
| `is_repeated_guest` | `int64` | `0` | 2 | 0.00% | Binary flag indicating if booking is from a returning customer (`1`) or first-time guest (`0`). |
| `previous_cancellations` | `int64` | `0` | 15 | 0.00% | Number of prior bookings canceled by the customer prior to this booking. |
| `previous_bookings_not_canceled` | `int64` | `0` | 73 | 0.00% | Number of prior reservations completed without cancellation prior to this booking. |
| `reserved_room_type` | `object` (`str`) | `C` | 10 | 0.00% | Anonymized code identifier for the room category initially booked by customer. |
| `assigned_room_type` | `object` (`str`) | `C` | 12 | 0.00% | Anonymized code identifier for the room category assigned at check-in (may differ from reserved room). |
| `booking_changes` | `int64` | `3` | 21 | 0.00% | Number of modifications made to reservation from booking creation until check-in or cancellation. |
| `deposit_type` | `object` (`str`) | `No Deposit` | 3 | 0.00% | Deposit requirement policy: `No Deposit`, `Non Refund`, or `Refundable`. |
| `agent` | `float64` | `304.0` | 334 | 13.69% (16,340 rows) | Anonymized ID of the travel agency that made the booking. |
| `company` | `float64` | `110.0` | 353 | 94.31% (112,593 rows) | Anonymized ID of corporate entity responsible for booking or payment. |
| `days_in_waiting_list` | `int64` | `0` | 128 | 0.00% | Number of days reservation remained in waitlist before confirmation. |
| `customer_type` | `object` (`str`) | `Transient` | 4 | 0.00% | Customer categorization: `Transient`, `Transient-party`, `Contract`, `Group`. |
| `adr` | `float64` | `0.0` | 8,879 | 0.00% | Average Daily Rate (total lodging revenue divided by staying room-nights). |
| `required_car_parking_spaces` | `int64` | `0` | 5 | 0.00% | Number of vehicle parking spaces requested by customer. |
| `total_of_special_requests` | `int64` | `0` | 6 | 0.00% | Count of guest special accommodations requested (e.g., high floor, twin beds, quiet room). |
| `reservation_status` | `object` (`str`) | `Check-Out` | 3 | 0.00% | Final booking lifecycle status: `Check-Out`, `Canceled`, or `No-Show`. |
| `reservation_status_date` | `object` (`str`) | `2015-07-01` | 926 | 0.00% | Date on which reservation last achieved its current status (cancellation date or checkout date). |
