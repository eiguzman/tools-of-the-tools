import json
import random
import os
import sys
import subprocess
from datetime import datetime, timedelta

random.seed(42)

REPO = "/home/eiguzman/Desktop/DSC190/tools-of-the-tools"
DATA_DIR = f"{REPO}/tests/test_data"
RESULTS_DIR = f"{REPO}/tests/test_results"

ALL_USERS = [f"user_{i}" for i in range(1, 301)]
BASE_DATE = datetime(2026, 4, 1, 0, 0, 0)

def make_data_file(followers, following, idx):
    fans = []
    for i, u in enumerate(followers):
        d = BASE_DATE + timedelta(hours=i * 7)
        fans.append({"Date": d.strftime("%Y-%m-%d %H:%M:%S"), "UserName": u})

    flist = []
    for i, u in enumerate(following):
        d = BASE_DATE + timedelta(hours=i * 7)
        flist.append({"Date": d.strftime("%Y-%m-%d %H:%M:%S"), "UserName": u})

    data = {
        "Profile And Settings": {
            "Follower": {"App": 1, "IsFastLane": True, "FansList": fans},
            "Following": {"App": 1, "IsFastLane": True, "Following": flist},
        }
    }
    path = f"{DATA_DIR}/tiktok_data_{idx:02d}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def run(cmd, outfile=None):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    output = result.stdout + result.stderr
    if outfile:
        with open(outfile, "w") as f:
            f.write(output)
    print(output, end="")
    return output

follower_pool = list(ALL_USERS[:100])
following_pool = list(ALL_USERS[:98]) + ["user_300"]
used = set(follower_pool) | set(following_pool)
unused = [u for u in ALL_USERS if u not in used]

nfb_prev = []

for i in range(1, 11):
    print(f"\n{'='*60}")
    print(f"STEP {i}: generating tiktok_data_{i:02d}.json")
    print(f"  followers={len(follower_pool)}, following={len(following_pool)}")

    path = make_data_file(follower_pool, following_pool, i)

    export_date = (datetime(2026, 5, 1) + timedelta(days=(i - 1) * 4)).strftime("%Y-%m-%d")
    prev_path = f"{DATA_DIR}/tiktok_data_{i-1:02d}.json" if i > 1 else None

    # --- unfollow-back ---
    uf_file = f"{RESULTS_DIR}/unfollow_back_{i:02d}.txt"
    run(["uv", "run", "tt-stats", "unfollow-back", path], outfile=uf_file)

    # --- growth chart ---
    growth_out = f"{RESULTS_DIR}/follower_growth_{i:02d}.png"
    run(["uv", "run", "tt-stats", "growth", path, "-o", growth_out])

    # --- compare ---
    if prev_path:
        cmp_file = f"{RESULTS_DIR}/compare_{i-1:02d}_to_{i:02d}.txt"
        run(["uv", "run", "tt-stats", "compare", prev_path, path], outfile=cmp_file)

    # --- change-chart ---
    if prev_path:
        run([
            "uv", "run", "tt-stats", "change-chart",
            prev_path, path,
            "-d", export_date,
            "-o", f"{RESULTS_DIR}/follower_change.png",
            "--history", f"{RESULTS_DIR}/follower_change_history.json",
            "--overwrite",
        ])

    # --- update pools for next iteration ---
    follower_set = set(follower_pool)
    following_set = set(following_pool)
    nfb = sorted(following_set - follower_set)
    print(f"  not following back: {nfb}")

    gained = random.randint(1, 10)
    lost = random.randint(1, 5)

    chosen_new = random.sample(unused, min(gained, len(unused)))
    chosen_lost = random.sample(follower_pool, min(lost, len(follower_pool)))

    for u in chosen_new:
        follower_pool.append(u)
        unused.remove(u)

    for u in chosen_lost:
        follower_pool.remove(u)

    for u in nfb:
        following_pool.remove(u)

    print(f"  next: +{len(chosen_new)} gained, -{len(chosen_lost)} lost from followers")
    print(f"  next: -{len(nfb)} unfollow-back removed from following")

print(f"\n{'='*60}")
print("DONE. Generated files:")
for f in sorted(os.listdir(RESULTS_DIR)):
    print(f"  {f}")
