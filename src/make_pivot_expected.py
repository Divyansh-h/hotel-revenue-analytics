"""
Compute Expected PivotTable Verification Benchmarks from PostgreSQL
Generates excel/inputs/pivot_expected_values.csv containing authoritative
database benchmarks for the 4 manual PivotTables:
1. Overall Property Totals (Bookings, Cancel Rate, Realised Revenue)
2. PT_Monthly: First 3 arrival months (2015-07, 2015-08, 2015-09)
3. PT_Segment: Top 3 market segments (Online TA, Offline TA/TO, Groups)
4. PT_LeadTime: First 3 lead time buckets (0-7, 8-30, 31-90)
5. PT_Channel: Top 3 distribution channels (TA/TO, Direct, Corporate) by deposit type

Outputs:
- excel/inputs/pivot_expected_values.csv
"""

import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_engine

OUTPUT_CSV = REPO_ROOT / "excel" / "inputs" / "pivot_expected_values.csv"


def make_pivot_expected() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    records = []

    # 1. Overall Property Totals
    q_totals = """
    SELECT
        COALESCE(hotel, 'Total Portfolio') AS hotel,
        COUNT(*)::integer AS bookings,
        ROUND(AVG(is_canceled)::numeric, 4) AS cancel_rate,
        ROUND(SUM(room_revenue) FILTER (WHERE is_canceled = 0)::numeric, 2) AS revenue_realised
    FROM hotel.bookings
    GROUP BY ROLLUP(hotel)
    ORDER BY CASE WHEN hotel = 'City Hotel' THEN 1 WHEN hotel = 'Resort Hotel' THEN 2 ELSE 3 END;
    """
    df_totals = pd.read_sql_query(q_totals, engine)
    for _, row in df_totals.iterrows():
        records.append({
            "pivot_table": "Overall_Totals",
            "row_label": row["hotel"],
            "col_label": "All",
            "metric": "Bookings",
            "expected_value": f"{row['bookings']:,}"
        })
        records.append({
            "pivot_table": "Overall_Totals",
            "row_label": row["hotel"],
            "col_label": "All",
            "metric": "Cancel_Rate",
            "expected_value": f"{row['cancel_rate'] * 100:.2f}%"
        })
        records.append({
            "pivot_table": "Overall_Totals",
            "row_label": row["hotel"],
            "col_label": "All",
            "metric": "Revenue_Realised",
            "expected_value": f"${row['revenue_realised']:,.2f}"
        })

    # 2. PT_Monthly: First 3 Arrival Months
    q_monthly = """
    SELECT
        arrival_month_start,
        COALESCE(hotel, 'Total') AS hotel,
        COUNT(*)::integer AS bookings,
        ROUND(AVG(is_canceled)::numeric, 4) AS cancel_rate,
        ROUND(SUM(room_revenue) FILTER (WHERE is_canceled = 0)::numeric, 2) AS revenue_realised
    FROM hotel.bookings
    WHERE arrival_month_start IN ('2015-07-01', '2015-08-01', '2015-09-01')
    GROUP BY arrival_month_start, ROLLUP(hotel)
    ORDER BY arrival_month_start, CASE WHEN hotel = 'City Hotel' THEN 1 WHEN hotel = 'Resort Hotel' THEN 2 ELSE 3 END;
    """
    df_m = pd.read_sql_query(q_monthly, engine)
    for _, row in df_m.iterrows():
        month_label = row["arrival_month_start"].strftime("%Y-%m") if hasattr(row["arrival_month_start"], "strftime") else str(row["arrival_month_start"])[:7]
        records.append({
            "pivot_table": "PT_Monthly",
            "row_label": month_label,
            "col_label": row["hotel"],
            "metric": "Bookings",
            "expected_value": f"{row['bookings']:,}"
        })
        records.append({
            "pivot_table": "PT_Monthly",
            "row_label": month_label,
            "col_label": row["hotel"],
            "metric": "Cancel_Rate",
            "expected_value": f"{row['cancel_rate'] * 100:.2f}%"
        })
        records.append({
            "pivot_table": "PT_Monthly",
            "row_label": month_label,
            "col_label": row["hotel"],
            "metric": "Revenue_Realised",
            "expected_value": f"${row['revenue_realised']:,.2f}"
        })

    # 3. PT_Segment: Top 3 Segments
    q_segment = """
    WITH hotel_totals AS (
        SELECT COALESCE(hotel, 'Total') AS hotel, SUM(room_revenue) FILTER (WHERE is_canceled = 0) AS total_rev
        FROM hotel.bookings
        GROUP BY ROLLUP(hotel)
    ),
    seg_stats AS (
        SELECT
            market_segment,
            COALESCE(hotel, 'Total') AS hotel,
            COUNT(*)::integer AS bookings,
            ROUND(AVG(is_canceled)::numeric, 4) AS cancel_rate,
            ROUND(SUM(room_revenue) FILTER (WHERE is_canceled = 0)::numeric, 2) AS revenue_realised
        FROM hotel.bookings
        WHERE market_segment IN ('Online TA', 'Offline TA/TO', 'Groups')
        GROUP BY market_segment, ROLLUP(hotel)
    )
    SELECT
        s.market_segment,
        s.hotel,
        s.bookings,
        s.cancel_rate,
        s.revenue_realised,
        ROUND((s.revenue_realised / h.total_rev * 100)::numeric, 2) AS revenue_share_pct
    FROM seg_stats s
    JOIN hotel_totals h ON s.hotel = h.hotel
    ORDER BY CASE s.market_segment WHEN 'Online TA' THEN 1 WHEN 'Offline TA/TO' THEN 2 ELSE 3 END,
             CASE s.hotel WHEN 'City Hotel' THEN 1 WHEN 'Resort Hotel' THEN 2 ELSE 3 END;
    """
    df_s = pd.read_sql_query(q_segment, engine)
    for _, row in df_s.iterrows():
        records.append({
            "pivot_table": "PT_Segment",
            "row_label": row["market_segment"],
            "col_label": row["hotel"],
            "metric": "Bookings",
            "expected_value": f"{row['bookings']:,}"
        })
        records.append({
            "pivot_table": "PT_Segment",
            "row_label": row["market_segment"],
            "col_label": row["hotel"],
            "metric": "Cancel_Rate",
            "expected_value": f"{row['cancel_rate'] * 100:.2f}%"
        })
        records.append({
            "pivot_table": "PT_Segment",
            "row_label": row["market_segment"],
            "col_label": row["hotel"],
            "metric": "Revenue_Realised",
            "expected_value": f"${row['revenue_realised']:,.2f}"
        })
        records.append({
            "pivot_table": "PT_Segment",
            "row_label": row["market_segment"],
            "col_label": row["hotel"],
            "metric": "Revenue_Share_Pct",
            "expected_value": f"{row['revenue_share_pct']:.2f}%"
        })

    # 4. PT_LeadTime: First 3 Buckets
    q_lead = """
    SELECT
        lead_bucket,
        lead_bucket_order,
        COALESCE(hotel, 'Total') AS hotel,
        COUNT(*)::integer AS bookings,
        ROUND(AVG(is_canceled)::numeric, 4) AS cancel_rate
    FROM hotel.bookings
    WHERE lead_bucket IN ('0-7', '8-30', '31-90')
    GROUP BY lead_bucket, lead_bucket_order, ROLLUP(hotel)
    ORDER BY lead_bucket_order, CASE hotel WHEN 'City Hotel' THEN 1 WHEN 'Resort Hotel' THEN 2 ELSE 3 END;
    """
    df_l = pd.read_sql_query(q_lead, engine)
    for _, row in df_l.iterrows():
        records.append({
            "pivot_table": "PT_LeadTime",
            "row_label": row["lead_bucket"],
            "col_label": row["hotel"],
            "metric": "Bookings",
            "expected_value": f"{row['bookings']:,}"
        })
        records.append({
            "pivot_table": "PT_LeadTime",
            "row_label": row["lead_bucket"],
            "col_label": row["hotel"],
            "metric": "Cancel_Rate",
            "expected_value": f"{row['cancel_rate'] * 100:.2f}%"
        })

    # 5. PT_Channel: Top 3 Channels x Deposit Types
    q_chan = """
    SELECT
        distribution_channel,
        COALESCE(deposit_type, 'Total') AS deposit_type,
        COUNT(*)::integer AS bookings,
        ROUND(AVG(is_canceled)::numeric, 4) AS cancel_rate
    FROM hotel.bookings
    WHERE distribution_channel IN ('TA/TO', 'Direct', 'Corporate')
    GROUP BY distribution_channel, ROLLUP(deposit_type)
    ORDER BY CASE distribution_channel WHEN 'TA/TO' THEN 1 WHEN 'Direct' THEN 2 ELSE 3 END,
             CASE deposit_type WHEN 'No Deposit' THEN 1 WHEN 'Non Refund' THEN 2 WHEN 'Refundable' THEN 3 ELSE 4 END;
    """
    df_c = pd.read_sql_query(q_chan, engine)
    for _, row in df_c.iterrows():
        records.append({
            "pivot_table": "PT_Channel",
            "row_label": row["distribution_channel"],
            "col_label": row["deposit_type"],
            "metric": "Bookings",
            "expected_value": f"{row['bookings']:,}"
        })
        records.append({
            "pivot_table": "PT_Channel",
            "row_label": row["distribution_channel"],
            "col_label": row["deposit_type"],
            "metric": "Cancel_Rate",
            "expected_value": f"{row['cancel_rate'] * 100:.2f}%"
        })

    out_df = pd.DataFrame(records)
    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print("=" * 80)
    print("PIVOT TABLE EXPECTED VALUES EXPORT REPORT")
    print("=" * 80)
    print(f"Total benchmark records generated: {len(out_df)}")
    print(f"File saved to: {OUTPUT_CSV}")
    print("-" * 80)
    print(out_df.head(15).to_string(index=False))
    print("-" * 80)
    print(f"[SUCCESS] All PivotTable expected benchmarks exported successfully.")
    print("=" * 80)


def main():
    make_pivot_expected()


if __name__ == "__main__":
    main()
