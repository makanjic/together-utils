#!/usr/bin/env python3
"""
Check which Together API keys are usable via the OpenAI-compatible API.

Usage:
    python check_together_keys.py --input keys.txt --output valid_keys.txt

`keys.txt` should contain one API key per line.
"""

import argparse
import json
import sys
from typing import List

import requests

TOGETHER_BASE_URL = "https://api.together.xyz/v1"  # OpenAI-compatible base URL


def load_keys(path: str) -> List[str]:
    keys = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            k = line.strip()
            if k and not k.startswith("#"):
                keys.append(k)
    return keys


def is_key_usable(api_key: str, timeout: int = 10) -> bool:
    """
    Heuristically check if a Together API key is usable.

    We call GET /models (OpenAI-compatible list models endpoint).
    - 200 => key valid & usable
    - 401/403 => invalid/unauthorized
    - 402 or error message mentioning "insufficient" => no funds / unusable
    - 429 => treat as usable (key is valid but rate-limited)
    - anything else => log and treat as unusable by default
    """
    url = f"{TOGETHER_BASE_URL}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        print(f"[ERROR] Network error for key {api_key[:8]}...: {e}", file=sys.stderr)
        return False

    status = resp.status_code

    # Try to parse error body if any
    msg = ""
    try:
        data = resp.json()
        if isinstance(data, dict):
            err = data.get("error") or {}
            if isinstance(err, dict):
                msg = (err.get("message") or "") + " " + (err.get("type") or "")
            else:
                msg = json.dumps(data)[:200]
    except Exception:
        msg = resp.text[:200] if resp.text else ""

    msg_lower = (msg or "").lower()

    if status == 200:
        # Key works, we got the models list
        return True

    if status in (401, 403):
        # Invalid or unauthorized key
        print(f"[INFO] Key {api_key[:8]}... unauthorized ({status}).", file=sys.stderr)
        return False

    if status == 402 or "insufficient" in msg_lower or "out of credits" in msg_lower:
        # Key exists but has no usable balance
        print(
            f"[INFO] Key {api_key[:8]}... appears to have insufficient balance.",
            file=sys.stderr,
        )
        return False

    if status == 429:
        # Rate-limited but key is valid; mark as usable
        print(
            f"[INFO] Key {api_key[:8]}... is rate-limited (429) but valid. Treating as usable.",
            file=sys.stderr,
        )
        return True

    # Any other unexpected status
    print(
        f"[WARN] Key {api_key[:8]}... unexpected status {status}, body='{msg}'. "
        "Treating as unusable.",
        file=sys.stderr,
    )
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Check availability of Together API keys (OpenAI-compatible)."
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to file with Together API keys."
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to write usable keys (one per line).",
    )
    args = parser.parse_args()

    keys = load_keys(args.input)
    if not keys:
        print(f"No keys found in {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(keys)} keys from {args.input}", file=sys.stderr)

    usable_keys: List[str] = []

    for k in keys:
        short = k[:8] + "..."
        print(f"[CHECK] Testing key {short}", file=sys.stderr)
        if is_key_usable(k):
            print(f"[OK] Key {short} is usable.", file=sys.stderr)
            usable_keys.append(k)
        else:
            print(f"[BAD] Key {short} is NOT usable.", file=sys.stderr)

    # Write usable keys out
    with open(args.output, "w", encoding="utf-8") as f:
        for k in usable_keys:
            f.write(k + "\n")

    print(
        f"Done. {len(usable_keys)} / {len(keys)} keys are usable. "
        f"Written to {args.output}"
    )


if __name__ == "__main__":
    main()
