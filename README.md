# Track Overlay (GateRace)

**Virtual racing gates on a real drone feed** — world-locked rings on the pilot’s live view, authoritative timing on a field laptop, optional **spectator POV** to a TV or the internet.

Part of [Drone Racing Projections](https://github.com/drone-racing-projections). This repository implements the **latency-first** stack: commercial DJI airframe, custom Android app for the pilot display, ground **race box** for scoring and spectator distribution.

| Priority | Principle |
|----------|-----------|
| 1 | Pilot visuals must feel instant (fun or nothing) |
| 2 | Come-and-fly ops — complex setup is OK if pilots only fly |
| 3 | Stock / prosumer DJI where possible (Mini 4 Pro class + MSDK) |
| 4 | Large outdoor gates that tolerate consumer GNSS |

---

## How it fits together

```
 Mini 4 Pro ──OcuSync──► RC + Android phone (GateRace app)
                              │  liveview + AR gates (pilot path, stays on phone)
                              │
                              ├── Wi‑Fi telemetry (10–20 Hz) ──► Race box (timing, leaderboard)
                              │
                              └── optional RTMP (delayed) ──► Race box spectator relay
                                                              ├── HLS → TV / LAN browsers
                                                              └── optional RTMP egress → internet
```

**Pilot path:** decode DJI liveview on the phone → project gates → show the pilot. Video for flying **never** routes through the laptop.

**Race box:** authoritative pass detection, heat control, director UI, heat logs, and **spectator** ingest/restream.

**Spectator path:** secondary, delayed on purpose. Safe for a sideline TV or Twitch/YouTube; unsuitable for piloting.

---

## Repository map

| Path | Role |
|------|------|
| `track_core/` | Track geometry (ENU), projection math, pass detection, race engine |
| `tracks/` | Track JSON (e.g. `demo_field.json`) |
| `race_box/` | Ground station HTTP/WebSocket API, director UI, spectator relay |
| `android/` | GateRace app (SIM overlay today; MSDK for field) |
| `sim/` | Desktop visual sim + host DJI-style telemetry mock |
| `docs/` | Decisions, API, BOM, spectator guide |
| `scripts/` | Tests and environment setup |

---

## Quick start

### Race box (ground station)

```bash
cd track-overlay
pip install aiohttp          # if needed
# optional spectator relay:
# sudo apt install ffmpeg

PYTHONPATH=. python3 race_box/server.py
```

- Director UI: <http://127.0.0.1:8088/>
- API overview: [docs/PHONE_API.md](docs/PHONE_API.md)
- Spectator: [docs/SPECTATOR.md](docs/SPECTATOR.md)

Arm a heat, watch the leaderboard, and (with `ffmpeg` installed) start a **demo** spectator stream from the director panel to verify TV/LAN playback.

### Unit / API checks

```bash
PYTHONPATH=. python3 scripts/test_pass_detect.py
PYTHONPATH=. python3 scripts/test_api_and_mock.py   # race box must be running
```

### Host telemetry mock (no phone)

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

Posts ENU telemetry as if an MSDK phone were flying the demo track. Use **either** this **or** the Android SIM app for a given heat—not both.

### Android SIM app

```bash
export ANDROID_HOME=/opt/android-sdk   # or your SDK path
cd android && ./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

On the **emulator**, the default race box URL is `http://10.0.2.2:8088`. On a **physical phone**, set the laptop’s LAN IP in the app URL field.

KVM makes the emulator practical. After a clean machine/container: `scripts/setup_android_env.sh`.

### Desktop overlay sim (optional GUI)

Needs a display and `numpy` + OpenCV:

```bash
pip install numpy opencv-python-headless   # or opencv-python with GUI
PYTHONPATH=. python3 sim/desktop_sim.py
```

Controls: W/S speed · A/D yaw · R/F up/down · Q/E camera pitch · Esc quit.

---

## Design notes

- Locked product/architecture choices: [docs/DECISION_V1.md](docs/DECISION_V1.md)
- Research options considered: [ARCHITECTURE_OPTIONS.md](ARCHITECTURE_OPTIONS.md)
- Hardware budget (user vs developer, mandatory vs nice-to-have): [docs/BOM_V1.md](docs/BOM_V1.md)
- Intensity & min/recommended specs: [docs/SPECS.md](docs/SPECS.md)
- Clock policy: heat time `t` is **phone-monotonic** within a heat (see API doc)—never mix with browser `performance.now()` or wall clocks for scoring.

Optional field API token: set `GATERACE_TOKEN` on the race box process.

---

## Field roadmap

1. DJI MSDK V5 app key + liveview surface under the gate overlay  
2. Phone → race box telemetry at 10–20 Hz; local render uses latest pose  
3. Phone → race box **spectator RTMP** (low bitrate), director HLS to TV  
4. Clap / LED latency calibration on the pilot path  
5. Real-world cones as optional hints under virtual gates  

---

## Safety

Experimental software. Follow local UAV regulations, VLOS, and insurance requirements. AR overlays are **not** a substitute for attitude awareness. Aircraft geofencing and failsafes remain DJI’s responsibility.

## License

See [LICENSE](LICENSE).
