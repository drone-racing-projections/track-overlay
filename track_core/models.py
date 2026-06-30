from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
import json
from pathlib import Path

from .geo import TrackOrigin


@dataclass
class Gate:
    id: str
    e: float
    n: float
    u: float
    normal_e: float
    normal_n: float
    normal_u: float = 0.0
    radius_m: float = 10.0
    thickness_m: float = 3.0
    sequence: int = 0
    name: str = ""

    def center(self) -> tuple[float, float, float]:
        return self.e, self.n, self.u

    def normal(self) -> tuple[float, float, float]:
        ne, nn, nu = self.normal_e, self.normal_n, self.normal_u
        mag = (ne * ne + nn * nn + nu * nu) ** 0.5 or 1.0
        return ne / mag, nn / mag, nu / mag


@dataclass
class Track:
    name: str
    origin: TrackOrigin
    gates: list[Gate] = field(default_factory=list)
    description: str = ""

    def ordered_gates(self) -> list[Gate]:
        return sorted(self.gates, key=lambda g: g.sequence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "origin": {
                "lat_deg": self.origin.lat_deg,
                "lon_deg": self.origin.lon_deg,
                "alt_m": self.origin.alt_m,
            },
            "gates": [asdict(g) for g in self.gates],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Track":
        o = d["origin"]
        origin = TrackOrigin(o["lat_deg"], o["lon_deg"], o.get("alt_m", 0.0))
        gates = [Gate(**g) for g in d.get("gates", [])]
        return cls(name=d["name"], origin=origin, gates=gates, description=d.get("description", ""))

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Track":
        return cls.from_dict(json.loads(Path(path).read_text()))


@dataclass
class Pose:
    t: float
    e: float
    n: float
    u: float
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    gimbal_pitch_deg: float | None = None
    gimbal_yaw_deg: float | None = None


@dataclass
class RaceConfig:
    start_gate_id: str | None = None
    require_order: bool = True
    min_speed_mps: float = 0.5
