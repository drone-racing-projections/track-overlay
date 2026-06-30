#!/usr/bin/env python3
"""API validation, ownership, finish lock, mock multi-speed gate completion."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = "http://127.0.0.1:8088"


def http(method: str, path: str, body: dict | None = None, timeout: float = 3.0):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            j = json.loads(raw)
        except Exception:
            j = {"raw": raw}
        return e.code, j


def main() -> None:
    code, h = http("GET", "/health")
    assert code == 200 and h.get("ok"), h
    assert h.get("clock_policy") == "phone_monotonic"

    code, j = http("POST", "/telemetry", {})
    assert code == 400, (code, j)

    code, sess = http("POST", "/session/arm", {"track": "demo_field", "pilot_id": "alice"})
    assert code == 200 and sess["state"] == "armed", sess
    assert sess.get("pilot_id") == "alice"
    assert sess.get("heat_id")

    code, j = http("POST", "/telemetry", {
        "t": 0.1, "e": 0, "n": 0, "u": 10, "pilot_id": "bob"
    })
    assert code == 409, (code, j)

    code, j = http("POST", "/session/start", {"t_server": 1.0})
    assert code == 400, (code, j)

    code, j = http("POST", "/session/start", {"t": 0.0})
    assert code == 200 and j["state"] == "running", j

    from track_core.models import Track
    from sim.dji_telemetry_mock import DjiTelemetryMock

    track = Track.load(ROOT / "tracks" / "demo_field.json")
    for speed in (8.0, 14.0, 25.0):
        for noise in (0.0, 1.5, 2.0):
            http("POST", "/session/arm", {"track": "demo_field", "pilot_id": "dji_mock"})
            mock = DjiTelemetryMock(track, speed_mps=speed, hz=20.0, gnss_noise_m=noise, seed=1)
            finished = False
            for _ in range(2000):
                _, _, tel = mock.tick()
                code, out = http("POST", "/telemetry", tel)
                assert code == 200, (speed, noise, code, out)
                if out.get("finished"):
                    finished = True
                    assert out.get("gates_hit") == ["g1", "g2", "g3", "g4"], out
                    break
            assert finished, f"did not finish speed={speed} noise={noise}"

    code, j = http("POST", "/telemetry", {
        "t": 99, "e": 0, "n": 0, "u": 10, "pilot_id": "dji_mock"
    })
    assert code == 409, (code, j)

    code, lb = http("GET", "/leaderboard")
    assert code == 200
    assert isinstance(lb.get("leaderboard"), list)
    assert len(lb["leaderboard"]) >= 1

    http("POST", "/session/arm", {"track": "demo_field", "pilot_id": "clock"})
    code, _ = http("POST", "/telemetry", {"t": 1.0, "e": 0, "n": 0, "u": 1, "pilot_id": "clock"})
    assert code == 200
    code, j = http("POST", "/telemetry", {"t": 0.5, "e": 0, "n": 0, "u": 1, "pilot_id": "clock"})
    assert code == 400, (code, j)

    print("API + mock regression OK")


if __name__ == "__main__":
    main()
