"""Small client for the SolMarrow REST API (https://app.solmarrow.com/api/v1).

Every call goes to this one host with the person's personal API key. Nothing is stored or logged by the plugin.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

import requests

BASE_URL = "https://app.solmarrow.com/api/v1"
TIMEOUT = 30
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


class SolMarrowError(Exception):
    """An error with a message that is safe and useful to show to the person."""


def api_key_from(credentials: dict[str, Any]) -> str:
    key = str(credentials.get("api_key") or "").strip()
    if not key:
        raise SolMarrowError("Add your SolMarrow API key (Settings → API keys in SolMarrow).")
    return key


def request(api_key: str, method: str, path: str, *, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    send_headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json", "User-Agent": "solmarrow-dify-plugin/1.0"}
    if body is not None:
        send_headers["Content-Type"] = "application/json"
    if headers:
        send_headers.update(headers)
    clean = {k: v for k, v in (params or {}).items() if v not in (None, "")}
    try:
        res = requests.request(method, BASE_URL + path, params=clean or None, json=body, headers=send_headers, timeout=TIMEOUT)
    except requests.RequestException:
        raise SolMarrowError("Could not reach SolMarrow. Try again in a moment.") from None
    try:
        data = res.json()
    except ValueError:
        data = {}
    if res.status_code == 401:
        raise SolMarrowError("SolMarrow did not accept the API key. It may be wrong or deleted; create a new one in Settings → API keys.")
    if res.status_code == 429:
        raise SolMarrowError("SolMarrow says too many requests or the daily post limit was reached. Wait a moment and try again.")
    if not res.ok:
        message = ""
        if isinstance(data, dict):
            err = data.get("error")
            message = err.get("message", "") if isinstance(err, dict) else str(err or "")
        raise SolMarrowError(message or f"SolMarrow answered with an error ({res.status_code}).")
    return data if isinstance(data, dict) else {}


def workspace_id(api_key: str, given: Any) -> str:
    """The workspace to use: the one given, or the only workspace this key can reach."""
    given = str(given or "").strip()
    if given:
        if not UUID_RE.match(given):
            raise SolMarrowError("workspace_id must be an id from List workspaces.")
        return given
    items = request(api_key, "GET", "/workspaces").get("workspaces") or []
    if len(items) == 1:
        return str(items[0]["id"])
    if not items:
        raise SolMarrowError("This API key has no workspace.")
    raise SolMarrowError("This key reaches several workspaces. Pass workspace_id (see List workspaces).")


def id_list(value: Any, name: str, limit: int) -> list[str]:
    """Ids typed as a comma-, space- or newline-separated list (or already a list)."""
    if value in (None, ""):
        return []
    parts = value if isinstance(value, list) else re.split(r"[,\s]+", str(value))
    ids = [str(p).strip() for p in parts if str(p).strip()]
    for item in ids:
        if not UUID_RE.match(item):
            raise SolMarrowError(f"{name} must be ids separated by commas; '{item[:40]}' is not an id.")
    if len(ids) > limit:
        raise SolMarrowError(f"{name} takes at most {limit} ids.")
    return list(dict.fromkeys(ids))


def json_object(value: Any, name: str) -> dict[str, Any] | None:
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except ValueError:
        raise SolMarrowError(f"{name} must be a JSON object, for example {{\"account-id\": \"text\"}}.") from None
    if not isinstance(parsed, dict):
        raise SolMarrowError(f"{name} must be a JSON object.")
    return parsed


def iso_time(value: Any, name: str) -> str | None:
    value = str(value or "").strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise SolMarrowError(f"{name} must be ISO 8601 with an offset, like 2026-11-12T09:00:00+06:00.") from None
    if parsed.tzinfo is None:
        raise SolMarrowError(f"{name} needs a time zone offset, like 2026-11-12T09:00:00+06:00.")
    return value
