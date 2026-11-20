#!/usr/bin/env python3
"""Offline Vertex provider contract, run inside the chart-pinned Hermes image.

The container has no network. aimock and a token endpoint listen on its own
loopback, so nothing can fall through to Google Cloud. Hermes resolves the
Vertex runtime exactly as it does in a Pod (chart-rendered config.yaml, a
synthetic service-account key at the mounted path). The final request goes
through a strict transport that accepts one exact URL and forwards it to aimock.
Only the OpenAI client construction is test-owned.
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

AIMOCK_PORT, TOKEN_PORT = 4010, 4011
SYNTHETIC_TOKEN = "synthetic-vertex-token"
PROMPT, MARKER = "vertex-contract-ping", "VERTEX_CONTRACT_OK"

token_hits = []


class TokenHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
        token_hits.append(
            {"grant_type": form.get("grant_type", [""])[0], "has_assertion": bool(form.get("assertion"))}
        )
        body = json.dumps({"access_token": SYNTHETIC_TOKEN, "expires_in": 3600, "token_type": "Bearer"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def fail(message):
    print(f"CONTRACT FAIL: {message}", flush=True)
    sys.exit(1)


def start_servers():
    server = HTTPServer(("127.0.0.1", TOKEN_PORT), TokenHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    mock = subprocess.Popen(
        ["node", "/opt/aimock/dist/cli.js", "-p", str(AIMOCK_PORT), "-h", "127.0.0.1",
         "-f", "/contract/fixtures", "--strict", "--validate-on-load", "--log-level", "warn"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{AIMOCK_PORT}/__aimock/journal", timeout=1).read()
            return mock
        except Exception:
            if mock.poll() is not None:
                fail(f"aimock exited early: {mock.stderr.read().decode()[:500]}")
            time.sleep(0.5)
    fail("aimock did not become ready")


def main():
    import httpx
    import openai
    from hermes_cli.config import load_config
    from hermes_cli.runtime_provider import resolve_runtime_provider

    mock = start_servers()
    cfg = load_config()
    model = cfg["model"]["default"]
    project = cfg["vertex"]["project_id"]
    region = cfg["vertex"]["region"]
    if model != "google/gemini-3.8-flash":
        fail(f"chart config selects {model!r}, expected google/gemini-3.8-flash")

    runtime = resolve_runtime_provider(requested="vertex")
    host = "aiplatform.googleapis.com" if region == "global" else f"{region}-aiplatform.googleapis.com"
    expected_base = f"https://{host}/v1beta1/projects/{project}/locations/{region}/endpoints/openapi"
    if runtime["provider"] != "vertex" or runtime["base_url"] != expected_base:
        fail(f"runtime resolved {runtime['provider']} {runtime['base_url']}, expected vertex {expected_base}")
    if runtime["api_key"] != SYNTHETIC_TOKEN or len(token_hits) != 1:
        fail(f"token was not minted once from the service-account key (hits={token_hits})")
    print(f"ok: runtime provider=vertex base_url={runtime['base_url']}")
    print(f"ok: token minted from the synthetic key (grant={token_hits[0]['grant_type']})")

    class Strict(httpx.BaseTransport):
        """Accept one exact Vertex URL and bearer token, then forward the body to aimock."""

        def __init__(self, base):
            self.url = f"{base}/chat/completions"
            self.inner = httpx.HTTPTransport()

        def handle_request(self, request):
            if str(request.url) != self.url:
                raise RuntimeError(f"unexpected URL {request.url}, expected {self.url}")
            if request.headers.get("authorization") != f"Bearer {SYNTHETIC_TOKEN}":
                raise RuntimeError("unexpected Authorization header")
            forwarded = httpx.Request(
                "POST", f"http://127.0.0.1:{AIMOCK_PORT}/v1/chat/completions",
                headers={"content-type": "application/json"}, content=request.content,
            )
            return self.inner.handle_request(forwarded)

    def ask(base_url, request_model):
        client = openai.OpenAI(
            base_url=base_url, api_key=runtime["api_key"], max_retries=0,
            http_client=httpx.Client(transport=Strict(runtime["base_url"])),
        )
        return client.chat.completions.create(
            model=request_model, messages=[{"role": "user", "content": PROMPT}]
        ).choices[0].message.content

    reply = ask(runtime["base_url"], model)
    if reply != MARKER:
        fail(f"reply {reply!r}, expected {MARKER!r}")
    print(f"ok: reply is the fixed marker {reply}")

    for label, base, req_model in (
        ("wrong route", runtime["base_url"].replace("/locations/", "/regions/"), model),
        ("wrong model", runtime["base_url"], "google/gemini-2.5-flash"),
    ):
        try:
            ask(base, req_model)
        except Exception as exc:
            print(f"ok: {label} is rejected ({type(exc).__name__})")
        else:
            fail(f"{label} was accepted")

    journal = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{AIMOCK_PORT}/__aimock/journal").read())
    entries = journal if isinstance(journal, list) else journal.get("entries", journal.get("journal", []))
    matched = [e for e in entries if PROMPT in json.dumps(e) and model in json.dumps(e)]
    if len(matched) != 1:
        fail(f"expected exactly one journaled request for {model}, saw {len(matched)} of {len(entries)}")
    print(f"ok: aimock journal holds {len(entries)} request(s); one matches {model}")
    mock.terminate()
    print("CONTRACT PASS")


if __name__ == "__main__":
    main()
