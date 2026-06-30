#!/usr/bin/env python3
"""Host-side DJI-style telemetry mock for the GateRace race box.

Simulates what an MSDK phone would publish after converting aircraft
GPS/attitude into track ENU — without a real aircraft or Android device.

Flies *through* each gate plane (back→front along the gate normal) so
pass detection on the race box registers clean hits.

Usage (from repo root):
  PYTHONPATH=. python3 sim/dji_telemetry_mock.py
  PYTHONPATH=. python3 sim/dji_telemetry_mock.py --url http://127.0.0.1:8088 --track demo_field
  PYTHONPATH=. python3 sim/dji_telemetry_mock.py --once
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from track_core.models import Track, Pose, Gate


@dataclass
class DjiAircraftState:
    latitude: float
    longitude: float
    altitude_m: float
    yaw_deg: float
    pitch_deg: float
    roll_deg: float
    gimbal_pitch_deg: float
    gimbal_yaw_deg: float
    gimbal_roll_deg: float
    velocity_x_mps: float
    velocity_y_mps: float
    velocity_z_mps: float
    gps_satellites: int
    gps_signal_level: int
    flight_mode: str
    t_aircraft_s: float
    t_unix: float


def http_json(method: str, url: str, body: dict | None = None, timeout: float = 2.0) -> dict:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def load_track(name: str) -> Track:
    path = ROOT / "tracks" / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"track not found: {path}")
    return Track.load(path)


def wrap_yaw(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


class DjiTelemetryMock:
    """Waypoint path: approach behind each gate, then fly through along normal."""

    def __init__(
        self,
        track: Track,
        speed_mps: float = 14.0,
        hz: float = 20.0,
        gnss_noise_m: float = 0.8,
        attitude_noise_deg: float = 0.4,
        seed: int | None = 42,
        standoff_m: float = 35.0,
    ):
        self.track = track
        self.speed = speed_mps
        self.dt = 1.0 / hz
        self.gnss_noise_m = gnss_noise_m
        self.attitude_noise_deg = attitude_noise_deg
        self.rng = random.Random(seed)
        self.gates = track.ordered_gates()
        self.waypoints: list[tuple[float, float, float]] = []
        for g in self.gates:
            ne, nn, nu = g.normal()
            # behind plane → through center → slightly past (guarantees d0<0 → d1>0)
            self.waypoints.append((g.e - ne * standoff_m, g.n - nn * standoff_m, g.u - nu * standoff_m + 1.0))
            self.waypoints.append((g.e, g.n, g.u))
            self.waypoints.append((g.e + ne * 8.0, g.n + nn * 8.0, g.u + nu * 8.0))
        self.wp_idx = 0
        self.e, self.n, self.u = self.waypoints[0]
        # nudge slightly so we start clearly behind first gate
        self.e -= 0.5
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.gimbal_pitch = -10.0
        self.gimbal_yaw = 0.0
        self.t = 0.0
        self.vx_n = 0.0
        self.vy_e = 0.0
        self.vz_d = 0.0

    def tick(self) -> tuple[DjiAircraftState, Pose, dict]:
        # chase current waypoint
        if self.wp_idx >= len(self.waypoints):
            te, tn, tu = self.waypoints[-1]
        else:
            te, tn, tu = self.waypoints[self.wp_idx]
        de, dn, du = te - self.e, tn - self.n, tu - self.u
        dist = math.sqrt(de * de + dn * dn + du * du) or 0.01
        desired_yaw = math.degrees(math.atan2(de, dn))
        dyaw = wrap_yaw(desired_yaw - self.yaw)
        self.yaw = wrap_yaw(self.yaw + max(-120 * self.dt, min(120 * self.dt, dyaw)))
        # move in 3D toward waypoint (not only yaw-forward) so we thread gates
        step = min(self.speed * self.dt, dist)
        self.e += de / dist * step
        self.n += dn / dist * step
        self.u += du / dist * step
        self.vx_n = dn / dist * self.speed
        self.vy_e = de / dist * self.speed
        self.vz_d = -du / dist * self.speed
        self.roll = max(-15.0, min(15.0, dyaw * 0.2))
        self.pitch = max(-10.0, min(10.0, -du / dist * 5.0))
        self.t += self.dt
        if dist < 2.0 and self.wp_idx < len(self.waypoints) - 1:
            self.wp_idx += 1

        ne = self.e + self.rng.gauss(0, self.gnss_noise_m)
        nn = self.n + self.rng.gauss(0, self.gnss_noise_m)
        nu = self.u + self.rng.gauss(0, self.gnss_noise_m * 0.5)
        nyaw = wrap_yaw(self.yaw + self.rng.gauss(0, self.attitude_noise_deg))
        npitch = self.pitch + self.rng.gauss(0, self.attitude_noise_deg * 0.5)
        nroll = self.roll + self.rng.gauss(0, self.attitude_noise_deg * 0.5)
        ngp = self.gimbal_pitch + self.rng.gauss(0, 0.2)

        lat, lon, alt = self.track.origin.to_llh(ne, nn, nu)
        dji = DjiAircraftState(
            latitude=lat, longitude=lon, altitude_m=alt,
            yaw_deg=nyaw, pitch_deg=npitch, roll_deg=nroll,
            gimbal_pitch_deg=ngp, gimbal_yaw_deg=self.gimbal_yaw, gimbal_roll_deg=0.0,
            velocity_x_mps=self.vx_n, velocity_y_mps=self.vy_e, velocity_z_mps=self.vz_d,
            gps_satellites=self.rng.randint(14, 22), gps_signal_level=5,
            flight_mode="GPS_ATTI", t_aircraft_s=self.t, t_unix=time.time(),
        )
        pose = Pose(
            t=self.t, e=ne, n=nn, u=nu,
            yaw_deg=nyaw, pitch_deg=npitch, roll_deg=nroll,
            gimbal_pitch_deg=ngp, gimbal_yaw_deg=self.gimbal_yaw,
        )
        tel = {
            "t": pose.t, "e": pose.e, "n": pose.n, "u": pose.u,
            "yaw_deg": pose.yaw_deg, "pitch_deg": pose.pitch_deg, "roll_deg": pose.roll_deg,
            "gimbal_pitch_deg": pose.gimbal_pitch_deg, "gimbal_yaw_deg": pose.gimbal_yaw_deg,
            "pilot_id": "dji_mock",
            "_dji": {
                "lat": dji.latitude, "lon": dji.longitude, "alt_m": dji.altitude_m,
                "gps_sats": dji.gps_satellites, "flight_mode": dji.flight_mode,
                "vel_ned_mps": [dji.velocity_x_mps, dji.velocity_y_mps, dji.velocity_z_mps],
            },
        }
        return dji, pose, tel


def main() -> None:
    ap = argparse.ArgumentParser(description="DJI telemetry mock → GateRace race box")
    ap.add_argument("--url", default="http://127.0.0.1:8088")
    ap.add_argument("--track", default="demo_field")
    ap.add_argument("--hz", type=float, default=20.0)
    ap.add_argument("--speed", type=float, default=14.0)
    ap.add_argument("--duration", type=float, default=0.0, help="0 = until finish / timeout")
    ap.add_argument("--timeout", type=float, default=120.0, help="safety timeout seconds")
    ap.add_argument("--no-arm", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--gnss-noise", type=float, default=0.8)
    args = ap.parse_args()

    track = load_track(args.track)
    mock = DjiTelemetryMock(track, speed_mps=args.speed, hz=args.hz, gnss_noise_m=args.gnss_noise)

    if args.once:
        dji, pose, tel = mock.tick()
        print(json.dumps({"dji": asdict(dji), "telemetry": tel}, indent=2))
        return

    base = args.url.rstrip("/")
    try:
        h = http_json("GET", f"{base}/health")
        print(f"race box ok: {h}", flush=True)
    except Exception as e:
        print(f"ERROR: cannot reach race box at {base}: {e}", file=sys.stderr)
        raise SystemExit(1)

    if not args.no_arm:
        sess = http_json("POST", f"{base}/session/arm", {"track": args.track, "pilot_id": "dji_mock"})
        print(f"armed: state={sess.get('state')} next={sess.get('next_gate_id')}", flush=True)

    t0 = time.monotonic()
    n = 0
    last_print = 0.0
    try:
        while True:
            loop_start = time.monotonic()
            dji, pose, tel = mock.tick()
            try:
                out = http_json("POST", f"{base}/telemetry", tel)
            except urllib.error.HTTPError as e:
                print(f"telemetry HTTP {e.code}", file=sys.stderr, flush=True)
                out = {}
            n += 1
            if args.verbose or (loop_start - last_print) > 1.0:
                last_print = loop_start
                print(
                    f"t={pose.t:6.2f}s ENU=({pose.e:6.1f},{pose.n:6.1f},{pose.u:5.1f}) "
                    f"yaw={pose.yaw_deg:6.1f} state={out.get('state')} "
                    f"next={out.get('next_gate_id')} hits={out.get('gates_hit')} new={out.get('new_passes')}",
                    flush=True,
                )
            if out.get("finished"):
                print(f"FINISH elapsed_s={out.get('elapsed_s')} gates={out.get('gates_hit')} frames={n}", flush=True)
                break
            elapsed_wall = time.monotonic() - t0
            if args.duration > 0 and elapsed_wall >= args.duration:
                print(f"duration reached frames={n}", flush=True)
                break
            if elapsed_wall >= args.timeout:
                print(f"TIMEOUT frames={n} state={out.get('state')} hits={out.get('gates_hit')}", flush=True)
                raise SystemExit(2)
            sleep = mock.dt - (time.monotonic() - loop_start)
            if sleep > 0:
                time.sleep(sleep)
    except KeyboardInterrupt:
        print(f"\nstopped frames={n}", flush=True)


if __name__ == "__main__":
    main()
