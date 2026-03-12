from __future__ import annotations

import argparse
from pathlib import Path


ASSET_PREFIXES = (
    "style_",
    "coverage_html_",
    "favicon_",
    "keybd_",
)


def _replace_asset_refs(html: str, *, report_dir: Path) -> str:
    for entry in report_dir.iterdir():
        if not entry.is_file():
            continue
        if not any(entry.name.startswith(prefix) for prefix in ASSET_PREFIXES):
            continue

        html = html.replace(f'"{entry.name}"', f'"{entry.resolve()}"')
    return html


def postprocess_report(*, report_dir: Path) -> int:
    html_files = sorted(report_dir.glob("*.html"))
    for html_file in html_files:
        original = html_file.read_text(encoding="utf-8")
        updated = _replace_asset_refs(original, report_dir=report_dir)
        if updated != original:
            html_file.write_text(updated, encoding="utf-8")
    return len(html_files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rewrite coverage HTML asset links to absolute file paths.",
    )
    parser.add_argument("report_dir", help="coverage html directory")
    args = parser.parse_args()

    count = postprocess_report(report_dir=Path(args.report_dir).resolve())
    print(f"Post-processed {count} HTML files in {Path(args.report_dir).resolve()}")


if __name__ == "__main__":
    main()
