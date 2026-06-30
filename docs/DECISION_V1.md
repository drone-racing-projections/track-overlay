# Decision V1 — Latency-first AR gate racing (DJI + ground race box)

**Date:** 2026-06-30  
**Priority order:** (1) pilot visual latency / fun (2) come-and-fly ops (3) commercial DJI airframe (4) accuracy good enough for large outdoor gates

## Locked choices

| Decision | Choice | Why |
|----------|--------|-----|
| Pilot primary view | **Custom Android app (MSDK V5)** on phone mounted to RC (prefer RC *without* built-in screen so *our* app owns the pixels) | Only practical way to put **world-locked rings in the pilot’s eyes** on a **stock DJI** without reverse-engineering goggles. Avoid RTMP/spectator paths for piloting. |
| Authoritative timing | **Ground race box** (field laptop / NUC) | Fair multi-pilot clock, logs, leaderboards; air/app only sends telemetry + soft cues. |
| Gate scale (v1) | **Large outdoor rings** (≈8–15 m diameter, generous thickness) | Consumer GNSS is meters-level; large gates keep passes fun and forgiving while pose is imperfect. |
| Aircraft (v1 target) | **DJI Mini 4 Pro** (MSDK V5 supported) + RC that uses a phone | Best price/stability/gimbal vs enterprise; verify current MSDK support list at purchase. Alternate: Mini 3 Pro. |
| Render location | **On the phone in the MSDK app** (GPU, minimal copies) | Adding a ground video hop for the *pilot* adds latency — forbidden for pilot path. Ground PC may render **spectator** views only (delay OK). |
| Not in v1 pilot path | Stock Fly app, RTMP livestream, goggles-only AR | Fly is closed; RTMP is multi-second; DJI goggles can’t inject our 3D overlay. |
| Later adapter | Open FPV / companion composite | If we outgrow screen-FPV latency, add without rewriting race core. |

## Latency doctrine

1. **Pilot pixels never leave the phone** after DJI delivers the liveview (decode → project gates → present). No re-encode, no Wi‑Fi to laptop for piloting.
2. Budget overlay pass **&lt; 1 frame @ 30–60 Hz** (aim &lt; 16 ms render). Profile everything.
3. Pose for drawing is **latest telemetry interpolated/extrapolated to “now”**; official passes use **ground-received pose history** with timestamps.
4. Accept imperfect gate registration in loop 1; optimize **feel** (stable rings, clear next gate, loud pass feedback).

## Come-and-fly ground setup (spend money here)

Pilots bring skill; **we** provide:

- Race box (NUC/laptop) + Wi‑Fi AP (private SSID for telemetry/API only — not pilot video)
- Phone preloaded with **GateRace** app + DJI MSDK keys (dev account)
- Mini 4 Pro (+ spares batteries) + RC + phone clamp + sun shade
- Printed / app track map; large **physical cones or flags** optional as real-world hints (virtual gates still authoritative)
- Safety: visual observer, geo awareness, insurance as required locally

Pilot flow: buckle phone → open GateRace → connect aircraft → arm heat on race box → fly rings → land → see time on box + phone.

## System diagram

```
[ Mini 4 Pro ] --OcuSync--> [ RC + Android phone: GateRace app ]
                                | liveview (low latency path)
                                | draws AR gates locally
                                |
                                +-- Wi‑Fi telemetry/events --> [ Race box: authoritative timing ]
                                                                  |
                                                                  +--> spectator RTMP (delayed OK)
                                                                  +--> leaderboard display
```

## Fun over perfection (v1 acceptance)

- Rings may jitter ±1–2 m at distance — OK if still “raceable”
- False pass rate low enough for casual heats; protests rare
- Single pilot timed runs before multi-drone RF management
