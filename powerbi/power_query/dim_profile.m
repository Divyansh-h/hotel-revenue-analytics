let
    Source = Csv.Document(File.Contents(DataFolder & "dim_profile.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"profile_key", Int64.Type},
        {"market_segment", type text},
        {"distribution_channel", type text},
        {"customer_type", type text},
        {"deposit_type", type text}
    }, "en-US")
in
    #"Changed Type"
