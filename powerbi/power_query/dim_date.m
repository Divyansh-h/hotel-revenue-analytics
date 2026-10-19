let
    Source = Csv.Document(File.Contents(DataFolder & "dim_date.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"date_key", type date},
        {"year", Int64.Type},
        {"quarter", Int64.Type},
        {"month_num", Int64.Type},
        {"month_short", type text},
        {"month_name", type text},
        {"month_start", type date},
        {"year_month", type text}
    }, "en-US")
in
    #"Changed Type"
