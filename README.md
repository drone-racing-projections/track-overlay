# Track Overlay

Virtual racing gates on a **real drone** FPV-style feed. Pilots fly through world-locked rings; a laptop on the field keeps score. Optional delayed video goes to a TV or the internet.

**This is GateRace** — the implementation living in this repo.

---

## Read these in order

| # | Doc | What it’s for |
|---|-----|----------------|
| 1 | **[docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md)** | The whole system in plain language (start here if you’re lost) |
| 2 | **[docs/START.md](docs/START.md)** | Run it on your machine today |
| 3 | **[docs/HARDWARE.md](docs/HARDWARE.md)** | What to buy — users first, then developers; must-have vs optional |
| 4 | **[docs/API.md](docs/API.md)** | Phone ↔ race box protocol (when you’re wiring software) |
| 5 | **[docs/SPECTATOR.md](docs/SPECTATOR.md)** | TV / internet POV via the race box |
| — | [docs/RESEARCH.md](docs/RESEARCH.md) | Background options we considered (optional reading) |

Android app notes: [android/README.md](android/README.md)

---

## 30-second picture

```
Drone ──RF──► Phone (GateRace app)
                 │ draws AR gates for the PILOT  (must stay fast)
                 │
                 ├── light telemetry ──► Race box laptop (official times)
                 │
                 └── optional delayed video ──► Race box ──► TV / Twitch / etc.
```

Rules of thumb:

- **Pilot video stays on the phone.** Never route it through the laptop for flying.
- **Race box owns timing** and optional spectator video.
- **Large outdoor gates** so normal GPS is good enough.

---

## Repo layout (code)

```
track_core/     Shared maths: GPS→local metres, gate hits, race state
tracks/         Track files (gate positions), e.g. demo_field.json
race_box/       Ground station: API, director web UI, spectator relay
android/        GateRace Android app (simulator mode today)
sim/            Laptop tools: fake DJI telemetry, optional desktop preview
scripts/        Tests and environment setup
docs/           Documentation (see table above)
```

---

## Fastest “it works” check

```bash
# Terminal 1 — ground station
pip install aiohttp
PYTHONPATH=. python3 race_box/server.py
# open http://127.0.0.1:8088/

# Terminal 2 — fake aircraft telemetry
PYTHONPATH=. python3 sim/dji_telemetry_mock.py
```

You should see a heat finish on the director page and show up on the leaderboard.

More detail: [docs/START.md](docs/START.md).

---

## License / safety

See [LICENSE](LICENSE). Experimental. Follow local drone law. AR is not a substitute for looking where you’re going.
