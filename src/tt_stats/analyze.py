import json
import os
import re
from collections import Counter
from datetime import datetime
from typing import List, Dict, Tuple, Optional


def _resolve_output_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(f"{base}_{n}{ext}"):
        n += 1
    return f"{base}_{n}{ext}"


def find_not_following_back(
    followers: List[Dict[str, str]],
    followings: List[Dict[str, str]],
) -> List[str]:
    follower_names = {f["UserName"] for f in followers if f.get("UserName")}
    return [
        f["UserName"]
        for f in followings
        if f.get("UserName") and f["UserName"] not in follower_names
    ]


def get_follower_growth(
    followers: List[Dict[str, str]], bin_by: str = "day"
) -> Dict[str, int]:
    counts: Counter = Counter()
    for f in followers:
        date_str = f.get("Date", "")
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        if bin_by == "day":
            key = dt.strftime("%Y-%m-%d")
        elif bin_by == "week":
            year, week, _ = dt.isocalendar()
            key = f"{year}-W{week:02d}"
        elif bin_by == "month":
            key = dt.strftime("%Y-%m")
        else:
            key = dt.strftime("%Y-%m-%d")
        counts[key] += 1

    return {k: counts[k] for k in sorted(counts)}


def generate_growth_chart(
    followers: List[Dict[str, str]],
    output_path: str = "follower_growth.png",
    bin_by: str = "day",
    start: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    try:
        plt.style.use("seaborn-v0_8")
    except OSError:
        plt.style.use("ggplot")

    if not overwrite:
        output_path = _resolve_output_path(output_path)

    if start:
        filtered = []
        for f in followers:
            d = f.get("Date", "")
            if d and d[:10] >= start:
                filtered.append(f)
        followers = filtered

    growth = get_follower_growth(followers, bin_by)
    if not growth:
        raise ValueError("No valid follower data to plot")

    dates = list(growth.keys())
    counts = list(growth.values())

    if bin_by == "day":
        x_dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    elif bin_by == "week":
        x_dates = [datetime.strptime(d + "-1", "%G-W%V-%u") for d in dates]
    else:
        x_dates = [datetime.strptime(d, "%Y-%m") for d in dates]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x_dates, counts, color="#25f4ee", linewidth=0.8, alpha=0.6)
    ax.scatter(x_dates, counts, color="#fe2c55", s=16, zorder=5)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("New Followers", fontsize=12)
    ax.set_title("TikTok Followers Gained Over Time", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    if bin_by == "month":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    elif bin_by == "day":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path


def compare_followers(
    old_followers: List[Dict[str, str]],
    new_followers: List[Dict[str, str]],
) -> Tuple[List[str], List[str]]:
    old_names = {f["UserName"] for f in old_followers if f.get("UserName")}
    new_names = {f["UserName"] for f in new_followers if f.get("UserName")}

    unfollowed = sorted(old_names - new_names)
    gained = sorted(new_names - old_names)

    return unfollowed, gained


def _extract_date_from_filename(filepath: str) -> Optional[str]:
    match = re.search(r'(\d{10})', os.path.basename(filepath))
    if match:
        try:
            dt = datetime.fromtimestamp(int(match.group(1)))
            return dt.strftime("%Y-%m-%d")
        except (OSError, ValueError):
            pass
    return None


def generate_change_chart(
    old_followers: List[Dict[str, str]],
    new_followers: List[Dict[str, str]],
    export_date: str,
    history_path: str = "follower_change_history.json",
    output_path: str = "follower_change.png",
    reset: bool = False,
    overwrite: bool = False,
) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not overwrite:
        output_path = _resolve_output_path(output_path)

    try:
        plt.style.use("seaborn-v0_8")
    except OSError:
        plt.style.use("ggplot")

    unfollowed, gained = compare_followers(old_followers, new_followers)
    gained_count = len(gained)
    lost_count = len(unfollowed)

    history = []
    if not reset and os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)

    existing = next((h for h in history if h["date"] == export_date), None)
    if existing:
        existing["gained"] = gained_count
        existing["lost"] = lost_count
        action = "Updated"
    else:
        history.append({
            "date": export_date,
            "gained": gained_count,
            "lost": lost_count,
        })
        action = "Added"

    history.sort(key=lambda h: h["date"])

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    dates = [h["date"] for h in history]
    gained_vals = [h["gained"] for h in history]
    lost_vals = [-h["lost"] for h in history]

    x = range(len(dates))
    width = min(0.6, 0.10 * (len(dates) + 1))

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_gained = ax.bar(
        list(x), gained_vals, width,
        label="New followers", color="#2ecc71", alpha=0.85
    )
    bars_lost = ax.bar(
        list(x), lost_vals, width,
        label="No longer follow", color="#e74c3c", alpha=0.85
    )

    for bar in bars_gained:
        h = bar.get_height()
        if h != 0:
            ax.annotate(
                str(int(h)),
                xy=(bar.get_x() + bar.get_width() / 2, 0),
                xytext=(0, -3),
                textcoords="offset points",
                ha="center", va="top", fontsize=9
            )
    for bar in bars_lost:
        h = bar.get_height()
        if h != 0:
            ax.annotate(
                str(int(abs(h))),
                xy=(bar.get_x() + bar.get_width() / 2, 0),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=9
            )

    ax.axhline(0, color="black", linewidth=0.8)

    net_vals = [h["gained"] - h["lost"] for h in history]
    ax.plot(list(x), net_vals, color="#2c3e50", linewidth=1, alpha=0.5, linestyle="--")
    ax.scatter(list(x), net_vals, color="#2c3e50", s=30, zorder=5)

    for i, nv in enumerate(net_vals):
        ax.annotate(
            str(nv),
            xy=(i, nv),
            xytext=(10, 0),
            textcoords="offset points",
            ha="left", va="center",
            fontsize=9, color="#2c3e50", fontweight="bold"
        )

    y_min, y_max = ax.get_ylim()
    y_pad = (y_max - y_min) * 0.2
    ax.set_ylim(y_min - y_pad, y_max + y_pad)

    ax.set_xlabel("Export date", fontsize=12)
    ax.set_ylabel("Followers", fontsize=12)
    ax.set_title("Follower Change Between Snapshots", fontsize=14, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(dates, rotation=45, ha="right")
    ax.set_xlim(-1, len(dates))
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"  {action} {export_date}: +{gained_count} gained, -{lost_count} unfollowed")

    return output_path
