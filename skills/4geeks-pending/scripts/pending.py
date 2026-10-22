#!/usr/bin/env python3
"""List all pending 4Geeks tasks using only title and task_type."""
import collections
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

INITIAL_URL = "https://breathecode.herokuapp.com/v1/assignment/user/me/task?task_status=PENDING&limit=100&offset=0"
EXPECTED_HOST = "breathecode.herokuapp.com"
EXPECTED_PATH = "/v1/assignment/user/me/task"
PAGE_SIZE = 100
MAX_PAGES = 10000
GENERIC_ERROR = "No se pudo consultar el trabajo pendiente de 4Geeks."
INVALID_TOKEN = "El token no es válido."
TYPE_LABELS = {
    "PROJECT": "Proyecto",
    "EXERCISE": "Ejercicio",
    "LESSON": "Lección",
    "QUIZ": "Cuestionario",
}


def clean_text(value):
    if not isinstance(value, str):
        return None
    value = " ".join(value.split())
    return value if value else None


def safe_next_url(value):
    if not isinstance(value, str) or not value:
        return None
    absolute = urllib.parse.urljoin(INITIAL_URL, value)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST or parsed.port not in (None, 443):
        return False
    if parsed.path != EXPECTED_PATH or parsed.username is not None or parsed.password is not None:
        return False
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if query.get("task_status") != ["PENDING"]:
        return False
    try:
        limit = int(query.get("limit", [str(PAGE_SIZE)])[0])
        offset = int(query.get("offset", [""])[0])
    except (TypeError, ValueError):
        return False
    if limit < 1 or limit > PAGE_SIZE or offset < 0:
        return False
    return absolute


def fetch(curl, token, url):
    # Pass header config on stdin, keeping credential/sentinel out of process argv.
    config = "header = \"Authorization: Token " + token.replace("\\", "\\\\").replace('"', '\\"') + "\"\n"
    result = subprocess.run(
        [curl, "--silent", "--max-redirs", "0", "--connect-timeout", "10", "--max-time", "30",
         "--config", "-", "--write-out", "\n%{http_code}", url],
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


def display_type(value):
    normalized = value.strip().upper()
    if normalized in TYPE_LABELS:
        return TYPE_LABELS[normalized]
    # Map common singular/plural variants conservatively.
    aliases = {"LESSONS": "LESSON", "EXERCISES": "EXERCISE", "PROJECTS": "PROJECT", "QUIZZES": "QUIZ", "QUIZES": "QUIZ"}
    if aliases.get(normalized) in TYPE_LABELS:
        return TYPE_LABELS[aliases[normalized]]
    return "Otros (" + clean_text(value) + ")"


def main():
    token = os.environ.get("BREATHECODE_TOKEN", "")
    if not token.startswith("oc-sent-v2.") or not token.endswith(".end"):
        print(GENERIC_ERROR)
        return 1
    curl = shutil.which("curl")
    if not curl:
        print(GENERIC_ERROR)
        return 1

    url = INITIAL_URL
    seen_urls = set()
    groups = collections.OrderedDict((label, []) for label in ("Proyecto", "Ejercicio", "Lección", "Cuestionario", "Otros"))
    total = 0
    for _ in range(MAX_PAGES):
        if url in seen_urls:
            print(GENERIC_ERROR)
            return 1
        seen_urls.add(url)
        try:
            status, body = fetch(curl, token, url)
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
            page = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            print(GENERIC_ERROR)
            return 1
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            print(GENERIC_ERROR)
            return 1
        for row in page["results"]:
            if not isinstance(row, dict) or row.get("task_status") != "PENDING":
                print(GENERIC_ERROR)
                return 1
            title = clean_text(row.get("title"))
            task_type = clean_text(row.get("task_type"))
            if title is None or task_type is None:
                print(GENERIC_ERROR)
                return 1
            label = display_type(task_type)
            group = label if label in groups else "Otros"
            groups[group].append((title, label))
            total += 1

        next_value = page.get("next")
        if next_value is None or next_value == "":
            break
        next_url = safe_next_url(next_value)
        if not next_url:
            print(GENERIC_ERROR)
            return 1
        url = next_url
    else:
        print(GENERIC_ERROR)
        return 1

    lines = []
    group_order = ["Proyecto", "Ejercicio", "Lección", "Cuestionario", "Otros"]
    for group in group_order:
        items = groups[group]
        if not items:
            continue
        lines.append(group + ":")
        for title, label in items:
            lines.append(f"{title} — {label}")
        lines.append(f"Conteo {group.lower()}: {len(items)}")
    lines.append(f"Total: {total}")
    if total == 0:
        lines.insert(0, "No hay tareas pendientes.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print(GENERIC_ERROR)
        sys.exit(1)
