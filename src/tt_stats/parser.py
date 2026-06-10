import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Tuple


def parse_tiktok_file(filepath: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    suffix = path.suffix.lower()
    if suffix == ".zip":
        return _parse_zip(path)
    elif suffix == ".json":
        return _parse_json(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .json or .zip")


def _parse_json(path: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _extract_from_data(data)


def _parse_zip(path: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    with zipfile.ZipFile(path, "r") as zf:
        json_files = [n for n in zf.namelist() if n.lower().endswith(".json")]
        if not json_files:
            raise ValueError("No JSON file found inside the ZIP archive.")
        with zf.open(json_files[0]) as f:
            data = json.load(f)
    return _extract_from_data(data)


def _extract_from_data(data: Dict[str, Any]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    profile = data.get("Profile And Settings", {})
    if not profile:
        raise ValueError("Invalid TikTok data: missing 'Profile And Settings'")

    follower_section = profile.get("Follower", {})
    fans_list = follower_section.get("FansList", [])

    following_section = profile.get("Following", {})
    following_list = following_section.get("Following", [])

    return fans_list, following_list
