from collections import Counter
from datetime import datetime
from typing import List, Dict, Tuple


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
) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

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
    ax.bar(x_dates, counts, width=0.8, color="#FE2C55", alpha=0.7)
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
