#!/usr/bin/env python3
"""Leak Investigation Report Generator – CLI entry point."""

import argparse
import sys
from pathlib import Path

from leak_report.collector import collect_from_json, collect_interactive
from leak_report.reporters import generate_html, generate_markdown, generate_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="leak-report",
        description="Generate professional leak investigation reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode, output as HTML
  python main.py --interactive --format html --output report.html

  # Load from JSON, generate Markdown
  python main.py --input examples/sample_incident.json --format markdown

  # Load from JSON, print plain text to stdout
  python main.py --input examples/sample_incident.json --format text
        """,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--interactive", action="store_true",
                      help="Collect incident data interactively via prompts")
    mode.add_argument("--input", metavar="FILE",
                      help="Path to a JSON file containing incident data")

    parser.add_argument("--format", choices=["html", "markdown", "text"],
                        default="text", help="Output format (default: text)")
    parser.add_argument("--output", metavar="FILE",
                        help="Write report to this file (default: print to stdout)")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.interactive:
            report = collect_interactive()
        else:
            report = collect_from_json(args.input)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"Error loading incident data: {exc}", file=sys.stderr)
        return 1

    generators = {"html": generate_html, "markdown": generate_markdown, "text": generate_text}
    content = generators[args.format](report)

    if args.output:
        path = Path(args.output)
        path.write_text(content, encoding="utf-8")
        print(f"Report written to: {path}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
