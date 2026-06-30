# Hardware

Two audiences:

1. **User** — running an event or practice (read this section first)  
2. **Developer** — building or testing the software  

In each section: **Must have** vs **Nice to have**.

You do **not** need a phone bought only for this project. A normal personal phone or a club spare is enough if it meets the floor under “Pilot phone.”

---

## Part A — Users

### A1. Must have — flying

| What | Notes | If you don’t have one |
|------|--------|------------------------|
| DJI (or MSDK-supported) aircraft | Target class: Mini 4 Pro. **Check MSDK support** before you buy | ~$800–1100 |
| Controller that works with a phone app | Prefer RC **without** its own screen so GateRace can own the display | Often in the combo |
| Android phone | **Yours or the club’s** — see specs below | $0 if you already own one |
| Batteries for the day | At least one spare is wise | $0–300 |
| Legal to fly there | Registration, VLOS, insurance as required | varies |

### A2. Must have — ground

| What | Notes | If you don’t have one |
|------|--------|------------------------|
| Laptop or small PC | Runs the race box. Weak is fine if you’re not encoding video | Often already owned; used ~$400+ |
| Way for phone to reach laptop | Same Wi‑Fi: phone hotspot, home Wi‑Fi, or a travel router | $0–150 |
| This software + Python 3.10+ | From this repo | Free |

With **A1 + A2** you can score heats (telemetry + director UI). No TV, no stream, no extra phones.

### A3. Nice to have — users

| What | Why |
|------|-----|
| Travel router | Cleaner than hotspot; private field network |
| Phone clamp + sun hood | Outdoor flying |
| Club/spare phone | Backup battery or if someone’s phone is too old for MSDK — **not** “buy flagships for the brand” |
| Extra batteries / hub | Longer days |
| TV or big monitor | Show spectator video or leaderboard |
| `ffmpeg` on the laptop | Required only for spectator HLS / restream |
| Power station | Sites without mains |
| Cones / flags under virtual gates | Helps humans see the course |
| Landing pad, LiPo bag, tools | Normal field kit |
| Second aircraft | Head-to-head without sharing one airframe |

### A4. Skip unless you know you need it

- Brand-new **event-only** flagship phone  
- Capture card + OBS (fallback if phone can’t RTMP yet)  
- RTK survey gear (large gates reduce the need in v1)  
- Server in the cloud (only for remote leaderboards later)  

**Rough money:** often under **$2k** if you already own laptop + phone; more if you’re buying the aircraft kit from zero.

### User specs (minimum → comfortable)

**Race box laptop**

| | Minimum | Comfortable |
|--|---------|-------------|
| CPU | Dual-core 64-bit | Quad-core modern laptop/NUC |
| RAM | 4 GB free for OS + race box only | 8–16 GB if spectator encode + browser |
| Disk | 1 GB free | 10 GB if you keep clips/logs |
| Software | Python 3.10+, `aiohttp` | + `ffmpeg` for spectator |

Scoring alone is light (~40 MB RAM for the race box process in lab). **Video encode** is what stresses the laptop.

**Pilot phone**

| | Minimum (app SIM / bench) | Comfortable (real DJI video later) |
|--|---------------------------|-------------------------------------|
| Android | 8+ (`minSdk` 26) | 11+ |
| RAM | 3 GB | 6–8 GB+ |
| Device class | Older midrange OK for simulator | Mid/flagship ~2021+ for sustained liveview + overlay |
| Role | Personal or club phone | Same |

**Spectator display:** any smart TV browser or laptop with VLC on the **same LAN** as the race box.

---

## Part B — Developers

### B1. Must have

| What | Notes |
|------|--------|
| Normal dev computer | See table below |
| JDK 17, Android SDK, Python 3.10+ | Build app + run race box |
| Git + this repo | |
| DJI developer account | Only when you plug in MSDK |

### B2. Nice to have

| What | Why |
|------|-----|
| KVM / Hypervisor | Emulator usable |
| 16–32 GB RAM | Emulator + IDE |
| Physical Android phone | Test without multi‑GB emulator |
| Real supported aircraft | Flight tests |
| Android Studio | Optional; `./gradlew` is enough |

### B3. Developer machine sizes

| | Minimum | Comfortable |
|--|---------|-------------|
| RAM | 8 GB (no emulator) | 16–32 GB with emulator |
| Disk | ~10 GB | 30 GB+ SDK + images |
| CPU | 4 cores | 8+ |
| Emulator | Optional | Expect **several GB RAM** and high CPU — lab sample ~3.5 GB for a 3 GB AVD |

You can develop scoring and API with **only** Python + `sim/dji_telemetry_mock.py` — no Android install.

---

## What uses the CPU (so you know where pain is)

| Software | Load | Comment |
|----------|------|---------|
| Race scoring / API | Very low | Not your bottleneck |
| Spectator `ffmpeg` | Medium–high | Main ground cost if streaming |
| Telemetry mock | Low | |
| Android SIM app | Low–medium | |
| Future MSDK liveview | High on **phone** GPU | Thermals matter |
| Android emulator | Very high on **dev PC** | Event site doesn’t need this |

Lab integrated checks (scoring, mock heats, spectator demo HLS, emulator heat after app fix) are summarized in git history / prior runs; treat phone MSDK load as **unmeasured on real aircraft** until you fly.

---

## Related

- Concepts: [HOW_IT_WORKS.md](HOW_IT_WORKS.md)  
- Run software: [START.md](START.md)  
- Spectator wiring: [SPECTATOR.md](SPECTATOR.md)  
