import argparse
import sys
import re
import os
from datetime import datetime

from .parser import parse_tiktok_file
from .analyze import (
    find_not_following_back,
    generate_growth_chart,
    compare_followers,
    generate_change_chart,
    _extract_date_from_filename,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze your TikTok follower data locally. No data is uploaded anywhere."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    ub = subparsers.add_parser(
        "unfollow-back", help="List people you follow who do not follow you back"
    )
    ub.add_argument("file", help="Path to TikTok data file (.json or .zip)")

    gr = subparsers.add_parser(
        "growth", help="Generate a follower growth chart (PNG)"
    )
    gr.add_argument("file", help="Path to TikTok data file (.json or .zip)")
    gr.add_argument(
        "-o",
        "--output",
        default="follower_growth.png",
        help="Output PNG path (default: follower_growth.png, relative to current working directory)",
    )
    gr.add_argument(
        "-b",
        "--bin",
        dest="bin_by",
        choices=["day", "week", "month"],
        default="day",
        help="Time grouping for the chart (default: day)",
    )
    gr.add_argument(
        "-s",
        "--start",
        help="Start date (YYYY-MM-DD) — only include followers from this date onward",
    )
    gr.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it exists instead of creating a numbered copy",
    )

    co = subparsers.add_parser(
        "compare",
        help="Compare two TikTok data files to find unfollowers and new followers",
    )
    co.add_argument("old_file", help="Path to older TikTok data file")
    co.add_argument("new_file", help="Path to newer TikTok data file")

    cc = subparsers.add_parser(
        "change-chart",
        help="Generate a bar chart showing followers gained and lost between snapshots",
    )
    cc.add_argument("old_file", help="Path to older TikTok data file")
    cc.add_argument("new_file", help="Path to newer TikTok data file")
    cc.add_argument(
        "-o",
        "--output",
        default="follower_change.png",
        help="Output PNG path (default: follower_change.png, relative to current working directory)",
    )
    cc.add_argument(
        "--history",
        default="follower_change_history.json",
        help="JSON file tracking change history across runs (default: follower_change_history.json, relative to current working directory)",
    )
    cc.add_argument(
        "-d",
        "--date",
        help="Export date for the new file (YYYY-MM-DD). If omitted, extracted from filename or current date.",
    )
    cc.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing history and start a fresh chart",
    )
    cc.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it exists instead of creating a numbered copy",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "unfollow-back": _cmd_unfollow_back,
        "growth": _cmd_growth,
        "compare": _cmd_compare,
        "change-chart": _cmd_change_chart,
    }
    commands[args.command](args)


def _cmd_unfollow_back(args):
    try:
        followers, followings = parse_tiktok_file(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    not_following = find_not_following_back(followers, followings)

    if not_following:
        print(
            f"People you follow who do NOT follow you back ({len(not_following)}):"
        )
        for name in not_following:
            print(f"  - {name}")
    else:
        print("Everyone you follow follows you back!")


def _cmd_growth(args):
    try:
        followers, _ = parse_tiktok_file(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not followers:
        print("No followers found in the data.", file=sys.stderr)
        sys.exit(1)

    try:
        output = generate_growth_chart(followers, args.output, args.bin_by, start=args.start, overwrite=args.overwrite)
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Follower growth chart saved to: {output}")


def _cmd_compare(args):
    try:
        old_followers, _ = parse_tiktok_file(args.old_file)
    except Exception as e:
        print(f"Error reading old file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        new_followers, _ = parse_tiktok_file(args.new_file)
    except Exception as e:
        print(f"Error reading new file: {e}", file=sys.stderr)
        sys.exit(1)

    unfollowed, gained = compare_followers(old_followers, new_followers)

    if unfollowed:
        print(f"Unfollowers ({len(unfollowed)}):")
        for name in unfollowed:
            print(f"  - {name}")
    else:
        print("No one unfollowed you between the two files.")

    if gained:
        print(f"\nNew followers ({len(gained)}):")
        for name in gained:
            print(f"  - {name}")
    else:
        print("\nNo new followers.")


def _cmd_change_chart(args):
    try:
        old_followers, _ = parse_tiktok_file(args.old_file)
    except Exception as e:
        print(f"Error reading old file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        new_followers, _ = parse_tiktok_file(args.new_file)
    except Exception as e:
        print(f"Error reading new file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.date:
        export_date = args.date
    else:
        export_date = _extract_date_from_filename(args.new_file)
        if not export_date:
            export_date = datetime.now().strftime("%Y-%m-%d")

    try:
        output = generate_change_chart(
            old_followers,
            new_followers,
            export_date,
            history_path=args.history,
            output_path=args.output,
            reset=args.reset,
            overwrite=args.overwrite,
        )
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Follower change chart saved to: {output}")
