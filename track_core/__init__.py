"""GateRace track core: geometry, pass detection, race timing (authoritative logic)."""
from .geo import enu_from_llh, llh_from_enu, TrackOrigin
from .models import Gate, Track, Pose, RaceConfig
from .pass_detect import PassDetector, PassEvent
from .race import RaceEngine, RaceState

__all__ = [
    "enu_from_llh",
    "llh_from_enu",
    "TrackOrigin",
    "Gate",
    "Track",
    "Pose",
    "RaceConfig",
    "PassDetector",
    "PassEvent",
    "RaceEngine",
    "RaceState",
]
