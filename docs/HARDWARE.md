# Hardware

Two audiences: **users** (events and practice) first, then **developers**. In each section: must-have vs nice-to-have.

A personal or club phone is enough if it meets the floor below—you don’t need a phone bought only for race day.

---

## A. Users

### Must-have — flight

| Item | Notes | Typical cost if buying |
|------|--------|-------------------------|
| MSDK-supported DJI (or equivalent) aircraft | Confirm support on developer.dji.com; Mini 4 Pro class is the v1 target | ~$800–1100 |
| Phone-centric remote | Prefer no built-in screen so GateRace owns the display | Often in the combo |
| RC ↔ phone USB cable | Official or compatible Lightning / USB‑C / Micro‑USB short cable | Usually included |
| Android phone | Personal or shared; needs working USB link to that RC (OTG as required by the handset) | $0 if you already own one |
| Batteries for the session | Spares recommended | $0–300 |
| Legal compliance | Registration, VLOS, insurance as required locally | Varies |

### Must-have — ground

| Item | Notes | Typical cost if buying |
|------|--------|-------------------------|
| Laptop or small PC | Runs the race box; modest CPU is fine without video encode | Often owned; used ~$400+ |
| Network path phone ↔ laptop | Same Wi‑Fi: hotspot, venue Wi‑Fi, or travel router | $0–150 |
| This repo + Python 3.10+ | Race box software | Free |

With the above you can score heats. TV, streaming, and spare phones are optional.

### Nice-to-have — users

| Item | Why |
|------|-----|
| Travel router | Cleaner private LAN than a phone hotspot |
| Clamp and sun hood | Outdoor readability |
| Spare / club phone | Backup battery or older-device fallback |
| Extra batteries and charger hub | Longer events |
| TV or large monitor | Spectator HLS or leaderboard display |
| `ffmpeg` on the race box | Spectator packaging and optional restream |
| Power station | Sites without mains |
| Cones or flags | Physical hints under virtual gates |
| Standard field kit | Landing pad, LiPo bag, tools |
| Second aircraft | Head-to-head without sharing one airframe |

### Usually skip for v1

Dedicated event-only flagship phones, capture-card OBS rigs, RTK survey gear, cloud VPS for leaderboards—unless you already know you need them.

**Budget sketch:** often under ~$2k if laptop and phone are already owned; more if buying the full aircraft kit from scratch.

### User specs

**Race box**

| | Minimum | Comfortable |
|--|---------|-------------|
| CPU | Dual-core 64-bit | Modern quad-core |
| RAM | 4 GB free for OS + race box | 8–16 GB with spectator encode + browser |
| Disk | ~1 GB free | ~10 GB with logs/clips |
| Software | Python 3.10+, `aiohttp` | + `ffmpeg` for spectator |

Scoring alone is light (tens of MB RAM for the server process in lab). Software video encode is the main laptop load.

**Pilot phone**

| | Minimum (SIM / bench) | Comfortable (MSDK live view) |
|--|----------------------|------------------------------|
| Android | 8+ (app minSdk 26) | 11+ |
| RAM | 3 GB | 6–8 GB+ |
| Class | Older midrange OK for simulator | Mid/flagship ~2021+ for sustained decode + overlay |

**Spectator display:** smart TV browser or laptop with VLC on the same LAN as the race box.

### Smart glasses

Optional experiment, not required. Many USB‑C glasses need DisplayPort Alt Mode; the RC needs a USB data/OTG-style link. See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for how those roles interact on one port.

---

## B. Developers

### Must-have

| Item | Notes |
|------|--------|
| Dev machine | See table below |
| JDK 17, Android SDK, Python 3.10+ | App builds + race box |
| Git and this repository | |
| DJI developer account | When integrating MSDK |

### Nice-to-have

| Item | Why |
|------|-----|
| Hardware virtualization (KVM, etc.) | Usable Android emulator |
| 16–32 GB RAM | Emulator + IDE |
| Physical Android phone | Device tests without emulator RAM cost |
| Supported aircraft | Flight tests |
| Android Studio | Optional; `./gradlew` is enough |

### Developer machine sizes

| | Minimum | Comfortable |
|--|---------|-------------|
| RAM | 8 GB without emulator | 16–32 GB with emulator |
| Disk | ~10 GB | 30 GB+ SDK and system images |
| CPU | 4 cores | 8+ |

You can develop scoring and APIs with Python and `sim/dji_telemetry_mock.py` only.

### Where CPU and RAM go

| Component | Load |
|-----------|------|
| Race scoring / API | Very low |
| Spectator `ffmpeg` | Medium–high on the race box |
| Telemetry mock | Low |
| Android SIM app | Low–medium on device |
| MSDK live view (field) | High on phone GPU / thermals |
| Android emulator | Very high on the dev PC |

---

## Related

[HOW_IT_WORKS.md](HOW_IT_WORKS.md) · [START.md](START.md) · [SPECTATOR.md](SPECTATOR.md)
