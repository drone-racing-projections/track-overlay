# Getting started

You need Python 3.10+ and this repo checked out.

## 1. Race box (always start here)

```bash
cd track-overlay
pip install aiohttp
# optional, only if you want TV/demo video relay:
# sudo apt install ffmpeg   # or Windows/macOS equivalent

PYTHONPATH=. python3 race_box/server.py
```

Open **http://127.0.0.1:8088/** — that’s the director UI (arm heats, leaderboard, spectator controls).

Optional shared secret: set env `GATERACE_TOKEN` before starting; then send the same token from clients.

## 2. Prove scoring without a phone

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

Arms `demo_field`, flies a fake path through all gates, prints FINISH. Check the director page.

Useful flags:

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --once      # one JSON sample
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --speed 18
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --no-arm  # if you already armed in the UI
```

## 3. Automated checks

Race box must be running for the API test.

```bash
PYTHONPATH=. python3 scripts/test_pass_detect.py
PYTHONPATH=. python3 scripts/test_api_and_mock.py
```

## 4. Android app (simulator)

Needs Android SDK / JDK. On a fresh Linux box with KVM:

```bash
./scripts/setup_android_env.sh
```

Build and run:

```bash
export ANDROID_HOME=/opt/android-sdk   # or your SDK path
cd android && ./gradlew :app:assembleDebug

# Emulator (heavy — see HARDWARE.md)
emulator -avd GateRace_API34 -no-window -no-audio -no-boot-anim \
  -gpu swiftshader_indirect -accel on &
adb wait-for-device
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

In the app:

- URL on **emulator:** `http://10.0.2.2:8088` (reaches the host laptop)
- URL on a **real phone:** `http://<laptop-LAN-ip>:8088`
- Set pilot name, tap **Arm**, watch gates; heat should finish on the race box

More: [android/README.md](../android/README.md)

## 5. Spectator demo (optional)

Race box running, `ffmpeg` installed. In the director UI → Spectator → mode **Demo pattern** → Start.

Or:

```bash
curl -X POST http://127.0.0.1:8088/spectator/start \
  -H 'Content-Type: application/json' -d '{"mode":"demo"}'
```

Play **http://127.0.0.1:8088/stream/index.m3u8** in VLC or the director page.

Details: [SPECTATOR.md](SPECTATOR.md)

## 6. Desktop visual sim (optional)

Needs a display and OpenCV:

```bash
pip install numpy opencv-python   # or opencv-python-headless without GUI
PYTHONPATH=. python3 sim/desktop_sim.py
```

Keys: W/S speed, A/D yaw, R/F up/down, Q/E pitch, Esc quit.

## Don’t do this

- Run **mock + Android app** as telemetry on the **same** heat (one will be rejected or they’ll fight).
- Point the pilot at the **spectator** HLS stream to fly.
- Use browser `performance.now()` as race time (see [API.md](API.md) clocks).

## Next

- Concepts: [HOW_IT_WORKS.md](HOW_IT_WORKS.md)  
- Gear: [HARDWARE.md](HARDWARE.md)  
