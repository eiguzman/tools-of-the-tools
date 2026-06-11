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
uv run tt-stats growth path/to/tiktok_data.json -o growth.png -s 2024-01-01
```
Saves a PNG line chart of followers gained over time (one dot per day by default). Use `-b day|week|month` to control the time grouping. Use `-s YYYY-MM-DD` to only include followers from that date onward. Add `--overwrite` to replace an existing file instead of creating a numbered copy.

### Compare two data files
```
uv run tt-stats compare older_data.json newer_data.json
```
Shows who unfollowed you and who started following you between the two snapshots.

### Generate a follower change chart
```
uv run tt-stats change-chart older_data.json newer_data.json -o change.png -d 2026-06-07
```
Saves a bar chart with green bars (new followers) above zero and red bars (unfollowers) below zero for each snapshot comparison. The x-axis shows the export date of the newer file.

The export date is auto-extracted from the newer filename if it contains a 10-digit Unix timestamp; otherwise pass `-d YYYY-MM-DD`. Each run adds a new pair of bars to the chart (or updates an existing date). The history is saved to `follower_change_history.json`.

Use `--reset` to clear the history and start a fresh chart. Use `--history <path>` to point to a different history file (e.g., per-account tracking). The history file is machine-generated — use `--reset` to restart rather than editing it manually. Add `--overwrite` to replace an existing PNG instead of creating a numbered copy.

Output files (PNG and history JSON) are written to the current working directory unless `-o` or `--history` specify an absolute path.
