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


def write_outreach_hooks(out: Path) -> None:
    hooks = (
        "# Outreach Hooks\n\n"
        "1. I assembled a swipe bundle your team can ship this week. Want the sample set?\n"
        "2. We can package scripts by channel and buyer stage in one day.\n"
        "3. If this is not relevant, reply unsubscribe and I will stop outreach.\n"
    )
    (out / "outreach_hooks.md").write_text(hooks, encoding="utf-8")


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
        fields = ["category", "count", "suggested_price", "stripe_link"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for cat, items in sorted(buckets.items()):
            suggested_price = 19 + len(items) * 2
            writer.writerow(
                {
                    "category": cat,
                    "count": len(items),
                    "suggested_price": suggested_price,
                    "stripe_link": "https://buy.stripe.com/swipe-growth-placeholder",
                }
            )

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
        md_lines.extend(
            [
                "## Onboarding",
                "- Form: https://forms.gle/swipe-onboarding-placeholder",
                "",
                "## Checkout",
                "- Starter: https://buy.stripe.com/swipe-starter-placeholder",
                "- Growth: https://buy.stripe.com/swipe-growth-placeholder",
                "- Operator: https://buy.stripe.com/swipe-operator-placeholder",
                "",
                "## Outreach hook",
                "Want a category-matched swipe pack for your current campaign sprint?",
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
        "## Onboarding\n"
        "- Form: https://forms.gle/swipe-onboarding-placeholder\n\n"
        "## Checkout\n"
        "- Starter: https://buy.stripe.com/swipe-starter-placeholder\n"
        "- Pro: https://buy.stripe.com/swipe-growth-placeholder\n"
        "- Agency: https://buy.stripe.com/swipe-operator-placeholder\n"
    )
    (out / "listing_draft.md").write_text(listing, encoding="utf-8")

    write_outreach_hooks(out)
    print(f"Generated {len(buckets)} bundles -> {out}")


if __name__ == "__main__":
    main()
