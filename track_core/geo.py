"""Local ENU tangent plane for track coordinates (meters)."""
from __future__ import annotations

from dataclasses import dataclass
import math

# WGS84
_A = 6378137.0
_F = 1 / 298.257223563
_E2 = _F * (2 - _F)


@dataclass(frozen=True)
class TrackOrigin:
    lat_deg: float
    lon_deg: float
    alt_m: float = 0.0

    def to_enu(self, lat_deg: float, lon_deg: float, alt_m: float = 0.0) -> tuple[float, float, float]:
        return enu_from_llh(self.lat_deg, self.lon_deg, self.alt_m, lat_deg, lon_deg, alt_m)

    def to_llh(self, e: float, n: float, u: float) -> tuple[float, float, float]:
        return llh_from_enu(self.lat_deg, self.lon_deg, self.alt_m, e, n, u)


def _latlon_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sL, cL = math.sin(lat), math.cos(lat)
    sO, cO = math.sin(lon), math.cos(lon)
    n = _A / math.sqrt(1 - _E2 * sL * sL)
    x = (n + alt_m) * cL * cO
    y = (n + alt_m) * cL * sO
    z = (n * (1 - _E2) + alt_m) * sL
    return x, y, z


def enu_from_llh(
    lat0: float, lon0: float, alt0: float,
    lat: float, lon: float, alt: float,
) -> tuple[float, float, float]:
    x0, y0, z0 = _latlon_to_ecef(lat0, lon0, alt0)
    x, y, z = _latlon_to_ecef(lat, lon, alt)
    dx, dy, dz = x - x0, y - y0, z - z0
    lat0r = math.radians(lat0)
    lon0r = math.radians(lon0)
    sL, cL = math.sin(lat0r), math.cos(lat0r)
    sO, cO = math.sin(lon0r), math.cos(lon0r)
    e = -sO * dx + cO * dy
    n = -sL * cO * dx - sL * sO * dy + cL * dz
    u = cL * cO * dx + cL * sO * dy + sL * dz
    return e, n, u


def llh_from_enu(
    lat0: float, lon0: float, alt0: float,
    e: float, n: float, u: float,
) -> tuple[float, float, float]:
    # Iterative-ish closed form via ECEF
    x0, y0, z0 = _latlon_to_ecef(lat0, lon0, alt0)
    lat0r = math.radians(lat0)
    lon0r = math.radians(lon0)
    sL, cL = math.sin(lat0r), math.cos(lat0r)
    sO, cO = math.sin(lon0r), math.cos(lon0r)
    dx = -sO * e - sL * cO * n + cL * cO * u
    dy = cO * e - sL * sO * n + cL * sO * u
    dz = cL * n + sL * u
    x, y, z = x0 + dx, y0 + dy, z0 + dz
    # ECEF to geodetic (Bowring-ish single iteration)
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - _E2))
    for _ in range(4):
        sL = math.sin(lat)
        n_rad = _A / math.sqrt(1 - _E2 * sL * sL)
        lat = math.atan2(z + _E2 * n_rad * sL, p)
    sL = math.sin(lat)
    n_rad = _A / math.sqrt(1 - _E2 * sL * sL)
    alt = p / math.cos(lat) - n_rad
    return math.degrees(lat), math.degrees(lon), alt
