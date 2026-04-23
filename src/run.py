from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build swipe-file collection assets")
    parser.add_argument("--input", required=True, help="Swipe CSV")
    parser.add_argument("--output", default="out", help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    buckets: dict[str, list[dict]] = defaultdict(list)
    with open(args.input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = (row.get("category") or "general").strip().lower()
            buckets[category].append(row)

    with open(out / "bundle_summary.csv", "w", encoding="utf-8", newline="") as f:
        fields = ["category", "count", "suggested_price"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for cat, items in sorted(buckets.items()):
            suggested_price = 19 + len(items) * 2
            writer.writerow({"category": cat, "count": len(items), "suggested_price": suggested_price})

    for cat, items in buckets.items():
        md_lines = [f"# Swipe Bundle - {cat.title()}", ""]
        for idx, item in enumerate(items, start=1):
            md_lines.extend(
                [
                    f"## Swipe {idx}",
                    f"- Use case: {item.get('use_case','')}",
                    "```text",
                    item.get("swipe_text", ""),
                    "```",
                    "",
                ]
            )
        (out / f"bundle_{cat}.md").write_text("\n".join(md_lines), encoding="utf-8")

    listing = (
        "# Swipe Collection Listing Draft\n\n"
        "## Offer\n"
        "Practical swipe templates for outreach, offers, and follow-ups.\n\n"
        "## Tiers\n"
        "- Starter: 25 swipes\n"
        "- Pro: 75 swipes\n"
        "- Agency: 150+ swipes\n\n"
        "## Checkout\n"
        "Payment link placeholder: https://buy.stripe.com/your-link\n"
    )
    (out / "listing_draft.md").write_text(listing, encoding="utf-8")

    print(f"Generated {len(buckets)} bundles -> {out}")


if __name__ == "__main__":
    main()
