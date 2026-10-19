let
    Source = Csv.Document(File.Contents(DataFolder & "fact_bookings.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"booking_id", Int64.Type},
        {"hotel_key", Int64.Type},
        {"profile_key", Int64.Type},
        {"arrival_date", type date},
        {"is_canceled", Int64.Type},
        {"is_no_show", Int64.Type},
        {"reservation_status", type text},
        {"lead_time", Int64.Type},
        {"lead_bucket", type text},
        {"lead_bucket_order", Int64.Type},
        {"total_nights", Int64.Type},
        {"total_guests", Int64.Type},
        {"country", type text},
        {"adr", type number},
        {"room_revenue", type number},
        {"is_repeated_guest", Int64.Type},
        {"previous_cancellations", Int64.Type},
        {"booking_changes", Int64.Type},
        {"special_requests", Int64.Type},
        {"room_type_mismatch", Int64.Type},
        {"days_cancelled_before_arrival", Int64.Type},
        {"cancel_timing_bucket", type text},
        {"cancel_timing_order", Int64.Type},
        {"is_duplicate_row", Int64.Type}
    }, "en-US")
in
    #"Changed Type"
