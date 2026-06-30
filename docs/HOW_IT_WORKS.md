# How it works

## The idea

You fly a consumer drone with a camera (v1 target: something in the Mini 4 Pro class with Mobile SDK support). The aircraft sends video and flight data to the **remote controller over radio**. On phone-centric remotes, the controller connects to your **phone over USB** so an app on the phone can show live view and talk to the aircraft stack (Android will usually prompt for USB / OTG permissions—same pattern as DJI’s own apps).

**GateRace** is that app: live video plus virtual gates fixed in the world. You fly through the gates in order. A **laptop on the field** (the race box) receives light telemetry over Wi‑Fi and records official times.

```
[ Drone ]
    |  radio
    v
[ Remote ] ---- USB ---- [ Phone: GateRace ]
                            |
                            |  Wi‑Fi (position updates)
                            v
                      [ Laptop: race box ]
                            |
                            +-- director UI / leaderboard
                            +-- optional delayed video for TV or online
```

## What each piece does

| Piece | Job |
|-------|-----|
| Drone | Camera and airframe |
| Remote | Sticks, radio link, USB link to the phone on phone-centric RCs |
| Phone + GateRace | Pilot display: video, AR gates, telemetry to the race box |
| USB (RC → phone) | How phone-centric setups deliver live view into the app |
| Laptop (race box) | Authoritative timing, heats, leaderboard; optional spectator video |
| Field Wi‑Fi | Telemetry and control between phone and laptop—not the pilot video path |

Prefer an RC **without** a built-in screen so GateRace owns the pixels. Built-in-screen remotes are a different integration path.

## Pilot vs scorekeeping vs spectators

**Flying** uses the phone display, fed from the RC (USB) and the drone (radio). That path should stay local and low-latency. Routing pilot video through the laptop and back adds delay and is a bad way to fly.

**Scoring** uses small telemetry messages (position, time, attitude) from the phone to the race box at roughly 10–20 Hz. The race box decides gate passes and official elapsed time.

**Spectators** may watch a **delayed** copy on a TV or online. The race box can ingest and redistribute that video. Fine for audiences; not for piloting.

## Coordinates and time (short version)

Gates and positions are in **metres east / north / up** from a GPS origin on the field (ENU). The phone converts GPS to ENU before sending telemetry.

Heat time `t` is **seconds on the phone during that heat** (often starting near zero after Arm). Scoring uses that domain only—not wall clocks or browser timers.

One heat, one telemetry source (one `pilot_id`). Don’t run the laptop mock and the phone against the same heat.

## Smart glasses

USB‑C glasses such as Xreal or Viture typically act as an **external display**: they expect **DisplayPort Alt Mode** from the phone (video out over USB‑C). Compatibility depends on the phone supporting DP Alt Mode; vendor lists matter.

The DJI RC link uses the phone as a **USB host / OTG** peer for live view and control. On a single USB‑C port, host-to-RC and DP-out-to-glasses are different roles and often can’t share one plug without a dock or dual-port phone that actually supports both.

A workable mental model when it does work:

`drone → radio → RC → USB → phone (GateRace) → USB‑C video out → glasses`

Glasses mirror (or extend) whatever GateRace is showing; they are not a second flight receiver. Charge-and-play adapters in the glasses ecosystem usually add power + display, not DJI OTG plus glasses on one port.

**Practical take:** ship v1 on the phone screen with RC USB. Treat glasses as an experiment: confirm DP Alt Mode, check latency and outdoor brightness, and solve the port conflict deliberately. Wireless casting adds delay and is a weak fit for racing. Bluetooth “AI glasses” are a different product class than DP FPV-style monitors.

## What’s implemented vs still on the roadmap

| Working in-repo | Still needs real MSDK / aircraft |
|-----------------|----------------------------------|
| Race box timing, director UI, leaderboard | Live DJI video inside GateRace |
| Telemetry mock and Android simulator | RC USB + MSDK permissions on a real phone |
| Spectator demo / HLS relay on the laptop | Production phone RTMP for spectators |
| Track files and pass detection | Field calibration on real GPS |

The product story above is the goal. The simulator and mock are how we exercise scoring and UI without a drone.

## Next

- Run software: [START.md](START.md)  
- Gear lists: [HARDWARE.md](HARDWARE.md)  
- Integration API: [API.md](API.md)  
- TV / stream: [SPECTATOR.md](SPECTATOR.md)  
