import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen

import httpx

from agent import vertex_adapter
from hermes_cli.main import main


EXPECTED_URL = (
    "https://aiplatform.googleapis.com/v1beta1/projects/vertex-contract-fixture"
    "/locations/global/endpoints/openapi/chat/completions"
)
EXPECTED_MODEL = "google/gemini-3.8-flash"
TOKEN = "synthetic-vertex-contract-token"


class SyntheticCredentials:
    token = TOKEN
    expired = False
    expiry = None


def load_fixture_credentials(path, snapshot):
    if path != "/var/run/secrets/vertex/sa.json" or snapshot is None:
        raise AssertionError("Hermes did not read the expected credential file")
    if json.loads(snapshot) != {"project_id": "synthetic-credential-project"}:
        raise AssertionError("Unexpected credential fixture")
    return SyntheticCredentials(), "synthetic-credential-project"


def verify_request(method, url, authorization, payload):
    if method != "POST" or url != EXPECTED_URL:
        raise AssertionError("Unexpected Vertex inference route")
    if authorization != f"Bearer {TOKEN}":
        raise AssertionError("Unexpected Vertex authorization header")
    if payload.get("model") != EXPECTED_MODEL:
        raise AssertionError("Unexpected Vertex model")


def negative_controls():
    for url, model, expected in (
        (EXPECTED_URL.replace("global", "wrong-region"), EXPECTED_MODEL, "route"),
        (EXPECTED_URL, "google/wrong-model", "model"),
    ):
        try:
            verify_request("POST", url, f"Bearer {TOKEN}", {"model": model})
        except AssertionError as exc:
            if expected not in str(exc):
                raise
        else:
            raise AssertionError(f"Incorrect {expected} passed validation")
    print("Wrong route and model rejected", file=sys.stderr)


def run():
    hits = 0
    for attempt in range(30):
        try:
            with urlopen("http://aimock:4010/health", timeout=1):
                break
        except OSError:
            if attempt == 29:
                raise
            time.sleep(1)

    def forward(_transport, request):
        nonlocal hits
        body = request.read()
        verify_request(
            request.method, str(request.url), request.headers.get("authorization"), json.loads(body)
        )
        with urlopen(
            Request(
                "http://aimock:4010/v1/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
            ),
            timeout=10,
        ) as response:
            hits += 1
            return httpx.Response(
                response.status,
                headers={"Content-Type": response.headers["Content-Type"]},
                content=response.read(),
            )

    negative_controls()
    sys.argv = ["hermes", "chat", "--quiet", "-q", "Run the Vertex contract smoke test."]
    with (
        patch.object(vertex_adapter, "_ensure_google_auth", return_value=True),
        patch.object(vertex_adapter, "_load_credentials", side_effect=load_fixture_credentials),
        patch.object(httpx.HTTPTransport, "handle_request", forward),
    ):
        try:
            main()
        except SystemExit as exc:
            if exc.code not in (None, 0):
                raise
    if hits != 1:
        raise AssertionError(f"Expected one matched inference request; observed {hits}")
    print("Verified one Vertex request reaching aimock", file=sys.stderr)


if __name__ == "__main__":
    if Path(os.environ["VERTEX_CREDENTIALS_PATH"]).is_file():
        run()
    else:
        raise SystemExit("Missing synthetic Vertex credential file")
