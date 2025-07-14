# facebook_posts_pure.py

import csv
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# ── CONFIG ────────────────────────────────────────────────────
INPUT  = Path("2024_fb_posts_president_scored_anon.csv")
OUTPUT = Path("output_facebook_posts_pure.txt")

# ── BASIC UTILITIES ───────────────────────────────────────────
is_num = lambda s: (lambda x: x.replace('.', '', 1).isdigit())(s)  # fast numeric test


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def group(rows: Iterable[Dict[str, str]], keys: Tuple[str, ...]):
    d: Dict[Tuple[str, ...], List[Dict[str, str]]] = defaultdict(list)
    for r in rows:
        d[tuple(r[k] for k in keys)].append(r)
    return d.items()


# ── COLUMN DESCRIPTION ───────────────────────────────────────
def describe_col(name: str, vals: List[str]) -> List[str]:
    out, vals = [f"\nColumn: {name}"], [v for v in vals if v.strip()]
    if vals and all(is_num(v) for v in vals[:20]):
        nums = list(map(float, vals))
        out += [
            f"  Count: {len(nums)}",
            f"  Mean:  {st.mean(nums):.2f}",
            f"  Min:   {min(nums)}",
            f"  Max:   {max(nums)}",
        ]
        if len(nums) > 1:
            out.append(f"  Std Dev: {st.stdev(nums):.2f}")
    else:
        top, cnt = (Counter(vals).most_common(1) + [('', 0)])[0]
        out += [
            f"  Unique Values: {len(set(vals))}",
            f"  Most Frequent: {top} ({cnt} times)",
        ]
    return out


# ── GROUP DESCRIPTION ────────────────────────────────────────
def describe_groups(label: str, grp, num_col: str) -> List[str]:
    out = [f"\nGrouped Summary: {label} on '{num_col}'"]
    for k, rows in list(grp)[:5]:
        nums = [float(r[num_col]) for r in rows if is_num(r.get(num_col, ""))]
        if nums:
            out.append(f"  Group {k}: Count={len(nums)}, Mean={st.mean(nums):.2f}")
    return out


# ── MAIN ─────────────────────────────────────────────────────
def main() -> None:
    data = list(read_csv(INPUT))

    # bucket values column-wise
    cols: Dict[str, List[str]] = defaultdict(list)
    for row in data:
        for k, v in row.items():
            cols[k].append(v)

    report = [
        f"Descriptive Statistics for: {INPUT.name}",
        "=" * 60,
    ]

    # 1) per-column stats
    for col, vals in cols.items():
        report += describe_col(col, vals)

    # 2) choose numeric column (prefer 'like_count', 'reaction_count', etc.)
    preferred = ("like_count", "reaction_count", "comment_count", "share_count")
    numeric   = [c for c, v in cols.items() if v and all(is_num(x) for x in v[:20])]
    target    = next((c for c in preferred if c in numeric), numeric[0] if numeric else None)

    # 3) group summaries
    #    • by page_id
    #    • by page_id & post_id (if post_id exists)
    if target:
        if "page_id" in cols:
            report += describe_groups("page_id", group(data, ("page_id",)), target)
        if "page_id" in cols and "post_id" in cols:
            report += describe_groups(
                "page_id & post_id", group(data, ("page_id", "post_id")), target
            )

    # write to disk
    OUTPUT.write_text("\n".join(report), encoding="utf-8")
    print(f"\nDone! Output saved to: {OUTPUT}")


if __name__ == "__main__":
    main()