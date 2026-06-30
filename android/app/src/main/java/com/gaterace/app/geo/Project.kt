package com.gaterace.app.geo

import kotlin.math.*

/** Project ENU points to pixel coords. Returns (x,y,depth) or null if behind camera. */
fun projectPoints(
    pose: Pose,
    points: List<Triple<Double, Double, Double>>,
    width: Int,
    height: Int,
    hfovDeg: Double = 72.0
): List<Triple<Float, Float, Float>?> {
    val yaw = Math.toRadians(pose.yawDeg)
    val pitch = Math.toRadians(pose.gimbalPitchDeg ?: pose.pitchDeg)
    val cf = Triple(sin(yaw) * cos(pitch), cos(yaw) * cos(pitch), sin(pitch))
    val upW = Triple(0.0, 0.0, 1.0)
    var cr = Triple(
        upW.second * cf.third - upW.third * cf.second,
        upW.third * cf.first - upW.first * cf.third,
        upW.first * cf.second - upW.second * cf.first
    )
    val crm = sqrt(cr.first * cr.first + cr.second * cr.second + cr.third * cr.third).coerceAtLeast(1e-9)
    cr = Triple(cr.first / crm, cr.second / crm, cr.third / crm)
    val cu = Triple(
        cf.second * cr.third - cf.third * cr.second,
        cf.third * cr.first - cf.first * cr.third,
        cf.first * cr.second - cf.second * cr.first
    )
    val fx = (width / 2.0) / tan(Math.toRadians(hfovDeg) / 2.0)
    val fy = fx
    val cx = width / 2.0
    val cy = height / 2.0
    return points.map { (e, n, u) ->
        val de = e - pose.e; val dn = n - pose.n; val du = u - pose.u
        val x = de * cr.first + dn * cr.second + du * cr.third
        val y = de * cu.first + dn * cu.second + du * cu.third
        val z = de * cf.first + dn * cf.second + du * cf.third
        if (z <= 0.5) null
        else Triple((cx + fx * (x / z)).toFloat(), (cy - fy * (y / z)).toFloat(), z.toFloat())
    }
}

fun gateRingPoints(gate: Gate, segments: Int = 48): List<Triple<Double, Double, Double>> {
    val (ne, nn, nu) = gate.normal()
    val helper = if (abs(nu) < 0.9) Triple(0.0, 0.0, 1.0) else Triple(1.0, 0.0, 0.0)
    var ax = Triple(
        nn * helper.third - nu * helper.second,
        nu * helper.first - ne * helper.third,
        ne * helper.second - nn * helper.first
    )
    val am = sqrt(ax.first * ax.first + ax.second * ax.second + ax.third * ax.third).coerceAtLeast(1e-9)
    ax = Triple(ax.first / am, ax.second / am, ax.third / am)
    val ay = Triple(
        nn * ax.third - nu * ax.second,
        nu * ax.first - ne * ax.third,
        ne * ax.second - nn * ax.first
    )
    return (0 until segments).map { i ->
        val th = 2.0 * PI * i / segments
        val c = cos(th); val s = sin(th)
        Triple(
            gate.e + gate.radiusM * (c * ax.first + s * ay.first),
            gate.n + gate.radiusM * (c * ax.second + s * ay.second),
            gate.u + gate.radiusM * (c * ax.third + s * ay.third)
        )
    }
}
