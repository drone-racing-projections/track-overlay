package com.gaterace.app.geo

import kotlin.math.*

private const val A = 6378137.0
private const val F = 1.0 / 298.257223563
private val E2 = F * (2 - F)

private fun latLonToEcef(latDeg: Double, lonDeg: Double, altM: Double): Triple<Double, Double, Double> {
    val lat = Math.toRadians(latDeg)
    val lon = Math.toRadians(lonDeg)
    val sL = sin(lat); val cL = cos(lat)
    val sO = sin(lon); val cO = cos(lon)
    val n = A / sqrt(1 - E2 * sL * sL)
    val x = (n + altM) * cL * cO
    val y = (n + altM) * cL * sO
    val z = (n * (1 - E2) + altM) * sL
    return Triple(x, y, z)
}

fun enuFromLlh(
    lat0: Double, lon0: Double, alt0: Double,
    lat: Double, lon: Double, alt: Double
): Triple<Double, Double, Double> {
    val (x0, y0, z0) = latLonToEcef(lat0, lon0, alt0)
    val (x, y, z) = latLonToEcef(lat, lon, alt)
    val dx = x - x0; val dy = y - y0; val dz = z - z0
    val lat0r = Math.toRadians(lat0)
    val lon0r = Math.toRadians(lon0)
    val sL = sin(lat0r); val cL = cos(lat0r)
    val sO = sin(lon0r); val cO = cos(lon0r)
    val e = -sO * dx + cO * dy
    val n = -sL * cO * dx - sL * sO * dy + cL * dz
    val u = cL * cO * dx + cL * sO * dy + sL * dz
    return Triple(e, n, u)
}
