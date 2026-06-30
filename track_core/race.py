from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import Track, Pose, RaceConfig
from .pass_detect import PassDetector, PassEvent


class RaceState(str, Enum):
    IDLE = "idle"
    ARMED = "armed"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass
class RaceResult:
    finished: bool
    t_start: float | None
    t_finish: float | None
    elapsed_s: float | None
    gates_hit: list[str] = field(default_factory=list)
    pass_events: list[PassEvent] = field(default_factory=list)


class RaceEngine:
    """Authoritative race logic — intended to run on the ground race box."""

    def __init__(self, track: Track, config: RaceConfig | None = None) -> None:
        self.track = track
        self.config = config or RaceConfig()
        self.detector = PassDetector()
        self.state = RaceState.IDLE
        self._order = [g.id for g in track.ordered_gates()]
        self._next_idx = 0
        self._t_start: float | None = None
        self._t_finish: float | None = None
        self._hits: list[str] = []
        self._events: list[PassEvent] = []

    def arm(self) -> None:
        self.detector.reset()
        self.state = RaceState.ARMED
        self._next_idx = 0
        self._t_start = None
        self._t_finish = None
        self._hits.clear()
        self._events.clear()

    def update(self, pose: Pose) -> list[PassEvent]:
        if self.state in (RaceState.IDLE, RaceState.FINISHED):
            return []
        gates = self.track.ordered_gates()
        # Only consider next gate if order required; else all
        if self.config.require_order:
            if self._next_idx >= len(gates):
                return []
            consider = [gates[self._next_idx]]
        else:
            consider = gates

        new_events = self.detector.update(pose, consider)
        for ev in new_events:
            if self.config.require_order:
                expected = self._order[self._next_idx]
                if ev.gate_id != expected:
                    continue
                if self.state == RaceState.ARMED:
                    self.state = RaceState.RUNNING
                    self._t_start = ev.t
                self._hits.append(ev.gate_id)
                self._events.append(ev)
                self._next_idx += 1
                if self._next_idx >= len(self._order):
                    self.state = RaceState.FINISHED
                    self._t_finish = ev.t
            else:
                if ev.gate_id not in self._hits:
                    if self.state == RaceState.ARMED:
                        self.state = RaceState.RUNNING
                        self._t_start = ev.t
                    self._hits.append(ev.gate_id)
                    self._events.append(ev)
                    if len(self._hits) >= len(self._order):
                        self.state = RaceState.FINISHED
                        self._t_finish = ev.t
        return new_events

    def result(self) -> RaceResult:
        elapsed = None
        if self._t_start is not None and self._t_finish is not None:
            elapsed = self._t_finish - self._t_start
        return RaceResult(
            finished=self.state == RaceState.FINISHED,
            t_start=self._t_start,
            t_finish=self._t_finish,
            elapsed_s=elapsed,
            gates_hit=list(self._hits),
            pass_events=list(self._events),
        )
