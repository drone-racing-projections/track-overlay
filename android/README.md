# GateRace Android app

Layer-1 AR gates on a synthetic horizon in **SIM** builds. Field builds will composite the same projection on DJI MSDK liveview.

## Build

```bash
export ANDROID_HOME=/opt/android-sdk
cd android
./gradlew :app:assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```

## Run with race box

1. Start the race box on the host (`PYTHONPATH=. python3 race_box/server.py`).  
2. Install and launch the app.  
3. Set **race box URL** and **pilot id** in the HUD fields (persisted).  
   - Emulator: `http://10.0.2.2:8088`  
   - Physical phone: `http://<laptop-lan-ip>:8088`  
4. Tap **Arm** (resets the SIM clock and arms a heat).  
5. SIM aircraft auto-flies the waypoint path through each gate; **Throttle+** raises speed.

Connection status and errors appear in the HUD. After **FINISH**, tap **Arm** again for a new heat (telemetry is rejected with 409 until then).

### Headless emulator (KVM)

```bash
export ANDROID_HOME=/opt/android-sdk
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools"
emulator -avd GateRace_API34 -no-window -no-audio -no-boot-anim \
  -gpu swiftshader_indirect -accel on &
adb wait-for-device
adb uninstall com.gaterace.app   # if signature changes between builds
adb install app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.gaterace.app/.ui.MainActivity
```

Bootstrap SDK/AVD: `../scripts/setup_android_env.sh`.

## Host-side alternative

Without a phone, drive the race box with:

```bash
PYTHONPATH=. python3 ../sim/dji_telemetry_mock.py
```

Do not run the mock and the app as telemetry sources on the same heat.

## DJI field integration

See `DjiIntegrationNotes.kt` and [docs/PHONE_API.md](../docs/PHONE_API.md). Set `SIM_MODE` to `false` in `app/build.gradle.kts`, add the MSDK AAR and app key, and replace `SimFlight` with liveview + pose callbacks.

Spectator RTMP from the phone (delayed) is documented in [docs/SPECTATOR.md](../docs/SPECTATOR.md); the pilot display must not depend on that stream.
