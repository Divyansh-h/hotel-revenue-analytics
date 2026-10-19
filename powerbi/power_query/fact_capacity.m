let
    Source = Csv.Document(File.Contents(DataFolder & "fact_capacity.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"hotel_key", Int64.Type},
        {"date_key", type date},
        {"rooms_available", Int64.Type}
    }, "en-US")
in
    #"Changed Type"
