# Spectator video (TV / internet)

This is **not** for flying. Pilots use the phone. Spectators can watch something delayed.

## Idea

1. Something publishes video **to** the race box (phone RTMP later, or OBS, or a test pattern).  
2. Race box runs `ffmpeg` and writes **HLS** for the LAN.  
3. Optionally it also **pushes** out to Twitch/YouTube/etc.

Needs **`ffmpeg`** installed on the race box machine.

## Modes

| Mode | Meaning |
|------|---------|
| `ingest` | Wait for RTMP push at `rtmp://<race-box>:1935/live/pilot` |
| `pull` | Race box pulls a URL you give it |
| `demo` | Colour bars / test pattern (no aircraft) |

Port **1935** and stream key `pilot` are defaults (`GATERACE_RTMP_PORT`, `GATERACE_STREAM_KEY`).

## Operator flow

1. Start race box.  
2. Director UI → Spectator, or API below.  
3. Start **demo** first to verify the TV.  
4. On LAN open: `http://<race-box-ip>:8088/stream/index.m3u8` (VLC or TV browser).  
5. Optional: set egress RTMP URL for the internet.

```bash
curl -X POST http://127.0.0.1:8088/spectator/start \
  -H 'Content-Type: application/json' \
  -d '{"mode":"demo"}'

curl -X POST http://127.0.0.1:8088/spectator/stop
curl http://127.0.0.1:8088/spectator
```

## Expect delay

LAN HLS: often a few seconds. Internet: often more. **Never** pilot off this.

## Security

Field LAN only for v1 ingest. Don’t expose RTMP to the open internet without a real media stack and auth.
