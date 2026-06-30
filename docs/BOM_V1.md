# Bill of materials — V1

Prices are approximate USD retail and vary by region. Confirm DJI **MSDK** aircraft support on [developer.dji.com](https://developer.dji.com) before buying aircraft for GateRace.

**Philosophy:** pilots should not need a second “event-only” flagship. Prefer **personal or club-shared** phones that meet [SPECS.md](SPECS.md). Spend first on **aircraft batteries**, a **usable RC path**, and a **boring laptop** as the race box.

---

## 1. User (events & come-and-fly)

### 1.A Mandatory — flight

You cannot run a real GateRace heat without these (or clear equivalents).

| Item | Notes | Est. |
|------|--------|------|
| MSDK-supported DJI aircraft | Mini 4 Pro class preferred; **verify support list** | $800–1100 |
| Compatible RC | Prefer phone-mount / no built-in screen so the app owns the display | often bundled |
| Android phone meeting [min/recommended specs](SPECS.md) | **Personal or club phone is fine** — not a dedicated event purchase | $0 if you already own one |
| Batteries enough for the day | At least one spare | $0–300 |
| Local legal / insurance compliance | VLOS, registration, etc. | varies |

### 1.B Mandatory — ground (race box)

| Item | Notes | Est. |
|------|--------|------|
| Laptop or small PC for race box | See minimum specs in [SPECS.md](SPECS.md); does **not** need a gaming GPU | $0 if you already own one; $400–900 if buying used/refurb |
| Field Wi‑Fi | Phone must reach race box; phone hotspot **or** cheap travel router | $0–150 |
| This software + Python 3.10+ | Race box from this repo | Free |

With only **1.A + 1.B** you can score heats (phone SIM or MSDK telemetry + director UI). No TV, no stream, no spare phone fleet.

### 1.C Nice to have — user / ops

| Item | Why | Est. |
|------|-----|------|
| Travel router / dedicated AP | Cleaner than a phone hotspot; isolates field LAN | $50–150 |
| Extra batteries + charging hub | Longer events | $150–300 |
| Phone clamp + sun hood | Usability outdoors | $30–80 |
| **Spare / club loaner phone** | Backup if someone’s personal phone is low battery or unsupported — **not** “buy flagships for the brand” | used midrange $100–400 |
| Outdoor TV or large monitor | Show HLS spectator POV or leaderboard | $200–500 |
| `ffmpeg` on race box | Spectator HLS + optional internet restream | Free (install) |
| Power station / inverter | Parks without mains | $200–600 |
| Cones / flags under virtual gates | Helps pilots and spectators | $50–150 |
| Landing pad, LiPo bag, prop tools | Standard field kit | $50–100 |
| Prop guards | Training only | $30 |
| Second aircraft | Head-to-head without sharing one airframe | +flight kit |

### 1.D Explicitly optional / later

| Item | Why it’s optional |
|------|-------------------|
| Brand-new flagship phone **dedicated** only to events | Overkill; personal/club midrange that meets specs is enough |
| Capture card + OBS PC | Fallback spectator path if phone RTMP isn’t ready |
| RTK survey gear | Tighter gate placement; large gates reduce need in v1 |
| VPS + domain | Remote leaderboards later |

**Ballpark to start (buy only what you lack):** often **well under $2k** if you already own a laptop and phone; **~$1.5k–3k** if buying aircraft + used ground kit.

---

## 2. Developer (building and testing GateRace)

### 2.A Mandatory — developer

| Item | Notes | Est. |
|------|--------|------|
| Dev machine | See developer minimum in [SPECS.md](SPECS.md) | often already owned |
| JDK 17 + Android SDK | Build the app | Free |
| Python 3.10+ | Race box, mocks, tests | Free |
| Git + this repository | | Free |
| DJI developer account | When integrating MSDK | Free–low |

### 2.B Nice to have — developer

| Item | Why | Est. |
|------|-----|------|
| KVM/virtualisation capable host | Android emulator at usable speed | — |
| 16 GB+ RAM | Emulator + IDE + browser | — |
| Physical Android phone | Real MSDK/device testing without emulator RAM cost | personal phone OK |
| Aircraft on MSDK support list | End-to-end flight tests | see user flight kit |
| Android Studio | Optional; CLI `gradlew` is enough for CI/lab | Free |
| Display for desktop OpenCV sim | Optional visual debugging | — |

### 2.C Not required for development

| Item | Notes |
|------|--------|
| Event TV / travel router | User/event concerns |
| Fleet of event-only phones | Use emulator + one personal device |
| Production stream keys | Only when testing spectator egress |

---

## What not to optimise for in V1

- Injecting overlays into **DJI Goggles** (unsupported for our AR)  
- Forcing the **pilot** to fly off a multi-second livestream or TV  
- Treating a **dedicated flagship phone per pilot** as a hard requirement  

See also [SPECS.md](SPECS.md) for CPU/RAM intensity and [SPECTATOR.md](SPECTATOR.md) for TV/internet POV.
