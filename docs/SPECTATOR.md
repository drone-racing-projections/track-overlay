# Spectator video

Delayed video for audiences (TV or internet), managed by the race box. Not for piloting.

## Pipeline

1. A source publishes video to the race box (phone RTMP later, OBS, or a test pattern).  
2. The race box runs `ffmpeg` and serves **HLS** on the LAN.  
3. Optionally it restreams to an external RTMP URL (Twitch, YouTube, custom).

Requires **`ffmpeg`** on the race box host.

## Modes

| Mode | Source |
|------|--------|
| `ingest` | RTMP push to `rtmp://<race-box>:1935/live/pilot` |
| `pull` | Race box pulls `pull_url` |
| `demo` | Built-in test pattern |

Defaults: port **1935**, stream key **`pilot`** (`GATERACE_RTMP_PORT`, `GATERACE_STREAM_KEY`).

## Operator steps

1. Start the race box.  
2. Use the director UI Spectator panel, or the API.  
3. Start with **demo** to verify the TV path.  
4. On the LAN: `http://<race-box-ip>:8088/stream/index.m3u8` (VLC, TV browser, or director player).  
5. Optional: set an egress RTMP URL for the internet.

```bash
curl -X POST http://127.0.0.1:8088/spectator/start \
  -H 'Content-Type: application/json' \
  -d '{"mode":"demo"}'

curl -X POST http://127.0.0.1:8088/spectator/stop
curl http://127.0.0.1:8088/spectator
```

## Latency

LAN HLS is often a few seconds; internet egress often more. Keep pilots on the phone path.

## Security

Treat RTMP ingest as a trusted field LAN service in v1. Don’t expose it to the public internet without a proper media stack and auth.
