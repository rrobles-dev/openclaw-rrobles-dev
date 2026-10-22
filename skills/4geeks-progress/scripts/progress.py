#!/usr/bin/env python3
"""Summarize all 4Geeks assignments using status and type only."""
import collections
import json
import os
import shutil
import subprocess
import sys
import urllib.parse

BASE_URL = "https://breathecode.herokuapp.com/v1/assignment/user/me/task"
INITIAL_URL = BASE_URL + "?limit=100&offset=0"
EXPECTED_HOST = "breathecode.herokuapp.com"
EXPECTED_PATH = "/v1/assignment/user/me/task"
MAX_PAGES = 10000
GENERIC_ERROR = "No se pudo consultar el avance de 4Geeks."
INVALID_TOKEN = "El token no es válido."


def next_url_is_safe(value, current_url):
    if not isinstance(value, str) or not value:
        return None
    absolute = urllib.parse.urljoin(current_url, value)
    parsed = urllib.parse.urlsplit(absolute)
    if (parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST or
            parsed.port not in (None, 443) or parsed.path != EXPECTED_PATH or
            parsed.username is not None or parsed.password is not None):
        return False
    return absolute


def fetch(curl, token, url):
    # Credential remains in process stdin rather than argv or a file.
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
        body, code = result.stdout.rsplit(b"\n", 1)
        return code.decode("ascii"), body
    except (ValueError, UnicodeDecodeError):
        return None, None


def main():
    token = os.environ.get("BREATHE" + "CODE_TOKEN", "")
    if not token.startswith("oc-sent-v2.") or not token.endswith(".end"):
        print(GENERIC_ERROR)
        return 1
    curl = shutil.which("curl")
    if not curl:
        print(GENERIC_ERROR)
        return 1

    url = INITIAL_URL
    seen = set()
    statuses = collections.Counter()
    by_type = collections.defaultdict(collections.Counter)
    total = 0

    for _ in range(MAX_PAGES):
        if url in seen:
            print(GENERIC_ERROR)
            return 1
        seen.add(url)
        try:
            code, body = fetch(curl, token, url)
        except (OSError, subprocess.TimeoutExpired):
            print(GENERIC_ERROR)
            return 1
        if code == "401":
            print(INVALID_TOKEN)
            return 0
        if code != "200" or body is None:
            print(GENERIC_ERROR)
            return 1
        try:
            page = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            print(GENERIC_ERROR)
            return 1
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            print(GENERIC_ERROR)
            return 1
        for row in page["results"]:
            if not isinstance(row, dict):
                print(GENERIC_ERROR)
                return 1
            status = row.get("task_status")
            task_type = row.get("task_type")
            if not isinstance(status, str) or not status.strip() or not isinstance(task_type, str) or not task_type.strip():
                print(GENERIC_ERROR)
                return 1
            status = " ".join(status.split())
            task_type = " ".join(task_type.split())
            statuses[status] += 1
            by_type[task_type][status] += 1
            total += 1

        nxt = page.get("next")
        if nxt is None or nxt == "":
            break
        safe_url = next_url_is_safe(nxt, url)
        if not safe_url:
            print(GENERIC_ERROR)
            return 1
        url = safe_url
    else:
        print(GENERIC_ERROR)
        return 1

    lines = [f"Total de tareas: {total}", "Por estado:"]
    for status in sorted(statuses):
        pct = statuses[status] * 100 / total if total else 0.0
        lines.append(f"{status}: {statuses[status]} ({pct:.1f}%)")
    lines.append("Por tipo:")
    for task_type in sorted(by_type, key=str.casefold):
        counts = by_type[task_type]
        type_total = sum(counts.values())
        completed = sum(count for status, count in counts.items() if status.upper() == "DONE")
        lines.append(f"{task_type}: {type_total} tareas, {completed} completadas")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print(GENERIC_ERROR)
        sys.exit(1)
