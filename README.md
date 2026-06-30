# Track Overlay

**Race through virtual gates while flying a real drone.**

You fly a camera drone. The remote talks to the aircraft over radio. You **plug the remote into your phone with USB**, open our app (**GateRace**), and you see live video **with race rings drawn in the world**. A laptop on the field keeps official time. Optional delayed video can go to a TV or online for spectators — not for piloting.

---

## Start here

1. **[docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md)** — the human story (USB, radio, phone, laptop, smart glasses)  
2. **[docs/START.md](docs/START.md)** — run the software on a computer today  
3. **[docs/HARDWARE.md](docs/HARDWARE.md)** — what you need (must-have vs nice; users then developers)  

Also: [docs/API.md](docs/API.md) (programmers), [docs/SPECTATOR.md](docs/SPECTATOR.md) (TV/stream), [android/README.md](android/README.md) (app build).

---

## Picture

```
 Drone  --radio-->  Remote controller  --USB-->  Phone (GateRace: video + gates)
                                                   |
                                                   +-- Wi‑Fi telemetry --> Laptop (scores the race)
                                                   +-- optional delayed video --> TV / internet
```

If you only remember one thing: **pilots look at the phone (or a display that mirrors that phone). They do not fly off the laptop or the livestream.**

---

## Try scoring in two commands (no drone)

```bash
pip install aiohttp
PYTHONPATH=. python3 race_box/server.py    # http://127.0.0.1:8088/

# other terminal
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

---

## Code map

| Folder | What it is |
|--------|------------|
| `race_box/` | Laptop ground station (times, web UI, optional spectator video) |
| `android/` | GateRace phone app (simulator mode until DJI SDK is wired) |
| `track_core/` | Shared “where are the gates / did they pass” logic |
| `tracks/` | Gate layouts (e.g. demo field) |
| `sim/` | Fake flights for testing |
| `docs/` | Documentation |

---

## License / safety

[LICENSE](LICENSE). Experimental. Obey local drone laws. Virtual gates are not a substitute for flying carefully.
