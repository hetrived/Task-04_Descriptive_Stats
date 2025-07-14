# facebook_posts_pandas.py

import pandas as pd
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
INPUT  = Path("2024_fb_posts_president_scored_anon.csv")
OUTPUT = Path("output_facebook_posts_pandas.txt")

# ── LOAD DATA ─────────────────────────────────────────────────
df = pd.read_csv(INPUT, low_memory=False)

report_lines = [
    f"Descriptive Statistics for: {INPUT.name}",
    "=" * 60,
]

# ── TABLE-WIDE SUMMARY ───────────────────────────────────────
report_lines.append("\n=== DataFrame.describe() (numeric) ===")
report_lines.append(df.describe().to_string())

report_lines.append("\n=== DataFrame.describe(include='object') ===")
report_lines.append(df.describe(include="object").to_string())

# ── COLUMN-WISE EXTRAS: TOP VALUE FOR CATEGORICALS ───────────
for col in df.select_dtypes(exclude="number"):
    top_val = df[col].mode(dropna=True)
    if not top_val.empty:
        report_lines.append(f"\nColumn: {col} – Top value: {top_val.iat[0]}")

# ── GROUPED SUMMARIES ────────────────────────────────────────
preferred_metric = next(
    (c for c in ("like_count", "reaction_count", "comment_count", "share_count") if c in df.columns),
    df.select_dtypes("number").columns[0],
)

if "page_id" in df.columns:
    grouped_page = df.groupby("page_id")[preferred_metric].agg(["count", "mean"])
    report_lines.append(
        f"\n=== Grouped by page_id on '{preferred_metric}' (first 5 rows) ==="
    )
    report_lines.append(grouped_page.head().to_string())

if {"page_id", "post_id"}.issubset(df.columns):
    grouped_page_post = (
        df.groupby(["page_id", "post_id"])[preferred_metric].agg(["count", "mean"])
    )
    report_lines.append(
        f"\n=== Grouped by page_id & post_id on '{preferred_metric}' (first 5 rows) ==="
    )
    report_lines.append(grouped_page_post.head().to_string())

# ── SAVE REPORT ──────────────────────────────────────────────
OUTPUT.write_text("\n".join(report_lines), encoding="utf-8")
print(f"Done! Output saved to: {OUTPUT}")
