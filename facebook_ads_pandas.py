# facebook_ads_pandas.py

import pandas as pd
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
INPUT  = Path("2024_fb_ads_president_scored_anon.csv")
OUTPUT = Path("output_facebook_ads_pandas.txt")

# ── LOAD DATA ─────────────────────────────────────────────────
df = pd.read_csv(INPUT, low_memory=False)

report = [
    f"Descriptive Statistics for: {INPUT.name}",
    "=" * 60,
]

# ── NUMERIC & OBJECT SUMMARIES (PANDAS BUILT-IN) ─────────────
report.append("\n=== DataFrame.describe() (numeric) ===")
report.append(df.describe().to_string())

report.append("\n=== DataFrame.describe(include='object') ===")
report.append(df.describe(include="object").to_string())

# ── TOP VALUE FOR EACH NON-NUMERIC COLUMN ────────────────────
for col in df.select_dtypes(exclude="number"):
    top = df[col].mode(dropna=True)
    if not top.empty:
        report.append(f"\nColumn: {col} – Top value: {top.iat[0]}")

# ── GROUPED STATISTICS ───────────────────────────────────────
# Choose a numeric metric to aggregate – prefer 'spend', else first numeric
metric = "spend" if "spend" in df.columns else df.select_dtypes("number").columns[0]

# Group by page_id
if "page_id" in df.columns:
    g1 = df.groupby("page_id")[metric].agg(["count", "mean"])
    report.append(f"\n=== Grouped by page_id on '{metric}' (first 5) ===")
    report.append(g1.head().to_string())

# Group by page_id + ad_id
if {"page_id", "ad_id"}.issubset(df.columns):
    g2 = df.groupby(["page_id", "ad_id"])[metric].agg(["count", "mean"])
    report.append(f"\n=== Grouped by page_id & ad_id on '{metric}' (first 5) ===")
    report.append(g2.head().to_string())

# ── WRITE REPORT ─────────────────────────────────────────────
OUTPUT.write_text("\n".join(report), encoding="utf-8")
print(f"Done! Output saved to: {OUTPUT}")
