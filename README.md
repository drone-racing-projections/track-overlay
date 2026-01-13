# Drone Racing Projections — Track Overlay

**Drone Racing Projections** is an open-source effort to project **virtual racing elements into real drone flights**.

This repository contains **Track Overlay**, a telemetry-driven system that renders
virtual racing tracks (gates, segments, checkpoints) over an FPV video feed while flying a **real drone in real airspace**.

The project is early-stage. Goals are clear, implementation details are intentionally open.

---

## What this is

- Real drone
- Real environment
- Virtual track projected onto FPV video
- Driven by telemetry (GPS, IMU, velocity)

No visual SLAM or object detection is required for the initial approach.

---

## Core idea (Track Overlay)

- The track exists in world coordinates
- The drone provides its estimated pose via telemetry
- A client projects the track onto the FPV video feed
- Gate passage is validated using large spatial volumes and margins

This favors simplicity, robustness, and fast iteration.

---

## Design principles

- Prefer understandable systems over complex magic
- Accept approximate precision when the experience allows it
- Validate ideas early with working demos
- Keep hardware and software replaceable

---

## Scope (current)

### In scope
- FPV video input
- Telemetry-based positioning and orientation
- Virtual track representation
- Real-time projection / HUD overlay
- Gate passage detection
- Linux-first development

### Out of scope (for now)
- Visual AR / SLAM
- Obstacle detection
- Centimeter-level precision
- Vendor-specific drone stacks

---

## Open implementation options

### Video input
- USB UVC capture
- Network streams (RTSP or similar)
- Video files (simulation/testing)

### Telemetry
- Simulated data
- MAVLink-based flight controllers
- Other telemetry sources if needed

### Track definition
- Gates and waypoints in world coordinates
- Configurable sizes and safety margins
- Simple text-based formats (YAML / JSON)

### Projection
- HUD-style overlays
- 3D projection using a camera model
- Simplified pinhole projection

---

## Roadmap (to MVP)

### Phase 1 — Linux demo (simulated drone)
- Video from file or webcam
- Keyboard-controlled simulated drone
- Simulated telemetry
- Virtual track with large gates
- Projection onto video
- Gate passage detection
- Basic timing/state display

### Phase 2 — Reproducible execution
- Clear documentation
- Explicit dependencies
- Setup and run instructions
- Track configuration examples
- Basic diagnostics

### Phase 3 — Real-world readiness
- Short demo video
- Project overview
- Safety-oriented test plan
- Drone capability checklist

### Phase 4 — Real drone integration (Linux)
- Real telemetry input
- Real video input
- Packet-loss tolerance
- Filter tuning with real data
- Complete virtual track flight

**MVP:**  
A real drone flying a virtual racing track in an open environment with stable visualization.

---

## Beyond the MVP

Possible directions:
- Local recording
- Live streaming
- Android or other platform ports
- Companion computers
- Higher-precision positioning
- Camera-based or hybrid AR projections

---

## Architecture (conceptual)

```
Drone (real or simulated)
 └─ pose estimation → telemetry
                      ↓
                Client application
        ┌──────────────────────────┐
        │ video input              │
        │ telemetry input          │
        │ virtual track            │
        │ projection / overlay     │
        │ optional recording       │
        │ optional streaming       │
        └──────────────────────────┘
```

---

## Status

- Repo initialized
- Scope defined
- Phase 1 pending

---

## License

TBD (MIT or Apache-2.0 likely).

---

## Contributions

Early contributions are best focused on:
- architecture
- assumptions
- design feedback
