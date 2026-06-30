# Architecture options (research background)

This note captures alternatives considered before locking **Decision V1** (see [docs/DECISION_V1.md](docs/DECISION_V1.md)). It remains useful when revisiting constraints (goggles, open FPV, enterprise airframes).

---

## Product definition

**Pilot experience:** live camera video with **world-locked** virtual gates (not HUD stickers), ordered checkpoints, timing and leaderboards.

**Not required for v1:** physical inflatable gates, autonomous flight, global cloud multiplayer.

**Core problem:** project gates from world coordinates into the camera image each frame using position, orientation, and camera extrinsics/intrinsics with low enough latency that gates do not “swim.”

---

## Ecosystem constraints (summary)

| Platform | Overlay on pilot display? | Notes |
|----------|---------------------------|--------|
| DJI MSDK V5 on phone/RC | **Yes** | Best fit for stock Mini/Air-class aircraft |
| Stock DJI Fly | No | Closed app |
| DJI Goggles / digital FPV | No custom AR injection | Great for flying feel; poor for *our* rings in-goggle |
| Open FPV + companion computer | Yes, with electronics | Maximum control, not “buy DJI and go” |
| Ground compositor (capture card) | On a **second** screen | Fine for spectators; wrong latency for piloting |

Livestream protocols (RTMP/RTSP/WebRTC to cloud) often add **hundreds of milliseconds to seconds** — acceptable for **spectators**, not for piloting AR.

---

## Options compared

| Option | Idea | Pilot latency | DJI-centric | Complexity |
|--------|------|---------------|-------------|------------|
| **A — MSDK app (chosen)** | AR on phone liveview; race box for timing | Best among DJI paths | High | App + field LAN |
| **B — Ground compositor** | Capture RC/goggles HDMI → PC overlays | Poor if used to pilot | High | Capture hardware |
| **C — Open FPV + companion** | Full stack on custom craft | Excellent if tuned | Low | High build burden |
| **D — Hybrid Avata/goggles + telemetry scoring** | Fly goggles; score on ground | N/A for AR-in-eyes | Medium | Split experience |
| **E — Enterprise + RTK** | Matrice-class, richer APIs | Good | Enterprise cost | Budget |

**V1 selection:** Option **A**, with Option **B**-style outputs only for **spectators** via the race box relay ([docs/SPECTATOR.md](docs/SPECTATOR.md)).

---

## Shared backend regardless of video path

Track files, ENU math, pass detection, and race state machine (`track_core/`, `race_box/`) stay independent of whether video is MSDK, open FPV, or spectator-only. That keeps a future compositor or companion path from rewriting scoring.

---

## Safety themes

Geofence, max speed, and lost-link behaviour remain on the aircraft vendor stack. AR must never be the sole attitude reference. Clear demo vs race modes and local regulation compliance are event-ops concerns, not overlay features.
