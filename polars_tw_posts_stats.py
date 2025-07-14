import polars as pl
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
CSV_PATH   = Path("2024_tw_posts_president_scored_anon.csv")
REPORT_TXT = Path("polars_tw_posts_output.txt")

# ── WRITE-HELPER ──────────────────────────────────────────────
def write(line: str) -> None:
    """Append a line (and a blank line) to the report."""
    with REPORT_TXT.open("a", encoding="utf-8") as f:
        f.write(line + "\n\n")

# ── CLEANING ─────────────────────────────────────────────────
def clean(df: pl.DataFrame) -> pl.DataFrame:
    key_cols = ["like_count", "retweet_count", "user_id", "tweet_id"]
    df = df.drop_nulls(subset=[c for c in key_cols if c in df.columns])
    return df.fill_null("Unknown")

# ── MAIN ─────────────────────────────────────────────────────
def main() -> None:
    REPORT_TXT.unlink(missing_ok=True)      # fresh file each run

    # 1) Load & clean
    df = pl.read_csv(CSV_PATH, infer_schema_length=50_000)
    df = clean(df)

    write("===== Polars Descriptive Stats (Twitter Posts) =====")

    # 2) Column names
    write("--- Columns in Dataset ---")
    write(", ".join(df.columns))

    # 3) Overall describe()
    write("--- Overall describe() ---")
    write(str(df.describe()))

    # 4) Unique counts per column
    write("--- Unique Values per Column ---")
    for col in df.columns:
        n_unique = df.select(pl.col(col).n_unique()).item()
        write(f"{col}: {n_unique}")

    # 5) Top-5 user_id by frequency
    if "user_id" in df.columns:
        write("--- Top 5 Most-Frequent user_id ---")
        top_users = (
            df.group_by("user_id")
              .len()
              .sort("len", descending=True)
              .head(5)
        )
        write(str(top_users))

    # choose an engagement metric
    metric = None
    for cand in ("like_count", "favorite_count", "retweet_count", "reply_count", "quote_count"):
        if cand in df.columns:
            metric = cand
            break

    # 6) Grouped stats by user_id
    if metric and {"user_id", metric}.issubset(df.columns):
        write(f"--- Grouped by user_id ({metric}) ---")
        g1 = (
            df.group_by("user_id")
              .agg([
                  pl.count(metric).alias("count"),
                  pl.mean(metric).alias("mean"),
                  pl.min(metric).alias("min"),
                  pl.max(metric).alias("max"),
              ])
              .sort("count", descending=True)
              .head(5)
        )
        write(str(g1))

    # 7) Grouped stats by (user_id, tweet_id)
    if metric and {"user_id", "tweet_id", metric}.issubset(df.columns):
        write(f"--- Grouped by (user_id, tweet_id) ({metric}) ---")
        g2 = (
            df.group_by(["user_id", "tweet_id"])
              .agg([
                  pl.count(metric).alias("count"),
                  pl.mean(metric).alias("mean"),
                  pl.min(metric).alias("min"),
                  pl.max(metric).alias("max"),
              ])
              .sort("count", descending=True)
              .head(5)
        )
        write(str(g2))

    write("===== Script Completed =====")
    print(f"Report written to: {REPORT_TXT.resolve()}")

# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    main()