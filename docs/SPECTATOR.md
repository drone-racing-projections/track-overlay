# Spectator POV — TV and internet via the race box

This document describes the **secondary** video path. It is for audiences, not for flying.

## Why the race box owns distribution

The phone already composites AR for the **pilot** with minimal latency. Replicating that on a TV by mirroring the pilot path would either:

- add latency into the pilot’s eyes (unacceptable), or  
- require a second encode anyway.

So we treat spectator video as an explicit **delayed** product:

1. Phone (or a bench encoder) publishes a **moderate-bitrate** RTMP stream **after** (or alongside) local preview — never as the pilot’s only display.  
2. The **race box** receives that stream, packages **HLS** for LAN devices (smart TV browser, VLC, director UI), and optionally **restreams** to Twitch, YouTube, or another RTMP endpoint.

Telemetry and scoring remain on the lightweight JSON/WebSocket API; video is a separate concern.

## Modes

| Mode | Source | Use case |
|------|--------|----------|
| `ingest` (default) | Phone/encoder pushes `rtmp://<race-box>:1935/live/pilot` | Field event |
| `pull` | Race box pulls `pull_url` (RTMP/RTSP/HTTP) | Existing encoder or lab feed |
| `demo` | ffmpeg test pattern | Verify TV/director without aircraft |

## Requirements

- `ffmpeg` installed on the race box host (`apt install ffmpeg` / equivalent).  
- Ports: **8088** (API + HLS via HTTP), **1935** (RTMP ingest; configurable with `GATERACE_RTMP_PORT`).  
- LAN firewall allows TV/clients to reach the race box on 8088.

## Operator steps

1. Start the race box: `PYTHONPATH=. python3 race_box/server.py`  
2. Open the director UI → **Spectator POV**.  
3. Choose mode (start with **Demo pattern** to test the TV).  
4. Optionally set **Internet egress RTMP** (stream key URL from Twitch/YouTube).  
5. Click **Start relay**.  
6. On a TV or laptop on the same LAN, open:

   `http://<race-box-lan-ip>:8088/stream/index.m3u8`

   or use the embedded player in the director UI. VLC can open the same HLS URL.

### Phone publish URL (ingest mode)

```text
rtmp://<race-box-lan-ip>:1935/live/pilot
```

Stream key defaults to `pilot` (`GATERACE_STREAM_KEY`). Until MSDK streaming is wired in GateRace, any RTMP client (OBS, ffmpeg on a companion, vendor livestream) can publish a delayed copy of the feed for spectators.

Example from a machine that can see the phone’s screen or an HDMI capture:

```bash
ffmpeg -re -i input.mp4 -c:v libx264 -tune zerolatency -c:a aac \
  -f flv rtmp://192.168.1.10:1935/live/pilot
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/spectator` | Status (`running`, `hls_ready`, ingest hint, errors) |
| `POST` | `/spectator/start` | Body: `{ "mode", "pull_url?", "egress_rtmp_url?", ... }` |
| `POST` | `/spectator/stop` | Stop ffmpeg relay |
| `POST` | `/spectator/config` | Update settings without starting |
| `GET` | `/stream/{file}` | HLS playlist and segments (`index.m3u8`, `.ts`) |

## Latency expectations

| Path | Typical delay | OK for |
|------|----------------|--------|
| Pilot AR on phone | Frame-scale | Flying |
| Spectator HLS on LAN | ~2–8+ s | Sideline TV |
| Internet RTMP egress | often 5–15+ s | Online audience |

Do **not** ask pilots to fly off the spectator TV.

## Security notes

- Spectator ingest on a field AP should be treated as a **trusted LAN** service.  
- Prefer a private SSID; set `GATERACE_TOKEN` for the control API if the network is shared.  
- Do not expose RTMP ingest on the public internet without authentication and rate limits (out of scope for v1; use a proper media server if you need that).

## Implementation detail

Relay logic lives in `race_box/spectator.py` and is supervised by `race_box/server.py`. HLS files are written under `race_box/static/stream/` and served with short cache headers.
