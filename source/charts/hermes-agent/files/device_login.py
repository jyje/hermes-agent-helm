#!/usr/bin/env python3
"""OAuth device-flow login for a Hermes agent (chart init container).

Provider-generic. Runs before the agent container. It:
  1. Skips immediately if a usable token already exists on the persistent
     volume (unless FORCE_RELOGIN=true), so restarts are fast.
  2. Otherwise runs the OAuth 2.0 Device Authorization Grant (RFC 8628) against
     the selected provider's authorization server.
  3. Delivers the verification URL + user code to the operator (Discord by
     default; always also printed to these init-container logs).
  4. Polls until authorized, then writes the token into $HERMES_HOME/.env under
     the provider's token env key, where Hermes reads it natively. Must run as
     the Hermes runtime uid so the agent can read the file.

Pure Python stdlib. Configured entirely via env vars (the chart fills these
from the selected `auth.deviceFlow.providers[<provider>]` profile):
  OAUTH_CLIENT_ID          OAuth client id for the device grant   (required)
  OAUTH_SCOPE              OAuth scope                            (default read:user)
  AUTH_HOST                device/token server host               (default github.com)
  TOKEN_ENV                .env key to store the token under      (required)
  VALIDATE_URL             optional GET endpoint to verify a token is still live
  NOTIFY                   discord | logs                         (default discord)
  DISCORD_BOT_TOKEN        required when NOTIFY=discord
  DISCORD_HOME_CHANNEL     required when NOTIFY=discord
  HERMES_HOME              default /opt/data
  LOGIN_TIMEOUT_SECONDS    default 870
  FORCE_RELOGIN            true to re-login even if a token exists
  CHOWN_UID / CHOWN_GID    chown the written .env to this uid/gid (the agent's
                           runtime uid) when running as root; -1 disables
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "").strip()
SCOPE = os.getenv("OAUTH_SCOPE", "read:user").strip()
AUTH_HOST = os.getenv("AUTH_HOST", "github.com").strip().rstrip("/")
TOKEN_ENV = os.getenv("TOKEN_ENV", "").strip()
VALIDATE_URL = os.getenv("VALIDATE_URL", "").strip()
NOTIFY = os.getenv("NOTIFY", "discord").strip().lower()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("DISCORD_HOME_CHANNEL", "").strip()
HERMES_HOME = Path(os.getenv("HERMES_HOME", "/opt/data"))
TIMEOUT = int(os.getenv("LOGIN_TIMEOUT_SECONDS", "870"))
FORCE_RELOGIN = os.getenv("FORCE_RELOGIN", "false").strip().lower() == "true"
CHOWN_UID = int(os.getenv("CHOWN_UID", "-1"))
CHOWN_GID = int(os.getenv("CHOWN_GID", "-1"))

DEVICE_CODE_URL = f"https://{AUTH_HOST}/login/device/code"
ACCESS_TOKEN_URL = f"https://{AUTH_HOST}/login/oauth/access_token"
DISCORD_API = "https://discord.com/api/v10"


def _post_form(url: str, fields: dict) -> dict:
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "hermes-device-login/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def discord_post(content: str) -> None:
    """Best-effort delivery of a message to the configured Discord channel."""
    if NOTIFY != "discord":
        return
    if not (BOT_TOKEN and CHANNEL_ID):
        print("  [discord] bot token / channel not set - skipping post")
        return
    body = json.dumps({"content": content}).encode()
    req = urllib.request.Request(
        f"{DISCORD_API}/channels/{CHANNEL_ID}/messages",
        data=body,
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "hermes-device-login/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"  [discord] posted message (HTTP {resp.status})")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        print(f"  [discord] post FAILED HTTP {exc.code}: {detail}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [discord] post FAILED: {exc}")


def read_env_token() -> str:
    env_path = HERMES_HOME / ".env"
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith(f"{TOKEN_ENV}="):
            return line.split("=", 1)[1].strip()
    return ""


def token_is_valid(token: str) -> bool:
    """Best-effort check that a token is still usable.

    With no VALIDATE_URL, a present token is assumed valid. Otherwise treats
    network/unknown errors as 'valid' so transient failures never block
    startup; only an explicit 401/403 forces a re-login.
    """
    if not token:
        return False
    if not VALIDATE_URL:
        return True
    req = urllib.request.Request(
        VALIDATE_URL,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "hermes-device-login/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return False
        return True
    except Exception:  # noqa: BLE001
        return True


def write_env_token(token: str) -> None:
    """Upsert TOKEN_ENV in $HERMES_HOME/.env, preserving other keys."""
    HERMES_HOME.mkdir(parents=True, exist_ok=True)
    env_path = HERMES_HOME / ".env"
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8", errors="replace").splitlines()
    out = [ln for ln in lines if not ln.strip().startswith(f"{TOKEN_ENV}=")]
    out.append(f"{TOKEN_ENV}={token}")
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    try:
        os.chmod(env_path, 0o600)
    except OSError:
        pass
    # When the init container runs as root (the robust default that can write
    # to any storage class), hand the file to the agent's runtime uid/gid so the
    # agent — which runs as that non-root uid — can read it.
    if CHOWN_UID >= 0 or CHOWN_GID >= 0:
        try:
            os.chown(env_path, CHOWN_UID, CHOWN_GID)
            print(f"  chowned {env_path} to {CHOWN_UID}:{CHOWN_GID}")
        except OSError as exc:
            print(f"  WARNING: could not chown {env_path}: {exc}")
    print(f"  wrote {TOKEN_ENV} to {env_path} (len={len(token)})")


def run_device_flow() -> int:
    if NOTIFY == "discord" and not (BOT_TOKEN and CHANNEL_ID):
        print("ERROR: NOTIFY=discord requires DISCORD_BOT_TOKEN and DISCORD_HOME_CHANNEL.")
        return 2

    print(f"Starting device flow (client={CLIENT_ID}, host={AUTH_HOST}) ...")
    dev = _post_form(DEVICE_CODE_URL, {"client_id": CLIENT_ID, "scope": SCOPE})
    device_code = dev.get("device_code")
    user_code = dev.get("user_code")
    verification_uri = dev.get("verification_uri", f"https://{AUTH_HOST}/login/device")
    interval = max(int(dev.get("interval", 5)), 1)
    expires_in = int(dev.get("expires_in", 900))
    if not device_code or not user_code:
        print(f"ERROR: device flow did not return a code: {dev}")
        return 1

    print(f"  user_code={user_code}  verify={verification_uri}  expires_in={expires_in}s")
    discord_post(
        f"{TOKEN_ENV} login required:\n"
        f"1. Open: {verification_uri}\n"
        f"2. Enter code: {user_code}\n"
        f"(valid ~{expires_in // 60} min; phone-friendly)"
    )

    print("  waiting for authorization ...")
    deadline = time.monotonic() + min(TIMEOUT, expires_in)
    token = ""
    while time.monotonic() < deadline:
        time.sleep(interval + 1)
        try:
            res = _post_form(
                ACCESS_TOKEN_URL,
                {
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  poll error (will retry): {exc}")
            continue

        if res.get("access_token"):
            token = res["access_token"]
            print(
                "  AUTHORIZED. token_prefix={} expires_in={} refresh_token={} scope={}".format(
                    token[:4],
                    res.get("expires_in", "(none -> long-lived)"),
                    "present" if res.get("refresh_token") else "absent",
                    res.get("scope", ""),
                )
            )
            break

        err = res.get("error", "")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval = int(res.get("interval", interval + 5))
            continue
        if err in ("expired_token", "access_denied"):
            print(f"  ERROR: {err}")
            discord_post(f"Login failed: {err}. The pod will retry.")
            return 1
        print(f"  poll returned error: {err or res}")

    if not token:
        print("  ERROR: timed out waiting for authorization")
        discord_post("Login timed out. The pod will retry.")
        return 1

    write_env_token(token)
    discord_post("Login complete. The agent is starting.")
    return 0


def main() -> int:
    if not CLIENT_ID or not TOKEN_ENV:
        print("ERROR: OAUTH_CLIENT_ID and TOKEN_ENV are required.")
        return 2

    existing = read_env_token()
    if existing and not FORCE_RELOGIN and token_is_valid(existing):
        print(f"Existing {TOKEN_ENV} is present and valid - skipping device flow.")
        return 0
    if existing and FORCE_RELOGIN:
        print("FORCE_RELOGIN=true - ignoring existing token.")
    elif existing:
        print("Existing token is missing/invalid - re-running device flow.")
    return run_device_flow()


if __name__ == "__main__":
    sys.exit(main())
