# twitter_posts_pandas.py

import pandas as pd
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
INPUT  = Path("2024_tw_posts_president_scored_anon.csv")
OUTPUT = Path("output_twitter_posts_pandas.txt")

# ── LOAD DATA ─────────────────────────────────────────────────
df = pd.read_csv(INPUT, low_memory=False)

report = [
    f"Descriptive Statistics for: {INPUT.name}",
    "=" * 60,
]

# ── BUILT-IN SUMMARIES ───────────────────────────────────────
report.append("\n=== DataFrame.describe() (numeric) ===")
report.append(df.describe().to_string())

report.append("\n=== DataFrame.describe(include='object') ===")
report.append(df.describe(include="object").to_string())

# ── TOP VALUES FOR CATEGORICALS ──────────────────────────────
for col in df.select_dtypes(exclude="number"):
    mode = df[col].mode(dropna=True)
    if not mode.empty:
        report.append(f"\nColumn: {col} – Top value: {mode.iat[0]}")

# ── GROUPED STATISTICS ───────────────────────────────────────
# Pick an engagement metric if present, else first numeric
preferred = (
    "like_count",
    "favorite_count",
    "retweet_count",
    "reply_count",
    "quote_count",
)
numeric_cols = df.select_dtypes("number").columns
metric = next((c for c in preferred if c in numeric_cols), numeric_cols[0])

# Group by user_id
if "user_id" in df.columns:
    g_user = df.groupby("user_id")[metric].agg(["count", "mean"])
    report.append(f"\n=== Grouped by user_id on '{metric}' (first 5) ===")
    report.append(g_user.head().to_string())

# Group by user_id + tweet_id
if {"user_id", "tweet_id"}.issubset(df.columns):
    g_user_tw = df.groupby(["user_id", "tweet_id"])[metric].agg(["count", "mean"])
    report.append(
        f"\n=== Grouped by user_id & tweet_id on '{metric}' (first 5) ==="
    )
    report.append(g_user_tw.head().to_string())

# ── WRITE REPORT ─────────────────────────────────────────────
OUTPUT.write_text("\n".join(report), encoding="utf-8")
print(f"Done! Output saved to: {OUTPUT}")
