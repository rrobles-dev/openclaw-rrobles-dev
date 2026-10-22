#!/usr/bin/env python3
"""Fetch and minimize the authenticated 4Geeks self-profile response."""
import json
import os
import shutil
import subprocess
import sys

URL = "https://breathecode.herokuapp.com/v1/admissions/user/me"
GENERIC_ERROR = "No se pudo consultar el perfil de 4Geeks."


def clean_text(value):
    if not isinstance(value, str):
        return None
    # Keep each requested value on exactly one output line.
    value = " ".join(value.split())
    return value if value else None


def profile_lines(payload):
    """Return only the explicitly permitted profile fields, or None if malformed."""
    if not isinstance(payload, dict):
        return None

    first = clean_text(payload.get("first_name"))
    last = clean_text(payload.get("last_name"))
    if not first or not last:
        return None
    name = first + " " + last

    roles = payload.get("roles")
    academy = None
    if isinstance(roles, list) and roles and isinstance(roles[0], dict):
        academy_obj = roles[0].get("academy")
        if isinstance(academy_obj, dict):
            academy = clean_text(academy_obj.get("name"))
    if not academy:
        return None

    active_names = []
    cohort_list = payload.get("cohorts")
    if isinstance(cohort_list, list):
        for entry in cohort_list:
            if not isinstance(entry, dict) or entry.get("educational_status") != "ACTIVE":
                continue
            cohort_obj = entry.get("cohort")
            if isinstance(cohort_obj, dict):
                cohort_name = clean_text(cohort_obj.get("name"))
                if cohort_name:
                    active_names.append(cohort_name)

    lines = ["Token: válido", "Nombre: " + name, "Academia: " + academy]
    if active_names:
        lines.extend("Cohorte activa: " + cohort_name for cohort_name in active_names)
    else:
        lines.append("Cohorte activa: ninguna")
    return lines


def main():
    token = os.environ.get("BREATHECODE_TOKEN", "")
    # A protected store secret must arrive as an opaque sentinel, never plaintext.
    if not token.startswith("oc-sent-v2.") or not token.endswith(".end"):
        print(GENERIC_ERROR)
        return 1
    curl = shutil.which("curl")
    if not curl:
        print(GENERIC_ERROR)
        return 1
    try:
        result = subprocess.run(
            [curl, "--silent", "--show-error", "--max-redirs", "0", "--connect-timeout", "10",
             "--max-time", "25", "--header", "Authorization: Token " + token,
             "--write-out", "\n%{http_code}", URL],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=30, check=False, env=os.environ.copy(),
        )
    except (OSError, subprocess.TimeoutExpired):
        print(GENERIC_ERROR)
        return 1
    if result.returncode != 0:
        print(GENERIC_ERROR)
        return 1
    try:
        body, status_bytes = result.stdout.rsplit(b"\n", 1)
        status = status_bytes.decode("ascii")
    except (ValueError, UnicodeDecodeError):
        print(GENERIC_ERROR)
        return 1
    if status == "401":
        print("El token no es válido.")
        return 0
    if status != "200":
        print(GENERIC_ERROR)
        return 1
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        print(GENERIC_ERROR)
        return 1
    lines = profile_lines(payload)
    if lines is None:
        print(GENERIC_ERROR)
        return 1

    # Output allowlist only; never emit raw API data or unexpected fields.
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
