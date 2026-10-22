#!/usr/bin/env python3
"""List the ten nearest upcoming 4Geeks events, using title and start time only."""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

URL = "https://breathecode.herokuapp.com/v1/events/all?upcoming=true"
GENERIC_ERROR = "No se pudieron consultar los próximos eventos de 4Geeks."
INVALID_TOKEN = "El token no es válido."
EMPTY_MESSAGE = "No hay próximos eventos."


def fetch(curl, token):
    # Keep the protected credential out of argv and files; curl reads it on stdin.
    config = "header = \"Authorization: Token " + token.replace("\\", "\\\\").replace('"', '\\"') + "\"\n"
    result = subprocess.run(
        [curl, "--silent", "--max-redirs", "0", "--connect-timeout", "10",
         "--max-time", "30", "--config", "-", "--write-out", "\\n%{http_code}", URL],
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


def parse_start(value):
    if not isinstance(value, str) or not value.strip():
        return None, None
    text = value.strip()
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        # Naive timestamps are treated as UTC for consistent ordering.
        ordering = parsed.replace(tzinfo=dt.timezone.utc) if parsed.tzinfo is None else parsed.astimezone(dt.timezone.utc)
        display = parsed.strftime("%Y-%m-%d %H:%M")
        if parsed.tzinfo is not None:
            offset = parsed.strftime("%z")
            if offset:
                display += " " + (offset[:3] + ":" + offset[3:] if len(offset) == 5 else offset)
        return ordering, display
    except (ValueError, OverflowError):
        return None, None


def clean_title(value):
    if not isinstance(value, str) or not value.strip():
        return "Sin título"
    return " ".join(value.split())


def main():
    token = os.environ.get("BREATHE" + "CODE_TOKEN", "")
    if not token.startswith("oc-sent-v2.") or not token.endswith(".end"):
        print(GENERIC_ERROR)
        return 1
    curl = shutil.which("curl")
    if not curl:
        print(GENERIC_ERROR)
        return 1

    try:
        code, body = fetch(curl, token)
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
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        print(GENERIC_ERROR)
        return 1

    if isinstance(payload, dict):
        events = payload.get("results")
    else:
        events = payload
    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        print(GENERIC_ERROR)
        return 1
    if not events:
        print(EMPTY_MESSAGE)
        return 0

    prepared = []
    for event in events:
        ordering, display = parse_start(event.get("starting_at"))
        prepared.append((ordering is None, ordering or dt.datetime.max.replace(tzinfo=dt.timezone.utc),
                         clean_title(event.get("title")), display or "fecha no disponible"))
    prepared.sort(key=lambda item: (item[0], item[1]))
    print("\n".join(f"{title} — {when}" for _, _, title, when in prepared[:10]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print(GENERIC_ERROR)
        sys.exit(1)
