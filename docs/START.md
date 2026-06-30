# Getting started

For the product story (radio, USB, phone, laptop), see [HOW_IT_WORKS.md](HOW_IT_WORKS.md). This page is commands and checks on a computer.

Needs Python 3.10+ and a checkout of this repo.

## 1. Race box

```bash
cd track-overlay
pip install aiohttp
# optional, for spectator video relay:
# install ffmpeg for your OS

PYTHONPATH=. python3 race_box/server.py
```

Director UI: **http://127.0.0.1:8088/**

Optional API auth: set `GATERACE_TOKEN` in the environment before starting.

## 2. Score a heat without a phone

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

Arms the demo track, flies a synthetic path through all gates, prints finish. Watch the director UI.

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --once
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --speed 18
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --no-arm   # if already armed in the UI
```

## 3. Tests

Race box must be up for the API suite.

```bash
PYTHONPATH=. python3 scripts/test_pass_detect.py
PYTHONPATH=. python3 scripts/test_api_and_mock.py
```

## 4. Android simulator

Builds a SIM app (fake flight UI). Real RC USB + MSDK comes later.

```bash
export ANDROID_HOME=/opt/android-sdk   # your SDK path
cd android && ./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

Race box URL:

- Emulator: `http://10.0.2.2:8088`
- Physical phone on LAN: `http://<laptop-ip>:8088`

Set pilot name, tap **Arm**. More detail: [android/README.md](../android/README.md).

Emulators are heavy; see [HARDWARE.md](HARDWARE.md). Optional Linux+KVM bootstrap: `scripts/setup_android_env.sh`.

## 5. Spectator demo (optional)

With `ffmpeg` installed, use **Demo pattern** in the director UI, or:

```bash
curl -X POST http://127.0.0.1:8088/spectator/start \
  -H 'Content-Type: application/json' \
  -d '{"mode":"demo"}'
```

Play `http://127.0.0.1:8088/stream/index.m3u8` in VLC or the director page. See [SPECTATOR.md](SPECTATOR.md).

## 6. Desktop overlay sim (optional)

Needs a display and OpenCV:

```bash
pip install numpy opencv-python
PYTHONPATH=. python3 sim/desktop_sim.py
```

Keys: W/S speed, A/D yaw, R/F altitude, Q/E pitch, Esc quit.

## Avoid

- Driving the same heat with both the telemetry mock and the phone app  
- Flying from the spectator stream or the laptop UI  

## Next

[HOW_IT_WORKS.md](HOW_IT_WORKS.md) · [HARDWARE.md](HARDWARE.md) · [API.md](API.md)
