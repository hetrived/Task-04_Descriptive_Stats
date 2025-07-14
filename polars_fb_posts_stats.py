import polars as pl
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
CSV_PATH   = Path("2024_fb_posts_president_scored_anon.csv")
REPORT_TXT = Path("polars_fb_posts_output.txt")

# ── WRITE-HELPER ──────────────────────────────────────────────
def write(line: str) -> None:
    """Append a line and a blank line to the report file."""
    with REPORT_TXT.open("a", encoding="utf-8") as f:
        f.write(line + "\n\n")

# ── CLEANING ─────────────────────────────────────────────────
def clean(df: pl.DataFrame) -> pl.DataFrame:
    key_cols = ["like_count", "comment_count", "page_id", "post_id"]
    df = df.drop_nulls(subset=[c for c in key_cols if c in df.columns])
    return df.fill_null("Unknown")

# ── MAIN ─────────────────────────────────────────────────────
def main() -> None:
    REPORT_TXT.unlink(missing_ok=True)  # fresh file each run

    # 1) Load & clean
    df = pl.read_csv(CSV_PATH, infer_schema_length=50_000)
    df = clean(df)

    write("===== Polars Descriptive Stats (Facebook Posts) =====")

    # 2) Column names
    write("--- Columns in Dataset ---")
    write(", ".join(df.columns))

    # 3) Overall describe()
    write("--- Overall describe() ---")
    write(str(df.describe()))

    # 4) Unique counts per column
    write("--- Unique Values per Column ---")
    uniq_counts = {
        col: df.select(pl.col(col).n_unique()).item() for col in df.columns
    }
    for k, v in uniq_counts.items():
        write(f"{k}: {v}")

    # 5) Top-5 page_id
    if "page_id" in df.columns:
        write("--- Top 5 Most-Frequent page_id ---")
        top_pages = (
            df.group_by("page_id")
              .len()
              .sort("len", descending=True)
              .head(5)
        )
        write(str(top_pages))

    # 6) Grouped stats by page_id  (using like_count if present)
    target = "like_count" if "like_count" in df.columns else None
    if target and {"page_id", target}.issubset(df.columns):
        write(f"--- Grouped by page_id ({target}) ---")
        g1 = (
            df.group_by("page_id")
              .agg([
                  pl.count(target).alias("count"),
                  pl.mean(target).alias("mean"),
                  pl.min(target).alias("min"),
                  pl.max(target).alias("max"),
              ])
              .sort("count", descending=True)
              .head(5)
        )
        write(str(g1))

    # 7) Grouped stats by (page_id, post_id)
    if target and {"page_id", "post_id", target}.issubset(df.columns):
        write(f"--- Grouped by (page_id, post_id) ({target}) ---")
        g2 = (
            df.group_by(["page_id", "post_id"])
              .agg([
                  pl.count(target).alias("count"),
                  pl.mean(target).alias("mean"),
                  pl.min(target).alias("min"),
                  pl.max(target).alias("max"),
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