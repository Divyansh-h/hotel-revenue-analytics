# Power BI Custom Report Theme: Hotel Analytics

This directory contains the custom enterprise Power BI theme [`hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json) designed for the Hotel Revenue & Occupancy Analytics dashboard.

---

## 1. How to Import the Theme into Power BI Desktop

Follow these simple steps to apply the theme to your Power BI report:

1. Launch **Power BI Desktop** and open your report file (`.pbix`).
2. On the top ribbon, click on the **View** tab.
3. In the **Themes** section, click the dropdown arrow to expand the theme gallery.
4. Near the bottom of the dropdown menu, select **Browse for themes...**
5. Navigate to the project directory:
   ```text
   powerbi/theme/hotel_theme.json
   ```
6. Select `hotel_theme.json` and click **Open**.
7. Power BI will apply the custom palette, typography, card formatting, and visual containers, displaying a confirmation message:
   > *"Theme imported successfully"*

---

## 2. Color Palette & WCAG 2.1 Contrast Standards

All 8 primary data colors were selected to be **color-blind-safe** (deuteranopia, protanopia, and tritanopia compliant) while ensuring clear distinction between the two hotel properties. Every data color meets or exceeds the **WCAG 2.1 graphical object contrast threshold (>= 3.0:1)** against white (`#FFFFFF`), and the foreground text color achieves **AAA contrast (15.49:1)**.

| Index | Color Hex | Color Swatch | Assigned Semantic Role | Contrast vs #FFFFFF | WCAG Status |
| :-: | :-: | :-: | :--- | :-: | :-: |
| **1** | `#1A365D` | Deep Navy | **City Hotel (Primary Series)** | **12.14:1** | **PASS** (>= 3.0:1) |
| **2** | `#C05621` | Terracotta Amber | **Resort Hotel (Secondary Series)** | **4.57:1** | **PASS** (>= 3.0:1) |
| **3** | `#0D7680` | Teal Slate | Tertiary Series (e.g. Transient) | **5.36:1** | **PASS** (>= 3.0:1) |
| **4** | `#6B21A8` | Deep Purple | Quaternary Series (e.g. Online TA) | **8.72:1** | **PASS** (>= 3.0:1) |
| **5** | `#334155` | Slate Steel | 5th Series (e.g. Offline TA/TO) | **10.35:1** | **PASS** (>= 3.0:1) |
| **6** | `#854D0E` | Bronze Olive | 6th Series (e.g. Direct) | **6.85:1** | **PASS** (>= 3.0:1) |
| **7** | `#9F1239` | Rose Burgundy | 7th Series (e.g. Corporate) | **8.02:1** | **PASS** (>= 3.0:1) |
| **8** | `#3730A3` | Deep Indigo | 8th Series (e.g. Groups) | **9.93:1** | **PASS** (>= 3.0:1) |

---

## 3. Secondary & Functional Color Tokens

- **Background**: `#FFFFFF` (Pure White, 0% transparency)
- **Foreground / Primary Text**: `#252423` (Off-black slate; **15.49:1 contrast ratio** against white background, exceeding the 7.0:1 AAA threshold)
- **Table Accent**: `#1A365D` (Matches City Hotel primary data color)
- **Card & Visual Borders**: `#E2E8F0` (Subtle 1px border with 4px corner radius)
- **KPI Status Indicators**:
  - **Good / High Performer**: `#2E7D32` (Forest Green, 5.13:1 contrast)
  - **Neutral**: `#F9A825` (Amber Gold, 1.97:1 contrast)
  - **Bad / Underperformer**: `#C62828` (Crimson Red, 5.62:1 contrast)
- **Diverging Color Scales**:
  - `maximum`: `#2E7D32` (Good)
  - `center`: `#F9A825` (Neutral)
  - `minimum`: `#C62828` (Bad)

---

## 4. Typography Standards (`Segoe UI`)

| Class | Font Face | Size | Weight / Color | Usage |
| :--- | :--- | :-: | :--- | :--- |
| **`callout`** | Segoe UI | **28 pt** | Semi-Bold / `#252423` | Headline KPI Card numbers |
| **`title`** | Segoe UI | **14 pt** | Semi-Bold / `#252423` | Visual container titles |
| **`header`** | Segoe UI | **12 pt** | Medium / `#252423` | Column headers, axis titles |
| **`label`** | Segoe UI | **10 pt** | Regular / `#718096` | Subtitles, data labels, axis ticks |

---

## 5. Automated Validation Engine

To re-verify the theme JSON syntax, hex regex conformity, and WCAG contrast ratios, run:

```bash
python src/validate_powerbi_theme.py
```

Or execute via `pytest`:

```bash
pytest src/validate_powerbi_theme.py
```
