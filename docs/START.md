# Getting started

**New here?** Read [HOW_IT_WORKS.md](HOW_IT_WORKS.md) first — drone, radio, **USB cable into the phone**, app, laptop — in plain language.

This page is only how to run **software on a computer** (and optionally the Android simulator) so you can see scoring without flying.

You need Python 3.10+ and this repo.

---

## 1. Race box (always start here)

```bash
cd track-overlay
pip install aiohttp
# optional — only for TV/demo video through the laptop:
# install ffmpeg for your OS

PYTHONPATH=. python3 race_box/server.py
```

Open **http://127.0.0.1:8088/** — director UI (arm heats, leaderboard, spectator controls).

Optional: set env `GATERACE_TOKEN` if you want a shared secret on the API.

## 2. Prove scoring without a phone or drone

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

Fakes an aircraft through the demo gates. Watch the director page finish a heat.

```bash
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --once    # one sample JSON
PYTHONPATH=. python3 sim/dji_telemetry_mock.py --speed 18
```

## 3. Automated checks

Race box must be running for the second command.

```bash
PYTHONPATH=. python3 scripts/test_pass_detect.py
PYTHONPATH=. python3 scripts/test_api_and_mock.py
```

## 4. Android app (simulator — still no real USB/DJI yet)

This pretends the flight on the phone UI. Real RC USB + MSDK is future work.

```bash
export ANDROID_HOME=/opt/android-sdk   # or your SDK
cd android && ./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

- Emulator → race box: `http://10.0.2.2:8088`
- Real phone on Wi‑Fi → race box: `http://<laptop-ip>:8088`

Tap **Arm** in the app. More: [android/README.md](../android/README.md)

Emulator needs a strong PC ([HARDWARE.md](HARDWARE.md)). Optional bootstrap: `scripts/setup_android_env.sh`.

## 5. Spectator demo (optional TV path)

With `ffmpeg` installed, in the director UI start **Demo pattern**, or:

```bash
curl -X POST http://127.0.0.1:8088/spectator/start \
  -H 'Content-Type: application/json' -d '{"mode":"demo"}'
```

Play `http://127.0.0.1:8088/stream/index.m3u8` in VLC. Details: [SPECTATOR.md](SPECTATOR.md).

## Don’t

- Run the laptop mock **and** the phone app into the **same** heat.
- Fly by watching the spectator stream or the laptop.

## Next

[HOW_IT_WORKS.md](HOW_IT_WORKS.md) · [HARDWARE.md](HARDWARE.md) · [API.md](API.md)
