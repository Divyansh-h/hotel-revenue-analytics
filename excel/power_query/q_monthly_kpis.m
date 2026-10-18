let
    Source = Csv.Document(File.Contents(DataFolder & "v_monthly_kpis.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"hotel", type text},
        {"month_start", type date},
        {"room_nights_sold", Int64.Type},
        {"room_nights_available", Int64.Type},
        {"room_revenue", type number},
        {"occupancy_pct", type number},
        {"adr", type number},
        {"revpar", type number}
    }, "en-US"),
    #"Inserted Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([month_start]), Int64.Type),
    #"Inserted Month Name" = Table.AddColumn(#"Inserted Year", "Month_Name", each Date.MonthName([month_start]), type text),
    #"Added High Occupancy" = Table.AddColumn(#"Inserted Month Name", "High_Occupancy_Flag", each if [occupancy_pct] >= 85 then "High" else "Normal", type text),
    #"Sorted Rows" = Table.Sort(#"Added High Occupancy", {{"hotel", Order.Ascending}, {"month_start", Order.Ascending}})
in
    #"Sorted Rows"
