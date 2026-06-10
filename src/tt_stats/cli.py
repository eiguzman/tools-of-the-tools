import argparse
import sys

from .parser import parse_tiktok_file
from .analyze import (
    find_not_following_back,
    generate_growth_chart,
    compare_followers,
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
        help="Output PNG path (default: follower_growth.png)",
    )
    gr.add_argument(
        "-b",
        "--bin",
        dest="bin_by",
        choices=["day", "week", "month"],
        default="day",
        help="Time grouping for the chart (default: day)",
    )

    co = subparsers.add_parser(
        "compare",
        help="Compare two TikTok data files to find unfollowers and new followers",
    )
    co.add_argument("old_file", help="Path to older TikTok data file")
    co.add_argument("new_file", help="Path to newer TikTok data file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "unfollow-back": _cmd_unfollow_back,
        "growth": _cmd_growth,
        "compare": _cmd_compare,
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
        output = generate_growth_chart(followers, args.output, args.bin_by)
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
