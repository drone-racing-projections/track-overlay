"""Project 3D ENU points into a simple pinhole camera (for sim + future native ports)."""
from __future__ import annotations

import math
from .models import Pose


def _rot_zyx_body_to_world(yaw_deg: float, pitch_deg: float, roll_deg: float):
    """Body: +X forward, +Y right, +Z down (NED-ish) — we use ENU world.

    For simplicity in v1 sim we treat yaw 0 = facing +N, camera looks along body +X
    in a local frame where x=forward(N when yaw0), y=right(E), z=up.
    """
    y = math.radians(yaw_deg)
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)
    cy, sy = math.cos(y), math.sin(y)
    cp, sp = math.cos(p), math.sin(p)
    cr, sr = math.cos(r), math.sin(r)
    # R = Rz(yaw) Ry(pitch) Rx(roll) mapping body→world in ENU-like (x east, y north, z up)
    # Remap: body forward = north component when yaw=0 → use yaw from north toward east
    # World ENU: e, n, u
    # Body: fwd, right, up
    # yaw: rotation about up from +N toward +E
    R = [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]
    # Above is for x=north, y=east, z=up — convert to e,n,u by swapping
    # body fwd → (n,e) with yaw from north
    # Actually define R_bw such that world_enu = R * body_fru
    # body_fru: forward, right, up
    # yaw 0: forward = +N = (0,1,0) in enu
    # yaw 90: forward = +E = (1,0,0)
    # R columns are body axes in world
    # forward = (sin(yaw), cos(yaw), 0) in (e,n,u)
    # right = (cos(yaw), -sin(yaw), 0)
    # up = (0,0,1) then apply pitch/roll...
    # Simpler FPV: yaw + gimbal pitch only for v1
    return R


def project_points(
    pose: Pose,
    points_enu: list[tuple[float, float, float]],
    width: int,
    height: int,
    hfov_deg: float = 70.0,
) -> list[tuple[float, float, float] | None]:
    """Return list of (u_px, v_px, depth_forward) or None if behind camera.

    Camera at pose ENU; looks along heading yaw (0=N) with pitch (gimbal or body).
    """
    yaw = math.radians(pose.yaw_deg)
    pitch = math.radians(
        pose.gimbal_pitch_deg if pose.gimbal_pitch_deg is not None else pose.pitch_deg
    )
    # Camera axes in ENU
    # forward
    cf = (math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch))
    # right = up_world × forward (approx level)
    up_w = (0.0, 0.0, 1.0)
    cr = (
        up_w[1] * cf[2] - up_w[2] * cf[1],
        up_w[2] * cf[0] - up_w[0] * cf[2],
        up_w[0] * cf[1] - up_w[1] * cf[0],
    )
    crm = math.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2) or 1.0
    cr = (cr[0] / crm, cr[1] / crm, cr[2] / crm)
    # cam up = forward × right
    cu = (
        cf[1] * cr[2] - cf[2] * cr[1],
        cf[2] * cr[0] - cf[0] * cr[2],
        cf[0] * cr[1] - cf[1] * cr[0],
    )

    fx = (width / 2) / math.tan(math.radians(hfov_deg) / 2)
    fy = fx
    cx, cy = width / 2, height / 2
    out: list[tuple[float, float, float] | None] = []
    pe, pn, pu = pose.e, pose.n, pose.u
    for e, n, u in points_enu:
        de, dn, du = e - pe, n - pn, u - pu
        # camera frame
        x = de * cr[0] + dn * cr[1] + du * cr[2]  # right
        y = de * cu[0] + dn * cu[1] + du * cu[2]  # up
        z = de * cf[0] + dn * cf[1] + du * cf[2]  # forward
        if z <= 0.5:
            out.append(None)
            continue
        u_px = cx + fx * (x / z)
        v_px = cy - fy * (y / z)
        out.append((u_px, v_px, z))
    return out


def gate_ring_points(gate, segments: int = 48) -> list[tuple[float, float, float]]:
    """Circle in gate plane, center at gate, radius gate.radius_m."""
    import math as m
    ne, nn, nu = gate.normal()
    # basis in plane
    helper = (0.0, 0.0, 1.0) if abs(nu) < 0.9 else (1.0, 0.0, 0.0)
    ax = (
        nn * helper[2] - nu * helper[1],
        nu * helper[0] - ne * helper[2],
        ne * helper[1] - nn * helper[0],
    )
    am = m.sqrt(ax[0] ** 2 + ax[1] ** 2 + ax[2] ** 2) or 1.0
    ax = (ax[0] / am, ax[1] / am, ax[2] / am)
    ay = (
        nn * ax[2] - nu * ax[1],
        nu * ax[0] - ne * ax[2],
        ne * ax[1] - nn * ax[0],
    )
    pts = []
    for i in range(segments):
        th = 2 * m.pi * i / segments
        c, s = m.cos(th), m.sin(th)
        pts.append((
            gate.e + gate.radius_m * (c * ax[0] + s * ay[0]),
            gate.n + gate.radius_m * (c * ax[1] + s * ay[1]),
            gate.u + gate.radius_m * (c * ax[2] + s * ay[2]),
        ))
    return pts
