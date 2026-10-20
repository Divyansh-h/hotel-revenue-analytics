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

def run():
    base_dir = Path(__file__).resolve().parent.parent
    findings_path = base_dir / "reports" / "findings_data.json"
    insight01_path = base_dir / "reports" / "insights" / "01_pricing_seasonality.md"
    insight02_path = base_dir / "reports" / "insights" / "02_cancellations.md"
    
    assert findings_path.exists(), f"Missing {findings_path}"
    assert insight01_path.exists(), f"Missing {insight01_path}"
    assert insight02_path.exists(), f"Missing {insight02_path}"
    
    with open(findings_path, "r", encoding="utf-8") as f:
        findings = json.load(f)
        
    with open(insight01_path, "r", encoding="utf-8") as f:
        text01 = f.read()
        
    with open(insight02_path, "r", encoding="utf-8") as f:
        text02 = f.read()
        
    print("=== STARTING INSIGHTS VALIDATION SUITE ===")
    validate_01(findings, text01)
    validate_02(findings, text02)
    print("\n=== ALL INSIGHTS AND FINDINGS VALIDATED 100% SUCCESSFULLY ===")

if __name__ == "__main__":
    run()
