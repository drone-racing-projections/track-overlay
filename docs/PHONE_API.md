# Phone ↔ race box API

Base URL on the field LAN: `http://<race-box-ip>:8088`  

Android emulator → host loopback: `http://10.0.2.2:8088`  

WebSocket: `ws://<host>:8088/ws`

This link carries **race control and telemetry only**. Pilot video for flying does not use it. Spectator video uses RTMP/HLS as described in [SPECTATOR.md](SPECTATOR.md).

Optional API auth: set `GATERACE_TOKEN` on the race box; send `Authorization: Bearer <token>` or header `X-GateRace-Token`.

---

## Clock policy

| Rule | Detail |
|------|--------|
| Heat time domain | Field `t` is **phone-monotonic seconds within a heat** |
| Soft start | Body must include `{ "t": <phone_monotonic> }` only |
| Forbidden for scoring | Unix wall clock, browser `performance.now()` |
| Backwards `t` | Rejected (beyond ~50 ms jitter) |

The race box may return `clock: "phone_monotonic"` and `last_pose_t` so directors can display live elapsed time without inventing a second clock.

---

## Heat ownership

1. `POST /session/arm` creates a heat (`heat_id`) and optional `pilot_id`.  
2. Telemetry from another `pilot_id` receives **409**.  
3. After the heat **finishes**, telemetry receives **409** until the next arm.

Only one active telemetry source per heat.

---

## Endpoints

### Health

`GET /health` → `{ "ok": true, "clock_policy": "phone_monotonic", "auth_required": false, "t_server_wall": … }`

### Tracks

- `GET /tracks` → `{ "tracks": ["demo_field", …] }`  
- `GET /tracks/{name}` → track JSON (origin + gates)

### Session

**Arm**

`POST /session/arm`

```json
{ "track": "demo_field", "pilot_id": "pilot1" }
```

**Soft start** (optional; usually the first gate starts the clock)

`POST /session/start`

```json
{ "t": 0.0 }
```

**Read session**

`GET /session` — includes `state`, `gates_hit`, `next_gate_id`, `elapsed_s`, `t_start`, `t_finish`, `splits`, `pilot_id`, `heat_id`, `last_pose_t`, `finished`.

### Telemetry

`POST /telemetry`

Required: `t`, `e`, `n`, `u` (track ENU metres). Optional: attitude, gimbal, `pilot_id`.

| Outcome | HTTP |
|---------|------|
| OK | 200 + session fields + `new_passes` |
| Bad / incomplete body | **400** `{ "error": "…" }` |
| Wrong pilot / finished / not armed | **409** |

Target rate: **10–20 Hz** while armed or running. Stop sending after finish until re-arm.

Phone converts WGS84 → ENU using the track origin before posting.

### Leaderboard and history

- `GET /leaderboard?limit=50&track=demo_field` — best times from `race_box/logs/heats.jsonl`  
- `GET /heats` — recent heat records  

### Spectator control

See [SPECTATOR.md](SPECTATOR.md): `/spectator`, `/spectator/start`, `/spectator/stop`, `/stream/...`.

---

## WebSocket `/ws`

**Server → client:** `session`, `pass`, `finish`, `ping`, `error`  

**Client → server:**

```json
{ "type": "hello", "pilot_id": "pilot1" }
{ "type": "telemetry", "payload": { /* same as POST /telemetry */ } }
{ "type": "ping" }
```

Prefer WebSocket telemetry once connected; HTTP remains supported.

---

## Director UI

Open `http://<race-box-ip>:8088/` for arming, live session state, leaderboard, and spectator relay controls.
