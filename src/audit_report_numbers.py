"""
Audit report numbers against physical data marts, tables, and findings data.
Parses reports/insights_summary.md (if present) and reports/insights/*.md,
extracting all numbers and validating against findings_data.json and CSV outputs.
Checks for causal phrases and writes reports/tables/number_audit.csv.
"""

import json
import glob
import re
import sys
from pathlib import Path
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

def load_data_sources(base_dir: Path):
    findings_path = base_dir / "reports" / "findings_data.json"
    findings = json.load(open(findings_path, "r", encoding="utf-8")) if findings_path.exists() else {}
    
    indexed_numbers = [] # list of (float_val, source_label)
    indexed_dates = {}    # date_str -> list of source_labels
    
    def record_val(val, src):
        if val is None or val == "" or pd.isna(val):
            return
        s = str(val).strip()
        # Dates YYYY-MM-DD or YYYY-MM
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            indexed_dates.setdefault(s, []).append(src)
            # Also index year-month YYYY-MM
            ym = s[:7]
            indexed_dates.setdefault(ym, []).append(f"{src}:year_month")
            return
        if re.match(r"^\d{4}-\d{2}$", s):
            indexed_dates.setdefault(s, []).append(src)
            return
            
        # Clean numeric
        clean_s = s.replace(",", "").replace("$", "").replace("%", "").replace("+", "").strip()
        try:
            f = float(clean_s)
            indexed_numbers.append((f, src))
        except ValueError:
            # If string has embedded numbers (e.g. text cells), extract them
            embedded = re.findall(r"[\+\-]?\b\d[\d,]*(?:\.\d+)?\b", s)
            for emb in embedded:
                try:
                    f = float(emb.replace(",", ""))
                    indexed_numbers.append((f, f"{src}:embedded"))
                except ValueError:
                    pass

    def walk_json(obj, path):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk_json(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk_json(v, f"{path}[{i}]")
        else:
            record_val(obj, f"findings_data.json:{path}")

    walk_json(findings, "root")

    for f in sorted(glob.glob(str(base_dir / "reports" / "tables" / "*.csv"))):
        fname = Path(f).name
        try:
            df = pd.read_csv(f)
            for col in df.columns:
                for val in df[col]:
                    record_val(val, f"reports/tables/{fname}:{col}")
        except Exception:
            pass

    for f in sorted(glob.glob(str(base_dir / "data" / "outputs" / "*.csv"))):
        fname = Path(f).name
        try:
            df = pd.read_csv(f)
            for col in df.columns:
                for val in df[col]:
                    record_val(val, f"data/outputs/{fname}:{col}")
        except Exception:
            pass

    return indexed_numbers, indexed_dates

def load_allowlist(allowlist_path: Path):
    allowlist = {}
    if not allowlist_path.exists():
        return allowlist
    with open(allowlist_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                allowlist[parts[0].strip()] = parts[1].strip()
    return allowlist

def round_half_up(val: float, prec: int) -> float:
    try:
        d = Decimal(str(val))
        return float(round(d, prec))
    except Exception:
        return round(val, prec)

def match_value(raw_token: str, kind: str, indexed_numbers, indexed_dates, allowlist, snippet: str):
    # 1. Check allowlist against token or snippet context
    # Check if exact token is in allowlist
    if raw_token in allowlist:
        return f"Allowlist: {allowlist[raw_token]}"
    
    # Check if token is part of a labeled phrase in allowlist (e.g. K1, D5, Prompt 2.3, Group 1, etc.)
    for entry, reason in allowlist.items():
        if entry in snippet:
            # Verify if this token is actually part of that entry
            # E.g. token '1' in 'K1' or 'Group 1' or '1 in 2'
            if raw_token in entry.split() or raw_token in re.findall(r"\d+", entry):
                return f"Allowlist ({entry}): {reason}"
            if entry.startswith("### ") and entry.endswith(raw_token):
                return f"Allowlist ({entry}): {reason}"

    # 2. Check dates
    if kind == "date":
        if raw_token in indexed_dates:
            return indexed_dates[raw_token][0]
        return None

    # 3. Check numeric
    clean_token = raw_token.replace(",", "").replace("$", "").replace("%", "").replace("+", "").strip()
    try:
        target_val = float(clean_token)
    except ValueError:
        return None

    if "." in clean_token:
        prec = len(clean_token.split(".")[1])
    else:
        prec = 0

    # Search indexed numbers
    for db_val, src in indexed_numbers:
        # Check direct round (both python round and round_half_up)
        r1 = round(db_val, prec)
        r2 = round_half_up(db_val, prec)
        t = round(target_val, prec)
        if r1 == t or r2 == t:
            return src
        if kind == "pct":
            p1 = round(db_val * 100.0, prec)
            p2 = round_half_up(db_val * 100.0, prec)
            if p1 == t or p2 == t:
                return src
        else:
            d1 = round(db_val / 100.0, prec)
            d2 = round_half_up(db_val / 100.0, prec)
            if d1 == t or d2 == t:
                return src

    return None

def audit_causal_phrases(text: str, filename: str):
    causal_pattern = re.compile(r"\b(because|caused|drives|driven by|due to|leads to)\b", re.IGNORECASE)
    flagged = []
    # Split text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sent in sentences:
        sent_clean = sent.replace("\n", " ").strip()
        m = causal_pattern.search(sent_clean)
        if m:
            flagged.append((m.group(0), sent_clean, filename))
    return flagged

def run():
    base_dir = Path(__file__).resolve().parent.parent
    allowlist_path = base_dir / "reports" / "audit_allowlist.txt"
    allowlist = load_allowlist(allowlist_path)
    
    print("Loading data sources into index...")
    indexed_numbers, indexed_dates = load_data_sources(base_dir)
    print(f"Loaded {len(indexed_numbers)} numeric entries and {len(indexed_dates)} date entries.")
    
    target_files = []
    summary_file = base_dir / "reports" / "insights_summary.md"
    if summary_file.exists():
        target_files.append(summary_file)
    target_files.extend(sorted((base_dir / "reports" / "insights").glob("*.md")))
    
    print(f"Auditing {len(target_files)} target file(s): {[f.name for f in target_files]}")
    
    date_pat = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{4}-\d{2}\b")
    money_pat = re.compile(r"[\+\-]?\$(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
    pct_pat = re.compile(r"[\+\-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%")
    num_pat = re.compile(r"[\+\-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
    
    audit_rows = []
    all_causal = []
    
    for fpath in target_files:
        text = fpath.read_text(encoding="utf-8")
        
        # Check causal phrases
        causal = audit_causal_phrases(text, fpath.name)
        all_causal.extend(causal)
        
        lines = text.split("\n")
        for line_no, line in enumerate(lines, 1):
            clean_line = re.sub(r"\]\([^\)]+\)", "]", line) # Remove link URLs
            
            tokens = []
            for m in date_pat.finditer(clean_line):
                tokens.append((m.group(), m.start(), m.end(), "date"))
            for m in money_pat.finditer(clean_line):
                tokens.append((m.group(), m.start(), m.end(), "money"))
            for m in pct_pat.finditer(clean_line):
                tokens.append((m.group(), m.start(), m.end(), "pct"))
            for m in num_pat.finditer(clean_line):
                if not any(t[1] <= m.start() < t[2] or t[1] < m.end() <= t[2] for t in tokens):
                    tokens.append((m.group(), m.start(), m.end(), "num"))
            tokens.sort(key=lambda x: x[1])
            
            for tok, s, e, kind in tokens:
                snippet = clean_line[max(0, s-25):min(len(clean_line), e+25)].strip()
                matched_src = match_value(tok, kind, indexed_numbers, indexed_dates, allowlist, snippet)
                status = matched_src if matched_src else "UNMATCHED"
                audit_rows.append({
                    "file": fpath.name,
                    "line": line_no,
                    "number": tok,
                    "context snippet": snippet,
                    "matched source or UNMATCHED": status
                })
                
    audit_df = pd.DataFrame(audit_rows)
    out_csv = base_dir / "reports" / "tables" / "number_audit.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    audit_df[["number", "context snippet", "matched source or UNMATCHED"]].to_csv(out_csv, index=False)
    
    # Summary
    total_nums = len(audit_df)
    unmatched_df = audit_df[audit_df["matched source or UNMATCHED"] == "UNMATCHED"]
    unmatched_count = len(unmatched_df)
    allowlist_count = len(audit_df[audit_df["matched source or UNMATCHED"].str.startswith("Allowlist")])
    data_matched_count = total_nums - unmatched_count - allowlist_count
    
    print("\n" + "="*60)
    print("FINAL REPORT AUDIT SUMMARY")
    print("="*60)
    print(f"Files Audited:           {len(target_files)}")
    print(f"Total Numbers Audited:   {total_nums}")
    print(f"Matched to Data Sources: {data_matched_count}")
    print(f"Matched to Allowlist:    {allowlist_count}")
    print(f"UNMATCHED Figures:       {unmatched_count}")
    print(f"Causal Phrases Found:    {len(all_causal)}")
    print("="*60)
    
    if all_causal:
        print("\nFLAGGED CAUSAL SENTENCES (MUST BE REWRITTEN):")
        for word, sent, fn in all_causal:
            print(f"  [{fn}] Word '{word}': {sent}")
            
    if unmatched_count > 0:
        print(f"\nUNMATCHED FIGURES ({unmatched_count} remaining):")
        for _, r in unmatched_df.head(20).iterrows():
            print(f"  [{r['file']}:L{r['line']}] {r['number']} in snippet: {r['context snippet']}")
            
    assert len(all_causal) == 0, f"Audit failed: {len(all_causal)} causal sentence(s) remaining."
    assert unmatched_count == 0, f"Audit failed: {unmatched_count} unmatched figure(s) remaining."
    print("\nAUDIT PASSED: Zero UNMATCHED numbers and zero causal phrases remain.")

if __name__ == "__main__":
    run()
