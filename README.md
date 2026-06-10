# tt-stats

A CLI tool that analyzes your TikTok follower data locally — no data is uploaded anywhere. It tells you which of your followings don't follow you back, generates a follower growth chart, and can compare two data files to detect unfollowers and new followers over time.

## Usage

Install from GitHub:
```
uv add "git+https://github.com/eiguzman/tools-of-the-tools.git"
```

Then run any command with `uv run tt-stats <command>`.

### Find who doesn't follow you back
```
uv run tt-stats unfollow-back path/to/tiktok_data.json
```
Lists everyone you follow who does not follow you back.

### Generate a follower growth chart
```
uv run tt-stats growth path/to/tiktok_data.json -o growth.png -b month
```
Saves a PNG bar chart of followers gained over time. Use `-b day|week|month` to control the time grouping.

### Compare two data files
```
uv run tt-stats compare older_data.json newer_data.json
```
Shows who unfollowed you and who started following you between the two snapshots.
