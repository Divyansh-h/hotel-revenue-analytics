let
    Source = Csv.Document(File.Contents(DataFolder & "fact_stay_nights.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"booking_id", Int64.Type},
        {"hotel_key", Int64.Type},
        {"profile_key", Int64.Type},
        {"stay_date", type date},
        {"adr", type number}
    }, "en-US")
in
    #"Changed Type"
