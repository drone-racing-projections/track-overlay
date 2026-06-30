package com.gaterace.app.sim

import com.gaterace.app.geo.Gate
import com.gaterace.app.geo.Pose
import com.gaterace.app.geo.Track
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * Auto-fly for emulator demos: waypoint path behind each gate → center → past,
 * so race-box plane crossing registers.
 */
class SimFlight(private val track: Track) {
    var speed = 12.0
    private var pose: Pose
    private val waypoints = mutableListOf<Triple<Double, Double, Double>>()
    private var wpIdx = 0

    init {
        val standoff = 35.0
        for (g in track.orderedGates()) {
            val (ne, nn, nu) = g.normal()
            waypoints += Triple(g.e - ne * standoff, g.n - nn * standoff, g.u + 1.0)
            waypoints += Triple(g.e, g.n, g.u)
            waypoints += Triple(g.e + ne * 8.0, g.n + nn * 8.0, g.u)
        }
        val (e0, n0, u0) = waypoints.first()
        pose = Pose(t = 0.0, e = e0, n = n0, u = u0, yawDeg = 0.0, gimbalPitchDeg = -8.0)
    }

    fun current() = pose

    fun boost() { speed = (speed + 3.0).coerceAtMost(28.0) }

    fun tick(dt: Double, nextGateId: String?) {
        if (waypoints.isEmpty()) return
        val (te, tn, tu) = waypoints[wpIdx.coerceAtMost(waypoints.lastIndex)]
        val de = te - pose.e
        val dn = tn - pose.n
        val du = tu - pose.u
        val dist = sqrt(de * de + dn * dn + du * du).coerceAtLeast(0.01)
        val yaw = Math.toDegrees(atan2(de, dn))
        val step = minOf(speed * dt, dist)
        pose = pose.copy(
            t = pose.t + dt,
            e = pose.e + de / dist * step,
            n = pose.n + dn / dist * step,
            u = pose.u + du / dist * step,
            yawDeg = yaw,
            gimbalPitchDeg = -8.0
        )
        if (dist < 2.0 && wpIdx < waypoints.lastIndex) wpIdx++
    }
}
