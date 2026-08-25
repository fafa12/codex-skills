#!/usr/bin/env python3
"""Save a generated report under the user's per-type document directory."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


TYPE_DIRS = {"daily": "日报", "weekly": "周报", "monthly": "月报"}


def format_date_range(start: dt.date, end: dt.date) -> str:
    """Format a weekly filename stem using its Monday-Sunday date range."""
    return f"{start.year}年{start.month}月{start.day}号-{end.year}年{end.month}月{end.day}号"


def weekly_stem(date_value: dt.date) -> str:
    """Return the canonical filename stem for the ISO week containing date_value."""
    start = date_value - dt.timedelta(days=date_value.weekday())
    return format_date_range(start, start + dt.timedelta(days=6))


def parse_period(report_type: str, value: str | None) -> tuple[str, str]:
    """Return the canonical filename stem and a human-readable period."""
    if not value:
        today = dt.date.today()
        if report_type == "daily":
            return today.isoformat(), today.isoformat()
        if report_type == "weekly":
            stem = weekly_stem(today)
            return stem, stem
        return today.strftime("%Y-%m"), today.strftime("%Y-%m")

    value = value.strip()
    if report_type == "daily":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("日报周期必须是 YYYY-MM-DD")
        dt.date.fromisoformat(value)
        return value, value

    if report_type == "weekly":
        if re.fullmatch(r"\d{4}-W\d{2}", value, re.IGNORECASE):
            year, week = value[:4], int(value[6:])
            try:
                monday = dt.date.fromisocalendar(int(year), week, 1)
            except ValueError as exc:
                raise ValueError("周报 ISO 周不是该年份的有效周") from exc
            stem = format_date_range(monday, monday + dt.timedelta(days=6))
            return stem, stem
        try:
            date_value = dt.date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("周报周期必须是 YYYY-Www 或 YYYY-MM-DD") from exc
        stem = weekly_stem(date_value)
        return stem, stem

    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = map(int, value.split("-"))
        dt.date(year, month, 1)
        return value, value
    try:
        date_value = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("月报周期必须是 YYYY-MM 或 YYYY-MM-DD") from exc
    stem = date_value.strftime("%Y-%m")
    return stem, stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=sorted(TYPE_DIRS), required=True)
    parser.add_argument("--period", help="YYYY-MM-DD, YYYY-Www, or YYYY-MM")
    parser.add_argument("--content-file", type=Path, help="UTF-8 Markdown file; omit to read stdin")
    parser.add_argument("--root", type=Path, default=Path(r"C:\00work\文档"))
    parser.add_argument("--filename", help="Optional .md filename within the mapped directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing canonical file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        stem, _ = parse_period(args.type, args.period)
        if args.content_file:
            content = args.content_file.read_text(encoding="utf-8")
        else:
            content = sys.stdin.read()
        if not content.strip():
            raise ValueError("报告内容为空")

        target_dir = (args.root / TYPE_DIRS[args.type]).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        if args.filename:
            filename = Path(args.filename).name
            if filename != args.filename:
                raise ValueError("--filename 只能是对应目录内的文件名")
            if not filename.lower().endswith(".md"):
                filename += ".md"
        else:
            filename = f"{stem}.md"

        target = target_dir / filename
        if target.exists() and not args.overwrite:
            timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            target = target_dir / f"{target.stem}-draft-{timestamp}{target.suffix}"

        target.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
        print(target)
        return 0
    except (OSError, ValueError) as exc:
        print(f"save_report.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
