package com.gaterace.app.geo

data class TrackOrigin(val latDeg: Double, val lonDeg: Double, val altM: Double = 0.0)

data class Gate(
    val id: String,
    val e: Double,
    val n: Double,
    val u: Double,
    val normalE: Double,
    val normalN: Double,
    val normalU: Double = 0.0,
    val radiusM: Double = 10.0,
    val thicknessM: Double = 3.0,
    val sequence: Int = 0,
    val name: String = ""
) {
    fun center() = Triple(e, n, u)
    fun normal(): Triple<Double, Double, Double> {
        val mag = kotlin.math.sqrt(normalE * normalE + normalN * normalN + normalU * normalU).coerceAtLeast(1e-9)
        return Triple(normalE / mag, normalN / mag, normalU / mag)
    }
}

data class Track(
    val name: String,
    val origin: TrackOrigin,
    val gates: List<Gate>,
    val description: String = ""
) {
    fun orderedGates() = gates.sortedBy { it.sequence }
}

data class Pose(
    val t: Double,
    val e: Double,
    val n: Double,
    val u: Double,
    val yawDeg: Double = 0.0,
    val pitchDeg: Double = 0.0,
    val rollDeg: Double = 0.0,
    val gimbalPitchDeg: Double? = null,
    val gimbalYawDeg: Double? = null
)
