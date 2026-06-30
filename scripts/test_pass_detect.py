#!/usr/bin/env python3
"""Unit test: fly straight through gate 1 and expect a pass."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from track_core.models import Track, Pose, RaceConfig
from track_core.race import RaceEngine, RaceState


def main() -> None:
    track = Track.load(ROOT / "tracks" / "demo_field.json")
    eng = RaceEngine(track, RaceConfig())
    eng.arm()
    g = track.ordered_gates()[0]
    ne, nn, _ = g.normal()
    # approach from behind
    for i, dist in enumerate(range(40, -5, -2)):
        t = i * 0.1
        pose = Pose(
            t=t,
            e=g.e - ne * dist,
            n=g.n - nn * dist,
            u=g.u,
            yaw_deg=0,
        )
        eng.update(pose)
    assert eng.state in (RaceState.RUNNING, RaceState.FINISHED), eng.state
    assert "g1" in eng.result().gates_hit
    # complete all gates along polyline centers
    eng = RaceEngine(track, RaceConfig())
    eng.arm()
    t = 0.0
    waypoints = []
    gates = track.ordered_gates()
    # start 40m before g1 along -normal
    for gi, g in enumerate(gates):
        ne, nn, nu = g.normal()
        waypoints.append((g.e - ne * 30, g.n - nn * 30, g.u, t))
        t += 1
        waypoints.append((g.e + ne * 5, g.n + nn * 5, g.u, t))
        t += 1
    prev = None
    for e, n, u, tw in waypoints:
        if prev is None:
            prev = (e, n, u, tw)
            continue
        e0, n0, u0, t0 = prev
        steps = 20
        for s in range(1, steps + 1):
            a = s / steps
            pose = Pose(
                t=t0 + a * (tw - t0),
                e=e0 + a * (e - e0),
                n=n0 + a * (n - n0),
                u=u0 + a * (u - u0),
            )
            eng.update(pose)
        prev = (e, n, u, tw)
    res = eng.result()
    print("hits", res.gates_hit, "elapsed", res.elapsed_s, "state", eng.state)
    assert res.finished, res
    assert len(res.gates_hit) == 4
    print("OK")


if __name__ == "__main__":
    main()
