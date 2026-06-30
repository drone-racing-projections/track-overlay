# API

Base URL: `http://<race-box-ip>:8088`  
Android emulator → host: `http://10.0.2.2:8088`  
WebSocket: `ws://<host>:8088/ws`

Telemetry and race control only. Pilot video does not use this channel. Spectator video: [SPECTATOR.md](SPECTATOR.md).

Optional auth: set `GATERACE_TOKEN` on the race box; send `Authorization: Bearer <token>` or `X-GateRace-Token`.

## Clocks

| Do | Don’t |
|----|--------|
| Send `t` as phone-monotonic seconds within the heat (often ~0 after Arm) | Use Unix time or browser `performance.now()` as race time |
| Keep `t` non-decreasing within a heat | Large backwards jumps (rejected) |

Soft start body: `{ "t": <phone heat time> }` only.

## Ownership

1. `POST /session/arm` with `pilot_id` opens a heat (`heat_id`).  
2. Other pilots receive **409** on telemetry.  
3. After **finished**, telemetry returns **409** until the next arm.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness; includes `clock_policy` |
| GET | `/tracks` | Track names |
| GET | `/tracks/{name}` | Track JSON |
| POST | `/session/arm` | `{ "track", "pilot_id" }` |
| POST | `/session/start` | Soft start `{ "t" }` |
| GET | `/session` | Current heat |
| POST | `/telemetry` | Position stream |
| GET | `/leaderboard` | Best times from log |
| GET | `/heats` | Recent heats |
| * | `/spectator…`, `/stream/…` | See spectator doc |
| WS | `/ws` | Live session + telemetry |

### Telemetry body

Required: `t`, `e`, `n`, `u` (ENU metres from track origin).  
Optional: attitude, gimbal fields, `pilot_id`.

| Outcome | Code |
|---------|------|
| Success | 200 (+ session fields, `new_passes`) |
| Invalid body | **400** |
| Not armed / wrong pilot / finished | **409** |

Target rate: **10–20 Hz** while armed or running. Phone converts WGS84 → ENU using the track origin.

### WebSocket

Server → client: `session`, `pass`, `finish`, `ping`, `error`  
Client → server: `hello`, `telemetry` (payload = POST body), `ping`

## Director UI

`http://<race-box-ip>:8088/` — arm heats, live state, leaderboard, spectator controls.
