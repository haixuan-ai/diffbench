"""Nexus entrant adapters (hosted-API only).

The Nexus engine source is NOT part of this repository. Nexus participates only through
the hosted HTTP API (POST /api/public/diffbench/run), which returns state trajectories
plus a server-side attestation. Scoring is done locally by the public scorer (diffbench/truth.py).
Set DIFFBENCH_NEXUS_URL (and optionally DIFFBENCH_TOKEN).
"""
from __future__ import annotations
import json, os, time, urllib.error, urllib.request
from .base import Adapter


class _NexusHttp(Adapter):
    entrant = ""
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base = (base_url or os.environ.get("DIFFBENCH_NEXUS_URL", "")).rstrip("/"); self.token = token or os.environ.get("DIFFBENCH_TOKEN", "")
    def version(self):
        try: return json.loads(urllib.request.urlopen(self.base + "/api/public/diffbench/info", timeout=20).read())["engine_build"]
        except Exception as e: return f"unreachable: {e}"
    def available(self): return (bool(self.base), "set DIFFBENCH_NEXUS_URL")
    def run(self, sc, dt):
        req = urllib.request.Request(self.base + "/api/public/diffbench/run", data=json.dumps({"entrant": self.entrant, "scenario": sc, "dt": dt}).encode(),
                                     headers={"Content-Type": "application/json", **({"Authorization": "Bearer " + self.token} if self.token else {})})
        for attempt in range(12):  # the public API allows 6 requests/min/IP; back off on HTTP 429
            try: return json.loads(urllib.request.urlopen(req, timeout=600).read())
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 11: raise
                time.sleep(11)


class NexusPgsHttp(_NexusHttp):
    name = "nexus_pgs"; entrant = "nexus_pgs"


class NexusDiffRigidHttp(_NexusHttp):
    name = "nexus_diffrigid"; entrant = "nexus_diffrigid"
