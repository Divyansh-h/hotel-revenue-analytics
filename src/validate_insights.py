"""
Validation suite for reports/insights/*.md and reports/findings_data.json.
Validates structural compliance, section requirements, mathematical scenarios,
and source tagging per Global Rule R1.
"""

import json
import re
from pathlib import Path
import pandas as pd

def validate_01(findings, insight_text):
    print("\n--- VALIDATING 01_PRICING_SEASONALITY.MD ---")
    
    # 1. Structure check: Finding -> Evidence -> Recommended action -> Expected impact
    sections = [
        "Insight (a): Seasonality Patterns & Dynamic Rate Rules",
        "Insight (b): Price and Occupancy Gaps",
        "### 1. Finding",
        "### 2. Evidence",
        "### 3. Recommended action",
        "### 4. Expected impact (As a Scenario)"
    ]
    for sec in sections:
        assert sec.lower() in insight_text.lower(), f"Missing section in 01: {sec}"
        print(f"PASS: Found section header '{sec}'")
        
    # 2. Check caveat and scenario label
    assert "Scenario, not forecast" in insight_text, "Missing 'Scenario, not forecast' label"
    assert "higher prices would probably reduce occupancy" in insight_text.lower(), "Missing price elasticity occupancy reduction caveat"
    assert "cannot measure price elasticity" in insight_text.lower(), "Missing 'cannot measure price elasticity' caveat"
    print("PASS: Verified scenario label and price elasticity caveats.")
    
    # 3. Verify key empirical data points are present
    bench = findings["hotel_benchmarks"]
    assert str(bench["City Hotel"]["capacity"]) in insight_text
    assert str(bench["City Hotel"]["peak_rooms_sold"]) in insight_text
    assert str(bench["City Hotel"]["nights_ge_90pct"]) in insight_text
    assert "2.89%" in insight_text
    assert "$580,233.65" in insight_text
    assert "$117.03" in insight_text
    
    assert str(bench["Resort Hotel"]["capacity"]) in insight_text
    assert str(bench["Resort Hotel"]["peak_rooms_sold"]) in insight_text
    assert str(bench["Resort Hotel"]["nights_ge_90pct"]) in insight_text
    assert "0.00%" in insight_text
    
    # Seasonality check
    assert "April, May, June, July" in insight_text
    assert "June, July, August, September" in insight_text
    assert "86.06%" in insight_text
    assert "$93.97" in insight_text
    assert "$177.16" in insight_text
    
    # Price gaps check
    assert "$975,708.65" in insight_text
    assert "10,813" in insight_text
    assert "$90.23" in insight_text
    assert "$48,785.43" in insight_text
    assert "$54,662.12" in insight_text
    
    # Group 2 check
    assert "28,094" in insight_text
    assert "$2,386,239.37" in insight_text
    assert "29,524" in insight_text
    assert "$1,669,891.18" in insight_text
    assert "$4,056,130.55" in insight_text
    assert "$418,478.86" in insight_text
    
    # Source tag pattern check
    source_tags = re.findall(r"\[([^\]]+\.csv[^\]]*)\]", insight_text)
    assert len(source_tags) >= 20, f"Expected at least 20 source tags, found {len(source_tags)}"
    print(f"PASS: Verified {len(source_tags)} bracketed CSV source citations in 01.")

def validate_02(findings, insight_text):
    print("\n--- VALIDATING 02_CANCELLATIONS.MD ---")
    
    # 1. Structure check: Finding -> Evidence -> Recommended action -> Expected impact
    insights = [
        "Insight (a): Lead Time and Cancellation Dynamics",
        "Insight (b): Deposit Policy & The Non Refund Paradox",
        "Insight (c): Cancellation Timing & Late Revenue Risk"
    ]
    for ins in insights:
        assert ins.lower() in insight_text.lower(), f"Missing insight title: {ins}"
        print(f"PASS: Found insight header '{ins}'")
        
    for sub in ["### 1. Finding", "### 2. Evidence", "### 3. Recommended action", "### 4. Expected impact (As a Scenario)"]:
        assert insight_text.lower().count(sub.lower()) >= 3, f"Expected at least 3 occurrences of {sub}"
        print(f"PASS: Found 3+ occurrences of '{sub}'")
        
    # 2. Scenario label and caveat check
    assert "Scenario, not forecast" in insight_text, "Missing 'Scenario, not forecast' label in 02"
    assert "higher prices would probably reduce occupancy" in insight_text.lower(), "Missing price elasticity occupancy reduction caveat in 02"
    assert "cannot measure price elasticity" in insight_text.lower(), "Missing 'cannot measure price elasticity' caveat in 02"
    print("PASS: Verified scenario label and price elasticity caveats in 02.")
    
    # 3. Association language check (Rule: use association language only)
    causal_words = [" caused ", " causes ", " drove ", " drives the cancellation "]
    for word in causal_words:
        assert word not in insight_text.lower(), f"Found causal language: '{word}'"
    print("PASS: Verified strictly association language used.")
    
    # 4. Insight (a) checks: Lead time & cancellations
    c_lead = findings["cancellations"]["lead_time"]
    assert "9.63%" in insight_text or "9.6%" in insight_text # 0-7d
    assert "27.86%" in insight_text or "27.9%" in insight_text # 8-30d
    assert "37.70%" in insight_text or "37.7%" in insight_text # 31-90d
    assert "44.71%" in insight_text or "44.7%" in insight_text # 91-180d
    assert "57.01%" in insight_text or "57.0%" in insight_text # 181+d
    assert "0.3163" in insight_text # Cramer's V
    assert "113.0 days" in insight_text # Median canceled
    assert "45.0 days" in insight_text # Median non-canceled
    assert "+68.0 days" in insight_text # Median shift
    assert "0.3785" in insight_text # Rank-biserial r
    assert "$477,528.30" in insight_text # Scenario A1 preserved revenue
    assert "4,988.9" in insight_text # Scenario A1 room nights
    assert "1,407.7" in insight_text # Scenario A1 avoided cancellations
    print("PASS: Verified Insight (a) lead bucket rates, test statistics, and Scenario A1.")
    
    # 5. Insight (b) checks: Deposit type & Non Refund paradox
    c_dep = findings["cancellations"]["deposit_type"]
    assert "28.38%" in insight_text or "28.4%" in insight_text # No Deposit
    assert "22.22%" in insight_text or "22.2%" in insight_text # Refundable
    assert "99.36%" in insight_text or "99.4%" in insight_text # Non Refund
    assert "counter-intuitive" in insight_text.lower(), "Must state plainly that Non Refund cancel rate is counter-intuitive"
    assert "hypotheses" in insight_text.lower(), "Must present findings as hypotheses to investigate"
    assert "recording artefact" in insight_text.lower(), "Must include recording artefact hypothesis"
    assert "group" in insight_text.lower(), "Must include group block hypothesis"
    
    # Cross-tabulation figures
    assert "97.18%" in insight_text or "14,175" in insight_text # PRT share/count
    assert "93.58%" in insight_text or "13,650" in insight_text # TA/TO share/count
    assert "62.88%" in insight_text or "9,172" in insight_text # Groups share/count
    assert "34.31%" in insight_text or "5,005" in insight_text # Offline TA/TO share/count
    assert "88.21%" in insight_text or "12,867" in insight_text # City Hotel share/count
    assert "$359,893.70" in insight_text # Scenario B1 preserved revenue
    print("PASS: Verified Insight (b) deposit rates, cross-tabulations, hypotheses, and Scenario B1.")
    
    # 6. Insight (c) checks: Timing & Late cancellation revenue risk
    c_time = findings["cancellations"]["timing_and_late_cancellations"]
    assert "11.9%" in insight_text or "11.94%" in insight_text # Share within 7d
    assert "3.5%" in insight_text # 0-1d share
    assert "8.4%" in insight_text # 2-7d share
    assert "$1,533,486.66" in insight_text # Upper bound revenue at risk
    assert "5,135" in insight_text # Total late cancellations
    assert "14,841" in insight_text # Total late room nights
    assert "$153,348.67" in insight_text # Scenario C1 revenue covered
    assert "1,484.1" in insight_text # Scenario C1 room nights covered
    assert "513.5" in insight_text # Scenario C1 avoided cancellations
    assert "reconfirmation" in insight_text.lower()
    assert "cancellation window" in insight_text.lower()
    print("PASS: Verified Insight (c) timing distribution, revenue at risk, and Scenario C1.")
    
    # Source tag pattern check
    source_tags = re.findall(r"\[([^\]]+\.csv[^\]]*)\]", insight_text)
    assert len(source_tags) >= 20, f"Expected at least 20 source tags, found {len(source_tags)}"
    print(f"PASS: Verified {len(source_tags)} bracketed CSV source citations in 02.")

def validate_03(findings, insight_text):
    print("\n--- VALIDATING 03_OVERBOOKING_MIX.MD ---")
    
    # 1. Structure check: Finding -> Evidence -> Recommended action -> Expected impact
    insights = [
        "Insight (a): Overbooking Buffer & Capacity Protection",
        "Insight (b): Room-Type Mismatch as a Walk-Risk Signal",
        "Insight (c): Commercial Segment & Channel Mix Optimization"
    ]
    for ins in insights:
        assert ins.lower() in insight_text.lower(), f"Missing insight title: {ins}"
        print(f"PASS: Found insight header '{ins}'")
        
    for sub in ["### 1. Finding", "### 2. Evidence", "### 3. Recommended action", "### 4. Expected impact (As a Scenario)"]:
        assert insight_text.lower().count(sub.lower()) >= 3, f"Expected at least 3 occurrences of {sub}"
        print(f"PASS: Found 3+ occurrences of '{sub}'")
        
    # 2. Scenario label and caveat check
    assert "Scenario, not forecast" in insight_text, "Missing 'Scenario, not forecast' label in 03"
    assert "higher prices would probably reduce occupancy" in insight_text.lower(), "Missing price elasticity occupancy reduction caveat in 03"
    assert "cannot measure price elasticity" in insight_text.lower(), "Missing 'cannot measure price elasticity' caveat in 03"
    print("PASS: Verified scenario label and price elasticity caveats in 03.")
    
    # 3. Rule K7 check: No segment-level occupancy or RevPAR
    assert "rule k7" in insight_text.lower(), "Must reference Rule K7 governance"
    # Ensure no claims of segment-level occupancy or RevPAR
    forbidden_terms = [
        "segment occupancy", "segment revpar", "channel occupancy", "channel revpar",
        "market segment occupancy", "market segment revpar"
    ]
    for ft in forbidden_terms:
        # Check that it's only mentioned in the context of disclaiming / prohibiting it
        matches = [m.start() for m in re.finditer(re.escape(ft), insight_text.lower())]
        for m in matches:
            context = insight_text[max(0, m-80):min(len(insight_text), m+80)].lower()
            assert "do not exist" in context or "not reported" in context or "strictly at the property level" in context, \
                f"Rule K7 violation: found '{ft}' used outside of disclaimer context: {context}"
    print("PASS: Verified Rule K7 compliance: no segment-level occupancy or RevPAR.")
    
    # 4. Insight (a) checks: Overbooking buffer methodology & room conversion
    ob = findings["overbooking_and_mix"]["overbooking_buffer"]
    assert "v_overbooking_buffer" in insight_text
    assert "daily cancel rate" in insight_text.lower()
    assert "tenth percentile" in insight_text.lower() or "10th percentile" in insight_text.lower()
    assert "250" in insight_text # City capacity
    assert "210" in insight_text # Resort capacity
    assert "18.69%" in insight_text or "18.7%" in insight_text # City conservative rate
    assert "46.7 rooms" in insight_text or "47 rooms" in insight_text # City conservative rooms
    assert "10.78%" in insight_text or "10.8%" in insight_text # Resort conservative rate
    assert "22.6 rooms" in insight_text or "23 rooms" in insight_text # Resort conservative rooms
    
    # Pilot recommendation: HALF the conservative rate
    assert "half" in insight_text.lower()
    assert "9.35%" in insight_text # City half rate
    assert "23.4 rooms" in insight_text or "23 rooms" in insight_text
    assert "5.39%" in insight_text # Resort half rate
    assert "11.3 rooms" in insight_text or "11 rooms" in insight_text
    assert "heuristic" in insight_text.lower(), "Must state it is a heuristic for discussion"
    assert "no walk or compensation cost data" in insight_text.lower() or "walk" in insight_text.lower()
    assert "cancellations are only known after" in insight_text.lower() or "after the fact" in insight_text.lower()
    assert "$59,494.05" in insight_text # Scenario A1 total revenue
    assert "594.0" in insight_text # Scenario A1 total room nights
    print("PASS: Verified Insight (a) overbooking buffer parameters, pilot half-rate, operational rationale, and Scenario A1.")
    
    # 5. Insight (b) checks: Room-type mismatch as walk risk
    rm = findings["overbooking_and_mix"]["room_type_mismatch"]
    assert "14,114" in insight_text # Total mismatches
    assert "18.78%" in insight_text # Overall mismatch pct
    assert "6,774" in insight_text # City mismatches
    assert "14.65%" in insight_text # City mismatch pct
    assert "7,340" in insight_text # Resort mismatches
    assert "25.37%" in insight_text # Resort mismatch pct
    assert "53.46%" in insight_text # Resort peak winter mismatch (Jan 2016)
    assert "cannot say" in insight_text.lower(), "Must state what the data cannot say"
    assert "downgraded" in insight_text.lower(), "Must state whether guests were downgraded"
    assert "2,822.8" in insight_text # Scenario B1 protected stays
    print("PASS: Verified Insight (b) room mismatch rates, seasonal patterns, data limitations, and Scenario B1.")
    
    # 6. Insight (c) checks: Segment & Channel mix
    seg = findings["overbooking_and_mix"]["segment_performance"]
    chan = findings["overbooking_and_mix"]["channel_performance"]
    
    # Largest revenue share
    assert "61.1%" in insight_text # Online TA City rev share
    assert "42.8%" in insight_text # Online TA Resort rev share
    assert "84.7%" in insight_text # TA/TO City rev share
    assert "74.0%" in insight_text # TA/TO Resort rev share
    
    # Highest ADR
    assert "$120.51" in insight_text # Direct City ADR
    assert "$126.78" in insight_text # Direct Resort ADR
    assert "$115.09" in insight_text # Direct City Channel ADR
    assert "$116.43" in insight_text # Direct Resort Channel ADR
    
    # Lowest cancel rate
    assert "17.3%" in insight_text # Direct City cancel rate
    assert "13.5%" in insight_text # Direct Resort cancel rate
    assert "18.2%" in insight_text # Direct City Channel cancel rate
    assert "16.8%" in insight_text # Direct Resort Channel cancel rate
    
    # Underperformers
    assert "Groups" in insight_text
    assert "68.9%" in insight_text # City Groups cancel rate
    assert "$86.38" in insight_text # City Groups ADR
    assert "42.4%" in insight_text # Resort Groups cancel rate
    assert "$66.31" in insight_text # Resort Groups ADR
    assert "42.8%" in insight_text # Offline TA/TO City cancel rate
    assert "$88.85" in insight_text # Offline TA/TO City ADR
    
    # Scenario C1: Shift 2,000 room-nights
    assert "2,000" in insight_text # Shifted room nights
    assert "$34.13" in insight_text # City ADR spread
    assert "$68,260.00" in insight_text # City incremental rev
    assert "$60.47" in insight_text # Resort ADR spread
    assert "$120,940.00" in insight_text # Resort incremental rev
    assert "$189,200.00" in insight_text # Total incremental rev
    print("PASS: Verified Insight (c) segment and channel metrics, underperformers, and Scenario C1.")
    
    # Source tag pattern check
    source_tags = re.findall(r"\[([^\]]+\.csv[^\]]*)\]", insight_text)
    assert len(source_tags) >= 20, f"Expected at least 20 source tags, found {len(source_tags)}"
    print(f"PASS: Verified {len(source_tags)} bracketed CSV source citations in 03.")

def run():
    base_dir = Path(__file__).resolve().parent.parent
    findings_path = base_dir / "reports" / "findings_data.json"
    insight01_path = base_dir / "reports" / "insights" / "01_pricing_seasonality.md"
    insight02_path = base_dir / "reports" / "insights" / "02_cancellations.md"
    insight03_path = base_dir / "reports" / "insights" / "03_overbooking_mix.md"
    
    assert findings_path.exists(), f"Missing {findings_path}"
    assert insight01_path.exists(), f"Missing {insight01_path}"
    assert insight02_path.exists(), f"Missing {insight02_path}"
    assert insight03_path.exists(), f"Missing {insight03_path}"
    
    with open(findings_path, "r", encoding="utf-8") as f:
        findings = json.load(f)
        
    with open(insight01_path, "r", encoding="utf-8") as f:
        text01 = f.read()
        
    with open(insight02_path, "r", encoding="utf-8") as f:
        text02 = f.read()
        
    with open(insight03_path, "r", encoding="utf-8") as f:
        text03 = f.read()
        
    print("=== STARTING INSIGHTS VALIDATION SUITE ===")
    validate_01(findings, text01)
    validate_02(findings, text02)
    validate_03(findings, text03)
    print("\n=== ALL INSIGHTS AND FINDINGS VALIDATED 100% SUCCESSFULLY ===")

if __name__ == "__main__":
    run()

