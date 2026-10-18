let
    Source = Csv.Document(File.Contents(DataFolder & "v_cancellation_drivers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"hotel", type text},
        {"dimension", type text},
        {"category", type text},
        {"sort_order", Int64.Type},
        {"bookings", Int64.Type},
        {"cancellations", Int64.Type},
        {"no_shows", Int64.Type},
        {"cancel_rate_pct", type number},
        {"share_of_bookings_pct", type number},
        {"cancel_rate_vs_hotel_avg_pp", type number}
    }, "en-US"),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([hotel] = "All") and List.Contains({"lead_bucket", "deposit_type", "customer_type", "market_segment"}, [dimension])),
    #"Added Risk Level" = Table.AddColumn(#"Filtered Rows", "Risk_Level", each if [cancel_rate_vs_hotel_avg_pp] > 10 then "High" else if [cancel_rate_vs_hotel_avg_pp] > 0 then "Medium" else "Low", type text),
    #"Sorted Rows" = Table.Sort(#"Added Risk Level", {{"dimension", Order.Ascending}, {"sort_order", Order.Ascending}, {"cancel_rate_pct", Order.Descending}})
in
    #"Sorted Rows"
