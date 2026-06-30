#!/usr/bin/env python3
"""GateRace race box: HTTP + WebSocket, authoritative timing, director UI.

Clock policy: heat time `t` is **phone-monotonic seconds** within a heat (usually
starting near 0 when the phone begins streaming). Soft start and splits use only
this domain — never mix with wall clock or browser performance.now().

Heat ownership: one active pilot_id per armed heat; other sources get 409.
Finished heats ignore telemetry until re-arm (409 with reason).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from track_core.models import Track, Pose, RaceConfig
from track_core.race import RaceEngine, RaceState

try:
    from aiohttp import web
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "-q", "--break-system-packages"])
    from aiohttp import web

TRACKS = ROOT / "tracks"
STATIC = Path(__file__).resolve().parent / "static"
LOG_DIR = ROOT / "race_box" / "logs"
HEAT_LOG = LOG_DIR / "heats.jsonl"

# Optional shared secret: Authorization: Bearer <token> or X-GateRace-Token
API_TOKEN = os.environ.get("GATERACE_TOKEN", "").strip()

engine: RaceEngine | None = None
track_name = "demo_field"
splits: list[dict[str, Any]] = []
ws_clients: set[web.WebSocketResponse] = set()
active_pilot_id: str | None = None
last_pose_t: float | None = None  # last accepted telemetry t (phone clock)
heat_id: str | None = None
heat_armed_wall: float | None = None


class TelemetryError(Exception):
    def __init__(self, message: str, status: int = 400, extra: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.extra = extra or {}


def load_engine(name: str) -> tuple[RaceEngine, str]:
    path = TRACKS / f"{name}.json"
    if not path.exists():
        path = TRACKS / "demo_field.json"
        name = "demo_field"
    tr = Track.load(path)
    eng = RaceEngine(tr, RaceConfig())
    eng.arm()
    return eng, name


def session_payload() -> dict[str, Any]:
    global engine, track_name, splits, active_pilot_id, last_pose_t, heat_id
    if engine is None:
        engine, track_name = load_engine(track_name)
    res = engine.result()
    gates = engine.track.ordered_gates()
    next_id = None
    if engine._next_idx < len(gates):
        next_id = gates[engine._next_idx].id
    # Live elapsed in phone-clock domain when running
    elapsed = res.elapsed_s
    if (
        res.t_start is not None
        and engine.state == RaceState.RUNNING
        and last_pose_t is not None
    ):
        elapsed = max(0.0, last_pose_t - res.t_start)
    return {
        "track": track_name,
        "state": engine.state.value,
        "gates_hit": res.gates_hit,
        "next_gate_id": next_id,
        "elapsed_s": elapsed,
        "finished": res.finished,
        "t_start": res.t_start,
        "t_finish": res.t_finish,
        "splits": list(splits),
        "pilot_id": active_pilot_id,
        "heat_id": heat_id,
        "last_pose_t": last_pose_t,
        "clock": "phone_monotonic",
    }


def append_heat_log(record: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with HEAT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def finish_heat_if_needed(res) -> None:
    global heat_id, active_pilot_id, track_name, splits, heat_armed_wall
    if not res.finished or not heat_id:
        return
    rec = {
        "heat_id": heat_id,
        "track": track_name,
        "pilot_id": active_pilot_id,
        "elapsed_s": res.elapsed_s,
        "t_start": res.t_start,
        "t_finish": res.t_finish,
        "gates_hit": res.gates_hit,
        "splits": list(splits),
        "finished_wall": datetime.now(timezone.utc).isoformat(),
        "armed_wall": heat_armed_wall,
    }
    append_heat_log(rec)


def read_leaderboard(limit: int = 50) -> list[dict[str, Any]]:
    if not HEAT_LOG.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in HEAT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    # best times first (finished only)
    rows = [r for r in rows if r.get("elapsed_s") is not None]
    rows.sort(key=lambda r: (r.get("elapsed_s") is None, r.get("elapsed_s", 1e9)))
    return rows[:limit]


def parse_telemetry(data: dict[str, Any]) -> tuple[Pose, str]:
    if not isinstance(data, dict):
        raise TelemetryError("body must be a JSON object")
    missing = [k for k in ("t", "e", "n", "u") if k not in data or data[k] is None]
    if missing:
        raise TelemetryError(f"missing required fields: {', '.join(missing)}")
    try:
        t = float(data["t"])
        e = float(data["e"])
        n = float(data["n"])
        u = float(data["u"])
        yaw = float(data.get("yaw_deg", 0) or 0)
        pitch = float(data.get("pitch_deg", 0) or 0)
        roll = float(data.get("roll_deg", 0) or 0)
    except (TypeError, ValueError) as ex:
        raise TelemetryError(f"invalid numeric field: {ex}") from ex
    if t != t:  # NaN
        raise TelemetryError("t is NaN")
    gp = data.get("gimbal_pitch_deg")
    gy = data.get("gimbal_yaw_deg")
    try:
        gp = float(gp) if gp is not None else None
        gy = float(gy) if gy is not None else None
    except (TypeError, ValueError) as ex:
        raise TelemetryError(f"invalid gimbal field: {ex}") from ex
    pilot = str(data.get("pilot_id") or "").strip() or "anonymous"
    pose = Pose(
        t=t, e=e, n=n, u=u,
        yaw_deg=yaw, pitch_deg=pitch, roll_deg=roll,
        gimbal_pitch_deg=gp, gimbal_yaw_deg=gy,
    )
    return pose, pilot


def apply_telemetry(data: dict[str, Any]) -> tuple[dict[str, Any], list[str], Any]:
    global engine, track_name, splits, active_pilot_id, last_pose_t
    if engine is None:
        engine, track_name = load_engine(track_name)

    pose, pilot = parse_telemetry(data)

    if engine.state == RaceState.IDLE:
        raise TelemetryError("heat not armed — POST /session/arm first", status=409)
    if engine.state == RaceState.FINISHED:
        raise TelemetryError(
            "heat finished — re-arm for a new run",
            status=409,
            extra={"session": session_payload()},
        )

    # Ownership: first telemetry locks pilot; mismatches rejected
    if active_pilot_id is None:
        active_pilot_id = pilot
    elif pilot != active_pilot_id:
        raise TelemetryError(
            f"pilot_id mismatch: heat owned by {active_pilot_id!r}, got {pilot!r}",
            status=409,
            extra={"owner": active_pilot_id},
        )

    # Monotonic-ish phone clock (allow small jitter / equal)
    if last_pose_t is not None and pose.t + 0.05 < last_pose_t:
        raise TelemetryError(
            f"t went backwards (last={last_pose_t}, got={pose.t}) — keep phone_monotonic within heat",
            status=400,
        )
    last_pose_t = pose.t

    events = engine.update(pose)
    res = engine.result()
    new_ids: list[str] = []
    for ev in events:
        new_ids.append(ev.gate_id)
        split_s = None
        if res.t_start is not None:
            split_s = ev.t - res.t_start
        splits.append({"gate_id": ev.gate_id, "t": ev.t, "split_s": split_s})
    if res.finished:
        finish_heat_if_needed(res)
    out = session_payload()
    out["new_passes"] = new_ids
    return out, new_ids, res


async def broadcast(msg_type: str, payload: dict[str, Any]) -> None:
    dead = []
    data = json.dumps({"type": msg_type, "payload": payload})
    for ws in list(ws_clients):
        try:
            await ws.send_str(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_clients.discard(ws)


async def handle_telemetry_result(out, new_ids, res) -> dict[str, Any]:
    await broadcast("session", {k: out[k] for k in out if k != "new_passes"})
    for gid in new_ids:
        sp = next((s for s in reversed(splits) if s["gate_id"] == gid), {})
        await broadcast("pass", {"gate_id": gid, "t": sp.get("t"), "split_s": sp.get("split_s")})
    if res.finished:
        await broadcast(
            "finish",
            {
                "elapsed_s": res.elapsed_s,
                "gates_hit": res.gates_hit,
                "pilot_id": active_pilot_id,
                "heat_id": heat_id,
            },
        )
    return out


def check_auth(request: web.Request) -> web.Response | None:
    if not API_TOKEN:
        return None
    auth = request.headers.get("Authorization", "")
    token = request.headers.get("X-GateRace-Token", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip() or token
    if token != API_TOKEN:
        return web.json_response({"error": "unauthorized"}, status=401)
    return None


async def get_health(request: web.Request) -> web.Response:
    return web.json_response({
        "ok": True,
        "t_server_wall": time.time(),
        "clock_policy": "phone_monotonic",
        "auth_required": bool(API_TOKEN),
    })


async def get_session(request: web.Request) -> web.Response:
    return web.json_response(session_payload())


async def post_arm(request: web.Request) -> web.Response:
    global engine, track_name, splits, active_pilot_id, last_pose_t, heat_id, heat_armed_wall
    denied = check_auth(request)
    if denied:
        return denied
    try:
        data = await request.json()
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    track_name = str(data.get("track") or "demo_field")
    path = TRACKS / f"{track_name}.json"
    if not path.exists():
        return web.json_response({"error": f"track not found: {track_name}"}, status=404)
    pilot = str(data.get("pilot_id") or "").strip() or None
    engine, track_name = load_engine(track_name)
    splits = []
    active_pilot_id = pilot  # may be None until first telemetry
    last_pose_t = None
    heat_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    heat_armed_wall = time.time()
    payload = session_payload()
    await broadcast("session", payload)
    return web.json_response(payload)


async def post_start(request: web.Request) -> web.Response:
    """Soft start using **phone-monotonic** `t` only (same domain as telemetry)."""
    global engine, last_pose_t
    denied = check_auth(request)
    if denied:
        return denied
    if engine is None:
        engine, _ = load_engine(track_name)
    try:
        data = await request.json()
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    # Prefer explicit phone clock field `t`; reject legacy wall/browser fields as start clock
    if "t" not in data:
        return web.json_response(
            {
                "error": "soft start requires phone-monotonic field 't' (same domain as telemetry)",
                "hint": "send {\"t\": <phone_pose_t>}; do not use performance.now() or unix wall time",
            },
            status=400,
        )
    try:
        t = float(data["t"])
    except (TypeError, ValueError):
        return web.json_response({"error": "invalid t"}, status=400)
    if engine.state == RaceState.ARMED:
        engine.state = RaceState.RUNNING
        engine._t_start = t
        last_pose_t = t
    elif engine.state == RaceState.FINISHED:
        return web.json_response({"error": "heat finished — re-arm first", **session_payload()}, status=409)
    payload = session_payload()
    await broadcast("session", payload)
    return web.json_response(payload)


async def post_telemetry(request: web.Request) -> web.Response:
    denied = check_auth(request)
    if denied:
        return denied
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "invalid JSON body"}, status=400)
    try:
        out, new_ids, res = apply_telemetry(data)
    except TelemetryError as e:
        body = {"error": e.message, **e.extra}
        return web.json_response(body, status=e.status)
    out = await handle_telemetry_result(out, new_ids, res)
    return web.json_response(out)


async def get_track(request: web.Request) -> web.Response:
    name = request.match_info["name"]
    p = TRACKS / f"{name}.json"
    if not p.exists():
        return web.json_response({"error": "not found"}, status=404)
    return web.json_response(json.loads(p.read_text()))


async def list_tracks(request: web.Request) -> web.Response:
    names = sorted(p.stem for p in TRACKS.glob("*.json"))
    return web.json_response({"tracks": names})


async def get_leaderboard(request: web.Request) -> web.Response:
    try:
        limit = int(request.query.get("limit", "50"))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 500))
    track = request.query.get("track")
    rows = read_leaderboard(limit=500)
    if track:
        rows = [r for r in rows if r.get("track") == track]
    return web.json_response({"leaderboard": rows[:limit]})


async def get_heats(request: web.Request) -> web.Response:
    """Raw recent heat log (newest last in file; we reverse for display)."""
    if not HEAT_LOG.exists():
        return web.json_response({"heats": []})
    rows = []
    for line in HEAT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return web.json_response({"heats": rows[-100:]})


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    denied = check_auth(request)
    # WS can't easily return JSON 401 before upgrade on all clients; close if token required
    ws = web.WebSocketResponse(heartbeat=20.0)
    await ws.prepare(request)
    if denied is not None:
        await ws.send_str(json.dumps({"type": "error", "payload": {"error": "unauthorized"}}))
        await ws.close(code=4401, message=b"unauthorized")
        return ws
    ws_clients.add(ws)
    await ws.send_str(json.dumps({"type": "session", "payload": session_payload()}))
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    await ws.send_str(json.dumps({"type": "error", "payload": {"error": "invalid JSON"}}))
                    continue
                typ = data.get("type")
                if typ == "telemetry":
                    try:
                        out, new_ids, res = apply_telemetry(data.get("payload") or {})
                        out = await handle_telemetry_result(out, new_ids, res)
                        await ws.send_str(json.dumps({"type": "session", "payload": out}))
                    except TelemetryError as e:
                        await ws.send_str(json.dumps({
                            "type": "error",
                            "payload": {"error": e.message, "status": e.status, **e.extra},
                        }))
                elif typ == "hello":
                    await ws.send_str(json.dumps({"type": "session", "payload": session_payload()}))
                elif typ == "ping":
                    await ws.send_str(json.dumps({
                        "type": "ping",
                        "payload": {"t_server_wall": time.time()},
                    }))
            elif msg.type in (web.WSMsgType.ERROR, web.WSMsgType.CLOSE):
                break
    finally:
        ws_clients.discard(ws)
    return ws


async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(STATIC / "index.html")


async def static_file(request: web.Request) -> web.Response:
    name = request.match_info["name"]
    path = STATIC / name
    if not path.exists() or not path.is_file():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", get_health)
    app.router.add_get("/session", get_session)
    app.router.add_post("/session/arm", post_arm)
    app.router.add_post("/session/start", post_start)
    app.router.add_post("/telemetry", post_telemetry)
    app.router.add_get("/tracks", list_tracks)
    app.router.add_get("/tracks/{name}", get_track)
    app.router.add_get("/leaderboard", get_leaderboard)
    app.router.add_get("/heats", get_heats)
    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/", index)
    app.router.add_get("/static/{name}", static_file)
    return app


def main() -> None:
    global engine, track_name, active_pilot_id, last_pose_t, heat_id, splits
    engine, track_name = load_engine("demo_field")
    active_pilot_id = None
    last_pose_t = None
    heat_id = None
    splits = []
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    app = create_app()
    auth_note = " auth=ON" if API_TOKEN else " auth=off"
    print(f"GateRace race box http://0.0.0.0:8088  (director UI /){auth_note}")
    web.run_app(app, host="0.0.0.0", port=8088, print=lambda *a: None)


if __name__ == "__main__":
    main()
