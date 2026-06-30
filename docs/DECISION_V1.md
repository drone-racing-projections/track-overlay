# Decision record — V1 latency-first AR gate racing

**Date:** 2026-06-30  
**Status:** Accepted for implementation in this repository  

**Priority order**

1. Pilot visual latency (experience must feel good)  
2. Come-and-fly ground operations  
3. Commercial DJI airframe where practical  
4. Accuracy “good enough” for large outdoor gates  

---

## Decisions

| Topic | Choice | Rationale |
|-------|--------|-----------|
| Pilot primary view | Custom **Android app (MSDK V5)** on a phone mounted to the RC (prefer RC *without* a built-in screen so GateRace owns the pixels) | Only practical way to draw **world-locked** rings in the pilot’s eyes on stock DJI without reverse-engineering goggles. |
| Authoritative timing | **Race box** on a field laptop / NUC | Shared clock, logs, leaderboards; phone sends telemetry and soft cues only. |
| Gate scale (v1) | **Large outdoor rings** (~8–15 m diameter, generous thickness) | Consumer GNSS is metres-level; large apertures stay fun when pose is imperfect. |
| Aircraft (v1 target) | **DJI Mini 4 Pro** (confirm current MSDK support) + phone-centric RC | Cost / stability / gimbal balance; Mini 3 Pro as alternate. |
| Where AR is rendered | **On the phone**, on top of MSDK liveview | Any ground hop for *pilot* video adds latency and is rejected for v1 piloting. |
| Spectator video | **Optional delayed path via race box** (RTMP ingest → HLS / egress RTMP) | TV and internet audiences are fine with seconds of delay; must not share the pilot pipeline. |
| Out of scope for pilot path | Stock Fly app, RTMP-only piloting, goggles-only AR | Fly is closed; RTMP latency is too high for piloting; goggles cannot host our overlay. |
| Later extension | Open FPV / companion compositor | Can be added without rewriting the race engine. |

---

## Latency doctrine

1. After DJI delivers liveview frames on the phone, pilot pixels **stay on the phone** (decode → project gates → present). No re-encode and no Wi‑Fi hop for piloting.  
2. Overlay work should fit in **under one frame** at 30–60 Hz (budget on the order of 16 ms). Profile early.  
3. Drawing uses the **latest pose**, optionally extrapolated to “now.” Official passes use **ground-received** pose history with phone-monotonic timestamps.  
4. Accept imperfect registration in loop one; optimise **feel** (stable rings, clear next gate, strong pass feedback).

---

## Clock doctrine

- Telemetry field `t` is **phone-monotonic seconds within a heat** (often starting near zero after Arm).  
- Soft start and splits use **only** that domain.  
- Do not mix Unix wall time or browser `performance.now()` into scoring.  
- The race box may expose wall time for logs (`t_server_wall`) without using it for elapsed race time.

---

## Come-and-fly ground setup

Pilots bring skill; organisers provide:

- Race box (laptop/NUC) + private Wi‑Fi AP for telemetry and spectator ingest  
- Phones preloaded with GateRace + MSDK keys  
- Mini 4 Pro fleet, RC, clamps, sun shades, batteries  
- Track map; optional physical cones/flags aligned with virtual gates  
- Safety: observer, local rules, insurance as required  

Pilot flow: mount phone → open GateRace → connect aircraft → arm heat on race box → fly rings → land → see time on phone and director UI.

---

## System diagram

```
[ Mini 4 Pro ] --OcuSync--> [ RC + Android: GateRace ]
                                | liveview + AR (pilot)
                                |
                                +-- telemetry/events --> [ Race box ]
                                |                           +-- director / leaderboard
                                +-- optional RTMP ---------+-- HLS to TV / LAN
                                                            +-- optional internet RTMP
```

---

## V1 acceptance (fun over perfection)

- Rings may jitter on the order of 1–2 m at distance if the course still feels raceable.  
- False passes rare enough for casual heats.  
- Single-pilot timed runs before multi-aircraft RF management.
