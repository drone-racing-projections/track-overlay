# GateRace — AR drone track overlay (latency-first)

World-locked **racing gates/rings** on a **DJI** live view. Pilots race checkpoints; **fastest clean run wins**.

## Priority

1. **Low latency visuals** (fun or nothing)  
2. **Come-and-fly** ground ops (complex setup OK if pilots just fly)  
3. **Commercial DJI** airframe (Mini 4 Pro class + MSDK app on phone)  
4. Large outdoor gates first (GNSS-tolerant)

See [docs/DECISION_V1.md](docs/DECISION_V1.md) and [docs/BOM_V1.md](docs/BOM_V1.md).

## Architecture (v1)

- **Phone (GateRace Android / MSDK):** decode DJI liveview → draw gates → show pilot. **Never** send pilot video through the laptop.
- **Race box (this repo, laptop on field Wi‑Fi):** authoritative pass detection & timing from telemetry JSON.
- **Spectator video (optional):** delayed RTMP from phone — not for piloting.

## Repo status

| Piece | Status |
|-------|--------|
| Track format + ENU geo | Done (`track_core`, `tracks/demo_field.json`) |
| Pass detection + race engine | Done |
| Ground race box HTTP API | Done (`race_box/server.py`) |
| Desktop overlay sim | Done (`sim/desktop_sim.py`) |
| Android MSDK GateRace app | **Next** (needs DJI key + device) |

## Quick start (software now)

```bash
cd /work/drone-track-overlay
PYTHONPATH=. python3 scripts/test_pass_detect.py

# Race box
PYTHONPATH=. python3 race_box/server.py
# curl -X POST http://127.0.0.1:8088/session/arm -d '{"track":"demo_field"}'

# Visual sim (needs display — see /work/DISPLAY.md)
PYTHONPATH=. python3 sim/desktop_sim.py
```

### Sim controls

W/S speed · A/D yaw · R/F up/down · Q/E camera pitch · ESC quit

## Hardware to buy (summary)

See **docs/BOM_V1.md**. Minimum roll-out: Mini 4 Pro + phone RC path + strong Android phone + field laptop + travel router ≈ **$2–3.5k**.

Register at [developer.dji.com](https://developer.dji.com), create MSDK app key for your package name.

## Next engineering steps

1. Android app skeleton from [MSDK V5 sample](https://github.com/dji-sdk/Mobile-SDK-Android-V5): video surface + pose → port `project.py` math to Kotlin/OpenGL.  
2. Phone posts `/telemetry` at 10–20 Hz to race box; local render uses latest pose.  
3. Field calibration: measure phone overlay latency (clap test / LED).  
4. Place real-world cones under virtual gates for v1 fun.

## Hardening (lab)

- Telemetry validation (400), heat ownership + finished lock (409)
- Phone-monotonic clock only; soft start requires `t`
- Heat log: `race_box/logs/heats.jsonl` · `GET /leaderboard` · director UI
- Optional `GATERACE_TOKEN` auth
- Android: editable race-box URL + pilot, reconnect, error HUD
- Tests: `scripts/test_pass_detect.py`, `scripts/test_api_and_mock.py`
- Env bootstrap: `scripts/setup_android_env.sh`
- Desktop sim needs: `pip install numpy opencv-python-headless`

## License / safety

Experimental. Follow local UAV law, VLOS, insurance. AR is **not** a substitute for attitude awareness. Geofencing remains DJI’s.

## Race box (director + API)

```bash
cd /work/drone-track-overlay
pip install aiohttp   # if needed
PYTHONPATH=. python3 race_box/server.py
# Director UI: http://127.0.0.1:8088/
# API docs: docs/PHONE_API.md
```

## Android app (SIM build)

```bash
export ANDROID_HOME=/opt/android-sdk
cd android && ./gradlew :app:assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

Emulator needs **KVM** (`/dev/kvm`). With KVM enabled:

```bash
export ANDROID_HOME=/opt/android-sdk
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin"
# AVD GateRace_API34 (google_apis x86_64 API 34) — create once:
# avdmanager create avd -n GateRace_API34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6
emulator -avd GateRace_API34 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -accel on &
adb wait-for-device
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

Emulator host loopback for race box: `http://10.0.2.2:8088`

### Host DJI telemetry mock (no phone / no aircraft)

Posts race-box `/telemetry` from simulated MSDK-like GPS/attitude → ENU:

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py           # arms demo_field, flies all gates
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --once -v  # sample JSON
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --no-arm   # if already armed by phone
```

Use **either** the Android SIM app **or** `dji_telemetry_mock.py` as the telemetry source for one heat (not both at once).
