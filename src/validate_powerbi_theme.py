"""
Power BI Theme Validator & WCAG Contrast Engine: src/validate_powerbi_theme.py

Validates powerbi/theme/hotel_theme.json:
1. Valid JSON structure and required theme schema properties.
2. Strict 6-digit hex format (^#[0-9A-Fa-f]{6}$) for all color definitions.
3. WCAG contrast ratio of foreground against background (>= 7.0:1, AAA level).
4. WCAG contrast ratio of every dataColor against white (>= 3.0:1, graphical UI requirement).
5. Prints formatted verification and contrast results table.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
THEME_FILE = REPO_ROOT / "powerbi" / "theme" / "hotel_theme.json"

HEX_REGEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def relative_luminance(hex_code: str) -> float:
    """Compute WCAG 2.1 relative luminance for an sRGB hex code."""
    hex_clean = hex_code.lstrip("#")
    r, g, b = [int(hex_clean[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def to_linear(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r_lin = to_linear(r)
    g_lin = to_linear(g)
    b_lin = to_linear(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    """Compute WCAG contrast ratio between two colors."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def collect_all_hex_colors(obj, hex_list=None):
    """Recursively collect all color hex strings from theme JSON."""
    if hex_list is None:
        hex_list = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("#"):
                hex_list.append((k, v))
            else:
                collect_all_hex_colors(v, hex_list)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str) and item.startswith("#"):
                hex_list.append(("list_item", item))
            else:
                collect_all_hex_colors(item, hex_list)

    return hex_list


def validate_theme():
    print("=" * 105)
    print("POWER BI REPORT THEME VALIDATION ENGINE: powerbi/theme/hotel_theme.json")
    print("=" * 105)

    if not THEME_FILE.exists():
        print(f"[FAIL] Missing theme file: {THEME_FILE}")
        return False

    # 1. JSON Parse
    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            theme = json.load(f)
        print("[PASS] Theme file successfully parsed as valid JSON.")
    except Exception as e:
        print(f"[FAIL] JSON parsing error: {e}")
        return False

    all_passed = True

    # 2. Schema Properties Check
    assert theme.get("name") == "Hotel Analytics", "Theme name must be 'Hotel Analytics'"
    data_colors = theme.get("dataColors", [])
    if len(data_colors) != 8:
        print(f"[FAIL] Expected 8 dataColors, found {len(data_colors)}")
        all_passed = False
    else:
        print(f"[PASS] Exact 8 dataColors defined.")

    bg = theme.get("background", "")
    fg = theme.get("foreground", "")
    table_accent = theme.get("tableAccent", "")
    if bg != "#FFFFFF":
        print(f"[FAIL] Background must be #FFFFFF, found {bg}")
        all_passed = False
    if fg != "#252423":
        print(f"[FAIL] Foreground must be #252423, found {fg}")
        all_passed = False
    if table_accent != data_colors[0]:
        print(f"[FAIL] tableAccent ({table_accent}) must match first dataColor ({data_colors[0]})")
        all_passed = False
    else:
        print(f"[PASS] tableAccent matches primary dataColor ({table_accent}).")

    # 3. Check Hex Regex on all colors
    all_colors = collect_all_hex_colors(theme)
    invalid_hex = []
    for key, c in all_colors:
        if not HEX_REGEX.match(c):
            invalid_hex.append((key, c))

    if invalid_hex:
        print(f"[FAIL] Found invalid hex codes: {invalid_hex}")
        all_passed = False
    else:
        print(f"[PASS] All {len(all_colors)} color definitions strictly match 6-digit hex format (^#[0-9A-Fa-f]{{6}}$).")

    # 4. WCAG Contrast Check: Foreground vs Background
    fg_bg_ratio = wcag_contrast_ratio(fg, bg)
    fg_bg_pass = fg_bg_ratio >= 7.0
    print(f"[{'PASS' if fg_bg_pass else 'FAIL'}] Foreground ({fg}) vs Background ({bg}) Contrast: {fg_bg_ratio:.2f}:1 (Target: >= 7.0:1)")
    if not fg_bg_pass:
        all_passed = False

    # 5. WCAG Contrast Check: Each dataColor vs White
    print("\n" + "-" * 105)
    print(f"{'INDEX':<6} | {'COLOR HEX':<10} | {'ROLE / SERIES NAME':<25} | {'CONTRAST RATIO':<16} | {'TARGET':<10} | {'STATUS'}")
    print("-" * 105)

    roles = [
        "City Hotel (Primary Series)",
        "Resort Hotel (Secondary Series)",
        "Teal / Tertiary Series",
        "Purple / Quaternary Series",
        "Slate Steel / 5th Series",
        "Deep Amber / 6th Series",
        "Burgundy / 7th Series",
        "Indigo / 8th Series",
    ]

    for idx, hex_code in enumerate(data_colors, 1):
        ratio = wcag_contrast_ratio(hex_code, "#FFFFFF")
        passed = ratio >= 3.0
        if not passed:
            all_passed = False
        stat_str = "PASS" if passed else "FAIL"
        role_name = roles[idx - 1] if idx <= len(roles) else f"Series {idx}"
        print(f"{idx:<6} | {hex_code:<10} | {role_name:<25} | {ratio:>6.2f}:1         | >= 3.0:1   | [{stat_str}]")

    print("-" * 105)

    # Status & Center/Min/Max check
    good = theme.get("good")
    neutral = theme.get("neutral")
    bad = theme.get("bad")
    print(f"KPI Status Colors: Good={good} ({wcag_contrast_ratio(good, '#FFFFFF'):.2f}:1), Neutral={neutral} ({wcag_contrast_ratio(neutral, '#FFFFFF'):.2f}:1), Bad={bad} ({wcag_contrast_ratio(bad, '#FFFFFF'):.2f}:1)")

    # Text Classes check
    tc = theme.get("textClasses", {})
    expected_tc = {
        "callout": 28,
        "title": 14,
        "header": 12,
        "label": 10
    }
    tc_valid = True
    for cname, expected_size in expected_tc.items():
        entry = tc.get(cname, {})
        if entry.get("fontFace") != "Segoe UI" or entry.get("fontSize") != expected_size:
            print(f"[FAIL] textClasses.{cname} invalid: {entry}")
            tc_valid = False
            all_passed = False
    if tc_valid:
        print("[PASS] textClasses (callout: 28, title: 14, header: 12, label: 10, fontFace: 'Segoe UI') strictly verified.")

    print("=" * 105)
    if all_passed:
        print("POWER BI THEME VERIFICATION: ALL THEME CRITERIA PASSED [PASS]")
    else:
        print("POWER BI THEME VERIFICATION: CHECKS FAILED [FAIL]")
    print("=" * 105)

    return all_passed


def test_theme():
    """Pytest entrypoint for theme validation."""
    assert validate_theme() is True


def main():
    ok = validate_theme()
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
