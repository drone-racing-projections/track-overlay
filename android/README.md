# GateRace Android

Layer-1 AR gates on liveview (SIM today; DJI MSDK for field).

## Build

```bash
export ANDROID_HOME=/opt/android-sdk
cd /work/drone-track-overlay/android
./gradlew :app:assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

## Emulator + race box

```bash
# terminal 1
cd /work/drone-track-overlay && PYTHONPATH=. python3 race_box/server.py

# terminal 2 — start AVD then:
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

Emulator reaches host race box at `http://10.0.2.2:8088` (BuildConfig.DEFAULT_RACE_BOX).

Headless AVD (KVM):

```bash
export ANDROID_HOME=/opt/android-sdk
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools"
emulator -avd GateRace_API34 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -accel on &
adb wait-for-device
```

Host-only alternative to the in-app SIM: `PYTHONPATH=. python3 sim/dji_telemetry_mock.py` (see repo README).

## SIM controls

- Auto-flies toward next gate
- **Throttle+** increases speed
- **Arm** arms heat on race box

## DJI

See `DjiIntegrationNotes.kt` and `docs/PHONE_API.md`. Set `SIM_MODE` false and add MSDK AAR + key.
