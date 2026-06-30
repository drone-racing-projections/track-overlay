# Track Overlay

Virtual racing gates on a real drone’s camera feed.

You fly a DJI-class aircraft. The remote links to the drone over radio and to your phone over USB. Open **GateRace**, see live video with world-locked gates, and race. A laptop on the field (the **race box**) keeps official time. Spectators can watch a delayed feed on a TV or online if you set that up—pilots always fly from the phone (or a display that mirrors it).

---

## Docs

| Start with | Then |
|------------|------|
| [How it works](docs/HOW_IT_WORKS.md) | [Getting started](docs/START.md) · [Hardware](docs/HARDWARE.md) |
| Building / integrating | [API](docs/API.md) · [Spectator video](docs/SPECTATOR.md) · [Android app](android/README.md) |
| Background | [Research notes](docs/RESEARCH.md) |

---

## Quick picture

```
Drone --radio--> Remote controller --USB--> Phone (GateRace: video + gates)
                                              |
                                              +-- Wi‑Fi telemetry --> Laptop (scoring)
                                              +-- optional delayed video --> TV / internet
```

---

## Try scoring without a drone

```bash
pip install aiohttp
PYTHONPATH=. python3 race_box/server.py    # http://127.0.0.1:8088/

# other terminal
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

---

## Repo layout

| Path | Role |
|------|------|
| `race_box/` | Ground station: timing, director UI, spectator relay |
| `android/` | GateRace app (simulator mode until MSDK is wired) |
| `track_core/` | Shared gate geometry and pass detection |
| `tracks/` | Track definitions (e.g. `demo_field.json`) |
| `sim/` | Desktop tools and fake telemetry |
| `scripts/` | Tests and env setup |
| `docs/` | Documentation |

---

## License and safety

See [LICENSE](LICENSE). Experimental software. Follow local UAV rules. AR overlays are not a substitute for situational awareness.
