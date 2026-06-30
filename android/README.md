# GateRace (Android)

Simulator build: synthetic horizon, gate overlay, telemetry to the race box.

Context: [../docs/HOW_IT_WORKS.md](../docs/HOW_IT_WORKS.md) · runbook: [../docs/START.md](../docs/START.md)

## Build

```bash
export ANDROID_HOME=/opt/android-sdk
./gradlew :app:assembleDebug
```

## Race box URL

| Device | URL |
|--------|-----|
| Emulator | `http://10.0.2.2:8088` |
| Phone on LAN | `http://<laptop-ip>:8088` |

Set URL and pilot in the UI, tap **Arm**.

## Field / MSDK

Set `SIM_MODE` false, add MSDK artifacts and app key, see `DjiIntegrationNotes.kt` and [../docs/API.md](../docs/API.md). RC connects to the phone over USB on phone-centric controllers.
