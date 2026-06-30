#!/usr/bin/env python3
"""Latency-friendly desktop sim: keyboard-fly through virtual gates on a synthetic feed.

Controls:
  W/S  forward / back
  A/D  yaw left / right
  R/F  up / down
  Q/E  pitch camera
  SPACE arm/start race (if idle)
  ESC  quit

Run from repo root:
  PYTHONPATH=. python3 sim/desktop_sim.py
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np

try:
    import cv2
except ImportError:
    print("Need opencv: apt install python3-opencv / pip install opencv-python")
    raise

from track_core.models import Pose, Track, RaceConfig
from track_core.race import RaceEngine, RaceState
from track_core.project import project_points, gate_ring_points


W, H = 1280, 720


def draw_gate(frame, gate, pose, active: bool) -> None:
    pts3 = gate_ring_points(gate, 64)
    proj = project_points(pose, pts3, W, H, hfov_deg=72)
    color = (0, 255, 80) if active else (0, 160, 255)
    thickness = 4 if active else 2
    img_pts = []
    for p in proj:
        if p is None:
            img_pts.append(None)
        else:
            img_pts.append((int(p[0]), int(p[1])))
    for i in range(len(img_pts)):
        a, b = img_pts[i], img_pts[(i + 1) % len(img_pts)]
        if a is not None and b is not None:
            # only draw if reasonably on screen
            if -200 < a[0] < W + 200 and -200 < b[0] < W + 200:
                cv2.line(frame, a, b, color, thickness, cv2.LINE_AA)
    # label
    center_proj = project_points(pose, [gate.center()], W, H)[0]
    if center_proj is not None:
        x, y, z = center_proj
        if 0 <= x < W and 0 <= y < H:
            cv2.putText(
                frame, gate.name or gate.id, (int(x) - 20, int(y)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA,
            )


def sky_ground(frame, pose: Pose) -> None:
    """Cheap synthetic horizon."""
    pitch = pose.gimbal_pitch_deg if pose.gimbal_pitch_deg is not None else pose.pitch_deg
    horizon = int(H / 2 + pitch * 8)
    horizon = max(0, min(H, horizon))
    frame[:horizon, :] = (80, 50, 30)  # BGR sky-ish
    frame[horizon:, :] = (40, 90, 40)
    # grid lines on ground for motion feel
    for k in range(-20, 21):
        # lines in ENU projected — simplified stripes by yaw
        pass


def main() -> None:
    track_path = ROOT / "tracks" / "demo_field.json"
    track = Track.load(track_path)
    engine = RaceEngine(track, RaceConfig(require_order=True))
    engine.arm()

    # start behind first gate
    g0 = track.ordered_gates()[0]
    ne, nn, nu = g0.normal()
    pose = Pose(
        t=0.0,
        e=g0.e - ne * 40,
        n=g0.n - nn * 40,
        u=g0.u + 2.0,
        yaw_deg=math.degrees(math.atan2(ne, nn)),
        pitch_deg=0.0,
        gimbal_pitch_deg=-5.0,
    )

    vel = 0.0
    yaw_rate = 0.0
    last = time.perf_counter()
    print("GateRace desktop sim — latency-first overlay prototype")
    print("W/S speed, A/D yaw, R/F altitude, Q/E camera pitch, ESC quit")

    while True:
        now = time.perf_counter()
        dt = min(0.05, now - last)
        last = now
        pose.t += dt

        # integrate
        yaw = math.radians(pose.yaw_deg)
        pose.e += math.sin(yaw) * vel * dt
        pose.n += math.cos(yaw) * vel * dt
        pose.yaw_deg += yaw_rate * dt

        events = engine.update(pose)
        for ev in events:
            print(f"  PASS {ev.gate_id} at t={ev.t:.2f}s")

        frame = np.zeros((H, W, 3), dtype=np.uint8)
        sky_ground(frame, pose)

        nxt = None
        if engine.state != RaceState.FINISHED and engine._next_idx < len(track.gates):
            nxt = track.ordered_gates()[engine._next_idx].id
        for g in track.ordered_gates():
            draw_gate(frame, g, pose, active=(g.id == nxt))

        # HUD
        res = engine.result()
        hud = f"state={engine.state.value}  vel={vel:.1f}m/s  alt={pose.u:.1f}m"
        if res.t_start is not None and engine.state == RaceState.RUNNING:
            hud += f"  time={pose.t - res.t_start:.2f}s"
        if res.finished and res.elapsed_s is not None:
            hud += f"  FINISH {res.elapsed_s:.2f}s"
            cv2.putText(frame, f"FINISH {res.elapsed_s:.2f}s", (W // 2 - 120, H // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, hud, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "GateRace sim — rings world-locked in ENU", (20, H - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("GateRace", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key in (ord("w"), ord("W")):
            vel = min(25.0, vel + 2.0)
        elif key in (ord("s"), ord("S")):
            vel = max(-5.0, vel - 2.0)
        elif key in (ord("a"), ord("A")):
            yaw_rate = -45.0
        elif key in (ord("d"), ord("D")):
            yaw_rate = 45.0
        elif key in (ord("r"), ord("R")):
            pose.u += 1.0
        elif key in (ord("f"), ord("F")):
            pose.u = max(0.5, pose.u - 1.0)
        elif key in (ord("q"), ord("Q")):
            pose.gimbal_pitch_deg = (pose.gimbal_pitch_deg or 0) + 3
        elif key in (ord("e"), ord("E")):
            pose.gimbal_pitch_deg = (pose.gimbal_pitch_deg or 0) - 3
        else:
            # decay yaw rate for keyboard
            yaw_rate *= 0.85
            if abs(yaw_rate) < 1:
                yaw_rate = 0.0

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
