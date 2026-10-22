#!/usr/bin/env python3
"""Summarize approved and awaiting-review 4Geeks tasks by type."""
import collections
import datetime as dt
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
PAGE_SIZE = 100
MAX_PAGES = 10000
GENERIC_ERROR = "No se pudo consultar el estado de las revisiones de 4Geeks."
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
         "--max-time", "30", "--config", "-", "--write-out", "\\n%{http_code}", url],
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


def parse_delivered_at(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def summarize(rows, now=None):
    """Return safe output lines or None if a needed field is malformed."""
    approved = collections.Counter()
    waiting = collections.Counter()
    oldest = None
    undated_waiting = 0
    now = now or dt.datetime.now(dt.timezone.utc)
    for row in rows:
        if not isinstance(row, dict):
            return None
        status = row.get("task_status")
        revision = row.get("revision_status")
        task_type = row.get("task_type")
        if not all(isinstance(v, str) and v.strip() for v in (status, revision, task_type)):
            return None
        task_type = " ".join(task_type.split())
        if revision.strip().upper() == "APPROVED":
            approved[task_type] += 1
        if status.strip().upper() == "DONE" and revision.strip().upper() == "PENDING":
            waiting[task_type] += 1
            raw_delivered_at = row.get("delivered_at")
            if raw_delivered_at is None:
                undated_waiting += 1
                continue
            delivered_at = parse_delivered_at(raw_delivered_at)
            if delivered_at is None:
                return None
            if oldest is None or delivered_at < oldest:
                oldest = delivered_at

    lines = ["Tareas aprobadas por tipo:"]
    if approved:
        lines.extend(f"{kind}: {approved[kind]}" for kind in sorted(approved, key=str.casefold))
    else:
        lines.append("Ninguna")
    lines.append("Entregas esperando revisión por tipo:")
    if waiting:
        lines.extend(f"{kind}: {waiting[kind]}" for kind in sorted(waiting, key=str.casefold))
    else:
        lines.append("Ninguna")
    lines.append(f"Total esperando revisión: {sum(waiting.values())}")
    if oldest is None:
        lines.append("Antigüedad de la más antigua: no disponible (sin delivered_at)")
    else:
        days = max(0, (now - oldest).days)
        lines.append(f"Antigüedad de la más antigua con fecha disponible: {days} días")
    if undated_waiting:
        lines.append(f"Entregas esperando revisión sin delivered_at: {undated_waiting}")
    return lines


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
    rows = []
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
        rows.extend(page["results"])
        next_value = page.get("next")
        if next_value is None or next_value == "":
            break
        safe_url = next_url_is_safe(next_value, url)
        if not safe_url:
            print(GENERIC_ERROR)
            return 1
        url = safe_url
    else:
        print(GENERIC_ERROR)
        return 1

    lines = summarize(rows)
    if lines is None:
        print(GENERIC_ERROR)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print(GENERIC_ERROR)
        sys.exit(1)
