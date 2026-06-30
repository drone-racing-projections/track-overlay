# Hardware intensity & recommended specs

Measurements below mix **lab samples from this environment** (2026-06-30 integrated run on a 16-thread host with KVM) with **engineering estimates** for field phones and aircraft. Treat numbers as order-of-magnitude guides, not certifications.

## Integrated test results (lab)

| Step | Result | Notes |
|------|--------|--------|
| Race box health | Pass | Idle ~35–40 MB RSS |
| Unit pass detection | Pass | ~45 ms CPU-bound on one core |
| API + multi-speed telemetry mock | Pass | ~2.4 s wall (network + 9 full heats in regression) |
| Spectator demo → HLS | Pass | ffmpeg ~126 MB RSS while packaging 1280×720 demo |
| Android emulator full heat | Pass when AVD + APK running | Emulator itself is the heavy part (~3–4 GB with 3 GB guest RAM) |

**Not measured on real Mini 4 Pro / MSDK** in this lab: pilot overlay GPU load on a physical phone, OcuSync, or battery draw.

---

## Intensity by component

| Component | CPU | RAM | GPU | Network | Storage | Notes |
|-----------|-----|-----|-----|---------|---------|--------|
| `track_core` pass / race logic | Very low | &lt; 50 MB | None | None | None | Pure Python maths; fine on any laptop |
| Race box HTTP/WS API | Very low | ~40 MB idle | None | Low (telemetry JSON) | Tiny (heat logs) | Dominated by idle interpreter |
| Spectator relay (`ffmpeg` HLS) | **Medium–high** | ~100–250 MB | None (software encode default) | Medium (video) | Burst for segments | Heaviest **ground** process if streaming |
| Host DJI telemetry mock | Low | &lt; 50 MB | None | Low | None | One core at a few percent |
| Desktop OpenCV sim | Low–medium | ~100–200 MB | Optional | None | None | GUI path needs a display |
| GateRace Android **SIM** (Canvas) | Low–medium | App tens of MB | Light GPU | Low (telemetry) | Small | Not representative of MSDK liveview |
| GateRace **MSDK** (field target) | **Medium–high** | 200 MB–1 GB+ | **High** (decode + overlay) | Low telemetry + optional RTMP | Cache/video buffers | Phone must handle liveview; do **not** use a worn-out budget handset for MSDK |
| Android **emulator** (dev only) | **Very high** | **3–8 GB** | Host GPU or SwiftShader | Low | Multi-GB SDK | Never needed at an event |
| Aircraft + RC (DJI) | Vendor | Vendor | Vendor | OcuSync RF | — | Not part of this repo’s CPU budget |

---

## Minimum vs recommended specs

### User — race box (field laptop / NUC)

| | Minimum | Recommended |
|--|---------|-------------|
| CPU | Dual-core 64-bit, 1.5 GHz+ (any recent Intel/AMD/Apple) | Quad-core, modern laptop/NUC |
| RAM | **4 GB** free for OS + race box only | **8–16 GB** if spectator HLS + browser director + Wi‑Fi tools |
| Storage | 1 GB free | 10 GB+ if recording segments / logs |
| OS | Linux, Windows, or macOS with Python 3.10+ | Linux or Windows for simplest `ffmpeg` ops |
| Network | Wi‑Fi or Ethernet to a small AP | Dedicated travel router; race box on Ethernet to AP if possible |
| Software | Python 3.10+, `aiohttp` | + `ffmpeg` when using spectator TV/internet |

Race box **without** spectator is intentionally light. Turning on **software-encoded HLS** is the main ground-side cost (one `ffmpeg` process).

### User — spectator display (TV / spare laptop)

| | Minimum | Recommended |
|--|---------|-------------|
| Device | Any smart TV browser or laptop with VLC/HLS | Wired Ethernet to AP; 1080p TV |
| Network | Same LAN as race box | 5 GHz Wi‑Fi or Ethernet; avoid guest isolation |

### User — pilot phone (RC mount)

**You do not need a phone bought only for events.** Use a normal personal phone that meets the floor below, or a **shared club phone** reused across events—not a second “fleet of dedicated flagships” as a requirement.

| | Minimum (SIM / bench) | Recommended (MSDK field) |
|--|----------------------|---------------------------|
| OS | Android 8+ (app `minSdk` 26) | Android 11+ with current security patches |
| SoC / GPU | Any 2019+ midrange for **SIM only** | Mid/flagship from ~2021+ with reliable sustained GPU (Pixel 6-class, Galaxy S21-class, or similar—**not** the cheapest Go edition) |
| RAM | 3 GB | **6–8 GB+** for MSDK liveview + overlay |
| Display | 720p | 1080p+, 90/120 Hz helps feel |
| Role | Personal phone or club loaner | Same—**dedicated spare** is nice, not mandatory |

If MSDK on a given handset is janky, upgrade *that* phone or use a club spare—don’t budget “one new flagship per pilot per season” as mandatory.

### User — aircraft / RC

| | Minimum | Recommended |
|--|---------|-------------|
| Aircraft | MSDK-supported DJI in Mini/Air class (confirm list) | Mini 4 Pro (or current supported equivalent) |
| RC | Works with phone app / MSDK | RC **without** built-in screen so GateRace owns pixels (or accept using the phone beside a screen RC) |
| Batteries | Enough for practice | Fly More + charging at the field |

### Developer — workstation

| | Minimum | Recommended |
|--|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | **8 GB** (no emulator) | **16–32 GB** with Android emulator |
| Disk | 10 GB | **30 GB+** for Android SDK + system images |
| KVM / HVF / HAXM | Optional | **Required** for a usable emulator |
| GPU | Integrated | Discrete or solid integrated for emulator + desktop sim |
| Software | JDK 17, Android SDK 34, Python 3.10+ | + Android Studio optional; `ffmpeg` for spectator tests |

Emulator with 3 GB guest RAM used **~3.5 GB host RSS** in lab (SwiftShader, headless). Plan RAM accordingly.

---

## Practical guidance

1. **Events:** prioritise one reliable midrange phone (personal or club) and a modest laptop with `ffmpeg` only if you want TV/internet POV.  
2. **Scoring-only days:** race box + telemetry mock or phone telemetry; skip spectator and emulator entirely.  
3. **Dev loops:** use host `dji_telemetry_mock.py` when you don’t need UI; use emulator when testing Android; reserve real MSDK for periodic device checks.  
4. **Bottlenecks to expect:** (a) phone GPU/thermal under liveview, (b) `ffmpeg` CPU on race box during HLS, (c) emulator RAM on laptops—not the Python race engine.
