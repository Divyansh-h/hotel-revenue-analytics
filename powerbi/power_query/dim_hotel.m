let
    Source = Csv.Document(File.Contents(DataFolder & "dim_hotel.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"hotel_key", Int64.Type},
        {"hotel", type text},
        {"rooms_capacity", Int64.Type}
    }, "en-US")
in
    #"Changed Type"
