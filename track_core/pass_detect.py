from __future__ import annotations

from dataclasses import dataclass

from .models import Gate, Pose


@dataclass
class PassEvent:
    gate_id: str
    t: float
    e: float
    n: float
    u: float
    approach_dot: float


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


class PassDetector:
    def __init__(self) -> None:
        self._prev: Pose | None = None
        self._cooldown: dict[str, float] = {}
        self.cooldown_s: float = 1.0

    def reset(self) -> None:
        self._prev = None
        self._cooldown.clear()

    def update(self, pose: Pose, gates: list[Gate]) -> list[PassEvent]:
        events: list[PassEvent] = []
        prev = self._prev
        self._prev = pose
        if prev is None:
            return events
        dt = pose.t - prev.t
        if dt <= 0:
            return events
        p0 = (prev.e, prev.n, prev.u)
        p1 = (pose.e, pose.n, pose.u)
        vel = ((p1[0] - p0[0]) / dt, (p1[1] - p0[1]) / dt, (p1[2] - p0[2]) / dt)
        speed = (vel[0] ** 2 + vel[1] ** 2 + vel[2] ** 2) ** 0.5

        for g in gates:
            last = self._cooldown.get(g.id)
            if last is not None and pose.t - last < self.cooldown_s:
                continue
            nrm = g.normal()
            c = g.center()
            d0 = _dot(_sub(p0, c), nrm)
            d1 = _dot(_sub(p1, c), nrm)
            # Cross from back (d<=0) to front (d>0), or strict d0<0 to d1>=0
            crossed = (d0 < 0 and d1 >= 0) or (d0 <= 0 and d1 > 0)
            if not crossed or d1 == d0:
                continue
            frac = -d0 / (d1 - d0)
            ip = (
                p0[0] + frac * (p1[0] - p0[0]),
                p0[1] + frac * (p1[1] - p0[1]),
                p0[2] + frac * (p1[2] - p0[2]),
            )
            radial = _sub(ip, c)
            along = _dot(radial, nrm)
            radial = (radial[0] - along * nrm[0], radial[1] - along * nrm[1], radial[2] - along * nrm[2])
            r = (radial[0] ** 2 + radial[1] ** 2 + radial[2] ** 2) ** 0.5
            if r > g.radius_m:
                continue
            approach = _dot(vel, nrm)
            if speed < 0.5 or approach <= 0:
                continue
            ev = PassEvent(gate_id=g.id, t=prev.t + frac * dt, e=ip[0], n=ip[1], u=ip[2], approach_dot=approach)
            events.append(ev)
            self._cooldown[g.id] = pose.t
        return events
