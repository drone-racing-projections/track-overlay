# Drone Track Overlay — Research & Architecture Options

**Working title:** AR gate / ring checkpoints overlaid on a live drone camera feed; pilots race through a virtual course; fastest full clear wins.

**Status:** Options for product/architecture choice (not a final committed design).

---

## 1. Product definition

### What the pilot experiences
- Live camera video (FPV-style or controller screen).
- **Virtual gates/rings** rendered in 3D as if fixed in the world (not stuck to the HUD).
- Each gate is a **checkpoint** with order, optional time penalties, start/finish.
- Timing, lap/sector times, leaderboard for multi-pilot events.
- Pass detection: when the drone’s pose is “through” the gate aperture within tolerance.

### What is *not* required for v1
- Physical inflatable gates (optional later for hybrid events).
- Fully autonomous gate navigation (pilot still flies).
- Cloud multiplayer at global scale (local/LAN race is enough for MVP).

### Core technical problem
Gates must sit in **world coordinates** and be projected into the **camera image** each frame using:
- Drone **position** (and preferably orientation),
- Camera **intrinsics** + **extrinsics** (gimbal / fixed FPV offset),
- Low enough **end-to-end latency** that gates don’t “swim” or lag dangerously.

That is a **video + pose + real-time 3D overlay** system, not “draw circles on a HUD.”

---

## 2. Constraints from commercial ecosystems (research summary)

### Consumer / prosumer DJI (Mini, Air, Mavic, Avata with Fly app)
- **Mobile SDK (MSDK) V5** on Android/iOS: live video frames, flight telemetry (position, attitude where exposed), RTMP/RTSP/Agora **outbound** livestream.
- Overlay is realistic **on the phone/tablet** that runs a custom DJI Fly–like app (replace or sit beside official app — licensing and supported aircraft list matter).
- **RTMP/RTSP livestream** often adds **high latency** (seconds in bad setups; often hundreds of ms+ even when “good”). **Unsuitable as the only path for piloting overlays.**
- Official Fly app is **closed**: you cannot inject AR into stock Fly without a custom MSDK app on a supported RC/phone setup.

### DJI digital FPV (O3 / Avata / Goggles / Air Unit)
- Excellent **low latency** (~28–40 ms class digital links depending on mode).
- Video path is largely **closed** inside goggles / Air Unit; **no public API to inject custom 3D overlays into the goggles framebuffer**.
- Practical overlays for FPV usually require **intercepting video elsewhere** (HDMI out from goggles if available, secondary RX, or **not using goggles as the overlay surface**).

### Open FPV stack (Betaflight / iNav + analog / HDZero / Walksnail)
- Full control of OSD / companion computer overlays.
- Gates as world-locked AR still need **pose** (GPS + attitude, or vision, or external tracking).
- More electronics and tuning; less “buy a DJI and go.”

### Positioning quality
| Source | Typical use | Gate accuracy (ballpark) |
|--------|-------------|---------------------------|
| Consumer GPS/GNSS on DJI | Outdoor | meters-level; OK for large gates (4–10 m) |
| RTK / RTK-capable enterprise | Survey-style | cm–dm; tight gates |
| Visual-inertial / SLAM on companion | GPS-denied / precision | depends on lighting/scene |
| External (motion capture / UWB anchors) | Arena / indoor | cm; heavy infrastructure |

**Implication:** v1 outdoor racing with **large virtual gates** + consumer GNSS is credible. Indoor tight tracks need tracking upgrades.

### Latency budget (rule of thumb)
| Segment | Target (pilotable AR) |
|---------|------------------------|
| Air link video | 30–80 ms (digital FPV) or higher on consumer OcuSync + phone |
| Decode + AR render + composite | **&lt; 16–33 ms** on device (1–2 frames @ 60 Hz) |
| Pose age vs video frame | Must be **time-aligned** or gates jitter |

If overlay path adds **&gt; ~100–150 ms** on top of the flight video the pilot trusts, the product feels wrong and can be unsafe for high-speed flight.

---

## 3. Shared logical architecture (all options)

Regardless of hardware, the system decomposes into the same services:

```
┌─────────────┐     pose + time      ┌──────────────────┐
│  Drone /    │ ───────────────────► │  Pose service    │
│  sensors    │                      │  (filter, sync)  │
└──────┬──────┘                      └────────┬─────────┘
       │ video frames                          │
       ▼                                       ▼
┌─────────────┐     camera model     ┌──────────────────┐
│  Video      │ ───────────────────► │  Track renderer  │
│  ingest     │                      │  (gates in 3D →  │
└─────────────┘                      │   2D overlay)    │
                                     └────────┬─────────┘
                                              │ composited frames
                                              ▼
                                     ┌──────────────────┐
                                     │  Display / TX    │
                                     │  (RC, phone,     │
                                     │   goggles HDMI,  │
                                     │   race director) │
                                     └────────┬─────────┘
                                              │
                                     ┌────────▼─────────┐
                                     │  Race engine     │
                                     │  (gates, timing, │
                                     │   leaderboard)   │
                                     └──────────────────┘
```

**Modules to build (software):**
1. **Track definition** — gates as pose + radius/width/height + sequence + metadata (JSON/YAML); editor (map or in-field “fly to place gate”).
2. **Pose pipeline** — GNSS + attitude (+ baro); optional fusion; timestamping.
3. **Camera model** — FOV, principal point, distortion; gimbal angles for gimballed cams; fixed mount for FPV.
4. **Overlay renderer** — OpenGL/Metal/Vulkan or engine (Unity/Unreal/Godot); transparent gate meshes, depth optional; occlusion later.
5. **Pass detector** — plane intersection + cylinder/torus volume; debounce; false-pass rejection (wrong direction).
6. **Race engine** — arm, start, checkpoint order, DNF, multi-drone sessions, anti-cheat (min times, geo-fence).
7. **Ops UI** — race director tablet; spectator stream (can be high-latency RTMP — spectators tolerate delay pilots cannot).

**Electronics you will likely add (even with DJI):**
- Companion computer **or** powerful phone/RC that runs the custom app (MSDK path).
- Optional: RTK module / NTRIP if you need tighter gates.
- Optional: secondary video path (HDMI grabber, WiFi display) for spectator/AR on non-pilot screens.
- Optional: LED / audio feedback on ground for pass confirmation (UX, not required for timing).

---

## 4. Architecture options (choose one primary path)

### Option A — **Custom DJI Mobile SDK app (phone / RC-as-phone)**  
**“Commercial DJI + software-heavy; minimal custom air electronics”**

| | |
|--|--|
| **Air** | Stock supported DJI (e.g. Mini 4 Pro, Air 3, Avata 2 — **verify MSDK support matrix** before buying) |
| **Pilot display** | Android phone on RC, or RC with open Android (where supported) running **your app** |
| **Video** | MSDK live video callback → decode → AR composite → full-screen preview |
| **Pose** | MSDK telemetry (GPS, attitude, gimbal) |
| **Extra electronics** | Minimal: good phone, mounts, maybe external battery / cooling |

**Pros**
- Highest leverage of commercial airframe + radio.
- Overlay on the **same screen the pilot already uses** (if they accept not using stock Fly).
- Fastest path to a demo with **one developer + one drone**.
- Live stream **to spectators** can still use RTMP **from the app after overlay** (delay OK for audience).

**Cons**
- Aircraft/RC **support limited** by DJI’s MSDK list; Avata/FPV goggles pilots may not get goggles AR.
- Must maintain Android (and optionally iOS) app + DJI SDK upgrades.
- Latency = OcuSync/phone decode + your render (usually acceptable for **cinematic / large-gate** racing, not full Multirotor League tight FPV).
- Legal/compliance: custom flight apps may face app store and local UAV rules; geofencing remains DJI’s.

**Best for:** Outdoor “AR racing league” with **prosumer camera drones**, large gates, phone/RC screen as primary view.

**Add-on electronics (optional):** RTK if available on platform; Raspberry Pi / mini PC on ground for race server only.

---

### Option B — **Ground “video + telemetry” compositor (HDMI / capture)**  
**“Keep stock Fly or goggles for control; AR on a parallel display or injected via capture”**

| | |
|--|--|
| **Air** | Stock DJI or FPV |
| **Pilot primary** | Stock Fly **or** goggles (**unmodified**) |
| **AR path** | Capture video (USB-C DisplayPort / HDMI out from RC or goggles, or wireless screen mirror) + ingest telemetry (MSDK secondary device, or Onboard/Cloud API where available, or MAVLink bridge on open stacks) → PC/Jetson composites AR → show on **second screen** or record |
| **Extra electronics** | Capture card, laptop/Jetson, maybe USB telemetry dongle / second phone running MSDK “telemetry only” |

**Pros**
- Pilot can keep **familiar stock UI** for actual flying (safety / muscle memory).
- Heavy rendering on a **ground GPU** (Unity/Unreal on laptop).
- Good for **race director, spectators, coaching**, and post-run review.
- Can evolve into “AR only on director screen” while pilots fly physical gates — product pivot possible.

**Cons**
- **Dual view problem:** if AR is only on the second screen, the pilot isn’t racing *through* the rings in their primary vision — undermines the core fantasy unless you force the pilot to fly looking at the AR monitor (awkward, higher risk).
- Capture + PC path often **adds latency**; hard to use as primary FPV.
- Syncing telemetry timestamps to captured video frames is non-trivial.

**Best for:** Broadcast / event production, training, hybrid events; **weak** as the only path for “pilot sees rings while racing” unless the AR monitor **is** the primary view (then similar latency concerns to A).

---

### Option C — **Open FPV racing stack + companion computer (on-aircraft overlay)**  
**“Real racing latency; maximum electronics; not a stock DJI camera drone”**

| | |
|--|--|
| **Air** | Custom 5" class (or similar) + HDZero / Walksnail / analog + Betaflight/iNav |
| **Companion** | Raspberry Pi 5 / Orange Pi / Radxa / small Jetson on airframe **or** on ground with low-latency digital RX |
| **Overlay** | Render gates on companion; composite into video **before** VTX, **or** OSD-like graphics in goggles ecosystem where supported |
| **Pose** | GPS+compass on FC, or external module; optional UWB/RTK |

**Pros**
- Latency can approach **true FPV racing**.
- Full ownership of video pipeline.
- Aligns with existing **drone racing culture** (MultiGP-style events with virtual gates as augmentation).

**Cons**
- **Not** “mostly commercial DJI”; significant build, tune, fail-safe, and regulatory burden.
- Safety and reliability work dominates the project.
- Harder for casual pilots.

**Best for:** Serious FPV racing product / league tech; R&D that prioritizes feel over convenience.

---

### Option D — **Hybrid “DJI Avata / O3 for flight feel + MSDK/ground AR for scoring” + physical or large virtual gates**  
**“Pragmatic event system”**

| | |
|--|--|
| **Pilot fly** | Avata / O3 goggles (stock, low latency) |
| **Scoring / rings** | Either (1) **large virtual gates** judged by **telemetry only** (no need to see rings perfectly), with optional AR on **ground screens**, or (2) **physical gates** + telemetry backup |
| **AR rings for pilots** | Simplified: LED on HUD / audio cue / coarse ring on a **phone mounted in peripheral vision** — not full world-locked in goggles |

**Pros**
- Uses best commercial FPV **feel** from DJI.
- Race timing can be **telemetry-accurate** even if goggles can’t show perfect AR.
- Faster to run real events.

**Cons**
- **Splits the fantasy:** pilot may not see the same beautiful rings in goggles.
- Product messaging must be careful (“telemetry race with spectator AR” vs “full AR FPV”).

**Best for:** Events and MVP scoring; weaker if the **core demo** must be “rings in the pilot’s video.”

---

### Option E — **Enterprise / SDK-forward DJI (Matrice / with Onboard or richer APIs) + RTK**  
**“Precision + budget”**

| | |
|--|--|
| **Air** | Enterprise platforms with better SDK/payload options and RTK |
| **Overlay** | MSDK and/or onboard computer with payload HDMI / network stream |
| **Pose** | RTK centimeter-class |

**Pros**
- Best **gate precision** and professional positioning.
- More legitimate for industrial demo / paid pilots.

**Cons**
- Cost (airframe + RTK + batteries) much higher.
- Still may not solve **goggles** overlay; often tablet/RC centric.

**Best for:** High-precision outdoor tracks, commercial clients, research.

---

## 5. Comparison matrix

| Criterion | A MSDK app | B Ground compositor | C Open FPV + companion | D Hybrid Avata + telemetry | E Enterprise + RTK |
|-----------|------------|---------------------|-------------------------|----------------------------|--------------------|
| Use stock DJI airframe | **High** | **High** | Low | **High (Avata)** | Enterprise DJI |
| Pilot sees world-locked rings | **Yes** (on app screen) | Only if AR is primary view | **Yes** (if in video path) | **Weak** in goggles | **Yes** on RC/tablet |
| Latency for racing feel | Medium | Medium–poor | **Best** | **Best** fly / weak AR | Medium |
| Extra electronics | Low | Medium | **High** | Low–medium | Medium–high |
| Cost to first demo | **Lowest** | Medium | High | Medium | **Highest** |
| Multi-drone race ops | Good (app + server) | Good (ground PC) | Good | Good | Good |
| Indoor / tight gates | Poor without add-ons | Poor | Medium–good with tracking | Poor | Better with RTK/mocap |
| Alignment with “DJI + a bit of electronics” | **Best** | Good | Poor | Good | OK if budget allows |

---

## 6. Recommended default (if forced to pick)

For a **serious project that still prioritizes commercial DJI** and the **pilot actually seeing rings**:

1. **Primary: Option A (MSDK app)** for the core product fantasy and development speed.  
2. **Race backend** shared (track files, timing, leaderboard) so you can later add **Option B** spectator/director views without rewrite.  
3. Revisit **Option C or D** only if user research says “must be goggles FPV latency.”

That yields an architecture that is **software-defined track + commercial drone + one custom app + small race server**, with optional ground electronics for events.

---

## 7. Cross-cutting design decisions (later, after option choice)

- **Gate size vs GNSS noise** — design gates so pass detection is robust (e.g. 5–15 m diameter outdoors without RTK).
- **Coordinate frame** — WGS84 → local ENU tangent plane at track origin; all gates in ENU meters.
- **Time sync** — monotonic timestamps on video frames and telemetry; interpolate pose to frame time.
- **Safety** — geofence, max speed, lost-link behavior remain on DJI; AR must never be the only attitude reference; clear “demo vs race” modes.
- **Anti-cheat** — server-side pass validation from telemetry; optional video audit trail.
- **Simulation** — desktop replay with recorded telemetry + video; integrate with existing `/work/pi-sim` only for companion-electronics R&D if Option C.

---

## 8. Rough MVP scope (Option A shaped)

1. Track JSON + simple editor (lat/lon/alt gates).  
2. Android MSDK app: video + pose + OpenGL gates + pass beep/UI.  
3. Single-pilot timed run; local leaderboard.  
4. Export spectator RTMP (delayed OK).  
5. Field test protocol: measure overlay latency and pass false positive/negative rates.

---

## 9. Open questions for stakeholders

1. Primary pilot display: **phone/RC screen** vs **FPV goggles**?  
2. Environment: **outdoor GNSS** vs indoor?  
3. Gate scale: **large AR gates** vs tight racing gates?  
4. Single-drone MVP vs **multi-drone** from day one?  
5. Budget tier: prosumer (~$1–3k air) vs enterprise?

---

*Document generated for architecture selection. Implementation design doc should follow once an option is chosen.*
