# GateRace phone ↔ race box API

Base URL (field Wi‑Fi): `http://<race-box-ip>:8088`  
Emulator → host: `http://10.0.2.2:8088`  
WebSocket: `ws://<host>:8088/ws`

Pilot **video never uses this link** — only race control + telemetry.

Optional auth: set env `GATERACE_TOKEN` on the race box; send `Authorization: Bearer <token>` or `X-GateRace-Token`.

## Clock policy (required)

- Field **`t` is phone-monotonic seconds within a heat** (typically starts near 0 when the phone begins the heat / after Arm resets sim).
- **Do not** mix unix wall time or browser `performance.now()` into `t` or soft start.
- Soft start body: `{ "t": <phone_monotonic> }` only.
- Race box rejects backwards `t` (beyond 50 ms jitter).

## Heat ownership

- `POST /session/arm` with `{ "track", "pilot_id" }` creates a heat (`heat_id`).
- First telemetry locks `pilot_id` if not set at arm; other pilots get **409**.
- After **finished**, telemetry gets **409** until re-arm (no silent ignore).

## Track

### `GET /tracks` → `{ "tracks": ["demo_field", ...] }`
### `GET /tracks/{name}` — track JSON (origin + gates)

## Session

### `POST /session/arm`
```json
{ "track": "demo_field", "pilot_id": "pilot1" }
```

### `POST /session/start` (soft start)
```json
{ "t": 0.0 }
```
Phone-monotonic only. Invalid without `t`.

### `GET /session`
Includes `pilot_id`, `heat_id`, `last_pose_t`, `clock: "phone_monotonic"`, live `elapsed_s` while running.

## Telemetry

### `POST /telemetry`
Required: `t`, `e`, `n`, `u`. Optional attitude/gimbal/`pilot_id`.
Invalid body → **400** with `{ "error": "..." }`. Ownership/finished → **409**.

Send **10–20 Hz** while armed/running. Stop when finished (client should re-arm).

## Leaderboard / history

- `GET /leaderboard?limit=50&track=demo_field` — best times from `race_box/logs/heats.jsonl`
- `GET /heats` — recent heat records

## WebSocket `/ws`

Messages: `session`, `pass`, `finish`, `ping`, `error`.

Client may send: `hello`, `telemetry` `{ "type":"telemetry", "payload": {…} }`, `ping`.

## Health

`GET /health` → `{ "ok": true, "clock_policy": "phone_monotonic", "auth_required": false, "t_server_wall": … }`

## Director UI

`http://<race-box-ip>:8088/`
