# How Track Overlay works

Read this first. No API tables — just the idea.

## What we’re building

Pilots fly a normal consumer drone (target: something like a **DJI Mini 4 Pro**). On the phone attached to the controller they see the live camera **plus** virtual rings floating in the real world. They fly through rings in order. Fastest clean run wins.

We call the app **GateRace**. The laptop on site is the **race box** (ground station).

## Two jobs that must not be mixed

### 1. Pilot view (must be fast)

The phone:

1. Gets live video from the drone (via DJI’s link / MSDK).
2. Draws the gates on top using the latest position.
3. Shows that to the pilot.

That path **must not** go: phone → Wi‑Fi → laptop → back to phone. That adds lag and kills the fun.

### 2. Official timing (must be fair)

The phone sends **small telemetry packets** (position, time, attitude) to the race box over field Wi‑Fi, about 10–20 times per second.

The race box decides when a gate was passed and what the official time is. Everyone trusts the laptop, not each phone’s stopwatch.

### 3. Spectator video (optional, allowed to be slow)

People by a TV — or on the internet — can watch a **delayed** copy of the feed. That **can** go through the race box (ingest video → play on LAN or restream online). Seconds of delay are fine. Pilots must **not** fly off that picture.

## Pieces of software

| Piece | Runs on | Does |
|-------|---------|------|
| **GateRace app** | Pilot’s Android phone | Live view + AR gates; sends telemetry; later may push delayed RTMP for spectators |
| **Race box** (`race_box/`) | Field laptop | Arms heats, scores passes, leaderboard, director web page, optional video relay |
| **Track files** (`tracks/`) | Shared | Where gates are in the world (metres from a GPS origin) |
| **track_core** | Inside race box & tools | Shared logic: geometry, “did they pass the gate?”, race state |
| **sim/** | Your laptop | Fake flights for testing without a drone |

Today the Android app runs in **SIM mode** (fake flight + drawn horizon). Real DJI video needs the Mobile SDK and an app key — not finished yet, but the race box and scoring already work.

## Coordinates in one sentence

We pick a GPS origin for the field. Everything else (gates, drone) is in **metres east / north / up** from that point (ENU). The phone converts GPS → ENU before talking to the race box.

## Time in one sentence

Heat time `t` is **seconds on the phone’s clock during that heat** (usually starting near zero after Arm). Scoring only uses that. Don’t mix in “wall clock” or browser timers.

## One heat, one telemetry source

Arm a heat with a `pilot_id`. Only that pilot’s telemetry counts. When the heat finishes, send nothing more until you Arm again. Don’t run the phone app **and** the laptop telemetry mock against the same heat.

## What “good enough” means for v1

Gates are **big** (roughly 8–15 m across) so normal GPS noise still lets people race. Rings may drift a bit. Fun first; survey-grade accuracy later if we care.

## Decisions we already locked

These aren’t open debates in this repo anymore:

1. Pilot AR on the **phone** (DJI MSDK path), not in goggles, not via livestream.
2. **Race box** is authoritative for time.
3. **Large outdoor** gates for v1.
4. Spectator video is **optional and delayed**, owned by the race box when we redistribute it.

Background alternatives we considered: [RESEARCH.md](RESEARCH.md).

## Where to go next

- Run something: [START.md](START.md)  
- Buy / borrow gear: [HARDWARE.md](HARDWARE.md)  
- Implement against the API: [API.md](API.md)  
- TV / stream: [SPECTATOR.md](SPECTATOR.md)  
