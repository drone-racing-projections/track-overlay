# Android app (GateRace)

Simulator build: draws gates on a fake horizon and sends telemetry to the race box.

Full project context: [../docs/HOW_IT_WORKS.md](../docs/HOW_IT_WORKS.md) · run steps: [../docs/START.md](../docs/START.md)

## Build

```bash
export ANDROID_HOME=/opt/android-sdk
./gradlew :app:assembleDebug
```

## Point at the race box

| Device | URL |
|--------|-----|
| Emulator | `http://10.0.2.2:8088` |
| Real phone | `http://<laptop-ip>:8088` |

Set URL + pilot in the app, tap **Arm**.

## Real DJI later

Set `SIM_MODE` false, add MSDK, see `DjiIntegrationNotes.kt` and [../docs/API.md](../docs/API.md).
