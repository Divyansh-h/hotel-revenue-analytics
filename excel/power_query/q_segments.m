let
    Source = Csv.Document(File.Contents(DataFolder & "v_segment_performance.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"hotel", type text},
        {"market_segment", type text},
        {"bookings", Int64.Type},
        {"cancellations", Int64.Type},
        {"cancel_rate_pct", type number},
        {"room_nights_sold", Int64.Type},
        {"room_revenue", type number},
        {"adr", type number},
        {"room_night_share_pct", type number},
        {"revenue_share_pct", type number},
        {"revenue_rank", Int64.Type},
        {"is_zero_revenue_segment", Int64.Type},
        {"is_underperformer", Int64.Type}
    }, "en-US"),
    #"Filtered Zero Revenue" = Table.SelectRows(#"Changed Type", each ([is_zero_revenue_segment] <> 1)),
    #"Added Performance Label" = Table.AddColumn(#"Filtered Zero Revenue", "Performance_Label", each if [is_underperformer] = 1 then "Underperformer" else "OK", type text),
    #"Removed Other Columns" = Table.SelectColumns(#"Added Performance Label", {"hotel", "market_segment", "bookings", "cancel_rate_pct", "adr", "revenue_share_pct", "revenue_rank", "Performance_Label"}),
    #"Sorted Rows" = Table.Sort(#"Removed Other Columns", {{"hotel", Order.Ascending}, {"revenue_rank", Order.Ascending}})
in
    #"Sorted Rows"
