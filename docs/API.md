# API — phone and tools → race box

Base URL: `http://<race-box-ip>:8088`  
Emulator → host: `http://10.0.2.2:8088`  
WebSocket: `ws://<host>:8088/ws`

**Telemetry and control only.** Pilot flying video does not use this. Spectator video: [SPECTATOR.md](SPECTATOR.md).

Optional auth: race box env `GATERACE_TOKEN`; clients send `Authorization: Bearer …` or `X-GateRace-Token`.

---

## Clocks (read this)

| Do | Don’t |
|----|--------|
| Send `t` as **seconds on the phone during this heat** (often ~0 after Arm) | Send Unix time or browser `performance.now()` as race time |
| Keep `t` moving forward within a heat | Jump backwards (server rejects large regressions) |

Soft start body is only: `{ "t": <phone heat time> }`.

---

## Ownership

1. `POST /session/arm` with `pilot_id` starts a heat (`heat_id`).  
2. Other pilots get **409** on telemetry.  
3. After **finished**, telemetry gets **409** until the next arm.

---

## Endpoints (short)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness; includes `clock_policy` |
| GET | `/tracks` | List track names |
| GET | `/tracks/{name}` | Track JSON (origin + gates) |
| POST | `/session/arm` | `{ "track", "pilot_id" }` |
| POST | `/session/start` | Soft start `{ "t" }` only |
| GET | `/session` | Current heat state |
| POST | `/telemetry` | Position stream (below) |
| GET | `/leaderboard` | Best times from log file |
| GET | `/heats` | Recent heat records |
| GET/POST | `/spectator…` | See spectator doc |
| GET | `/stream/{file}` | HLS files |
| WS | `/ws` | Live session + telemetry |

### Telemetry body

Required: `t`, `e`, `n`, `u` (ENU metres from track origin).  
Optional: `yaw_deg`, `pitch_deg`, `roll_deg`, gimbal fields, `pilot_id`.

| Result | Code |
|--------|------|
| OK | 200 (+ session fields, `new_passes`) |
| Bad JSON / missing fields | **400** |
| Not armed / wrong pilot / finished | **409** |

Target **10–20 Hz** while armed/running.

### WebSocket messages

Server → client: `session`, `pass`, `finish`, `ping`, `error`  
Client → server: `hello`, `telemetry` (payload = same as POST body), `ping`

---

## Director UI

`http://<race-box-ip>:8088/` — arm, watch heat, leaderboard, spectator controls.
