#!/usr/bin/env python3
"""Read all of the current user's 4Geeks project assignments, output minimized fields."""
import collections
import json
import os
import shutil
import subprocess
import sys
import urllib.parse

BASE_URL = "https://breathecode.herokuapp.com/v1/assignment/user/me/task"
PAGE_SIZE = 100
MAX_PAGES = 10000
GENERIC_ERROR = "No se pudo consultar los proyectos de 4Geeks."
INVALID_TOKEN = "El token no es válido."


def clean_text(value):
    if not isinstance(value, str):
        return None
    value = " ".join(value.split())
    return value if value else None


def get_page(curl, token, limit, offset):
    query = urllib.parse.urlencode({"task_type": "PROJECT", "limit": limit, "offset": offset})
    url = BASE_URL + "?" + query
    # Send auth through stdin via curl config; never put credential/sentinel in argv.
    config = "header = \"Authorization: Token " + token.replace("\\", "\\\\").replace('"', '\\"') + "\"\n"
    result = subprocess.run(
        [curl, "--silent", "--max-redirs", "0", "--connect-timeout", "10",
         "--max-time", "30", "--config", "-", "--write-out", "\n%{http_code}", url],
        input=config.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        timeout=35, check=False, env=os.environ.copy(),
    )
    if result.returncode != 0:
        return None, None
    try:
        body, status_bytes = result.stdout.rsplit(b"\n", 1)
        status = status_bytes.decode("ascii")
    except (ValueError, UnicodeDecodeError):
        return None, None
    return status, body


def main():
    token = os.environ.get("BREATHECODE_TOKEN", "")
    if not token.startswith("oc-sent-v2.") or not token.endswith(".end"):
        print(GENERIC_ERROR)
        return 1
    curl = shutil.which("curl")
    if not curl:
        print(GENERIC_ERROR)
        return 1

    projects = []
    offset = 0
    expected_count = None
    seen_offsets = set()
    for _ in range(MAX_PAGES):
        if offset in seen_offsets:
            print(GENERIC_ERROR)
            return 1
        seen_offsets.add(offset)
        try:
            status, body = get_page(curl, token, PAGE_SIZE, offset)
        except (OSError, subprocess.TimeoutExpired):
            print(GENERIC_ERROR)
            return 1
        if status == "401":
            print(INVALID_TOKEN)
            return 0
        if status != "200" or body is None:
            print(GENERIC_ERROR)
            return 1
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            print(GENERIC_ERROR)
            return 1
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            print(GENERIC_ERROR)
            return 1
        count = payload.get("count")
        if not isinstance(count, int) or count < 0:
            print(GENERIC_ERROR)
            return 1
        if expected_count is None:
            expected_count = count
        elif count != expected_count:
            # Dataset changed during pagination: avoid claiming an incomplete list.
            print(GENERIC_ERROR)
            return 1

        rows = payload["results"]
        if len(rows) > PAGE_SIZE or (not rows and offset < expected_count):
            print(GENERIC_ERROR)
            return 1
        for row in rows:
            if not isinstance(row, dict):
                print(GENERIC_ERROR)
                return 1
            title = clean_text(row.get("title"))
            state = clean_text(row.get("task_status"))
            if title is None or state is None:
                print(GENERIC_ERROR)
                return 1
            projects.append((title, state))

        offset += len(rows)
        if offset >= expected_count:
            break
        if not rows:
            print(GENERIC_ERROR)
            return 1
    else:
        print(GENERIC_ERROR)
        return 1

    if expected_count is None or len(projects) != expected_count:
        print(GENERIC_ERROR)
        return 1

    counts = collections.Counter(state for _, state in projects)
    lines = [f"{title} — {state}" for title, state in projects]
    lines.append("Conteo por estado:")
    for state in sorted(counts):
        lines.append(f"{state}: {counts[state]}")
    if not projects:
        lines.insert(0, "No hay proyectos.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail closed without exposing response data or credential-related diagnostics.
        print(GENERIC_ERROR)
        sys.exit(1)
