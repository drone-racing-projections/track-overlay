package com.gaterace.app.geo

import android.content.Context
import org.json.JSONObject

object TrackLoader {
    fun fromAssets(context: Context, name: String = "demo_field"): Track {
        val json = context.assets.open("tracks/$name.json").bufferedReader().use { it.readText() }
        return fromJson(json)
    }

    fun fromJson(json: String): Track {
        val o = JSONObject(json)
        val origin = o.getJSONObject("origin")
        val gatesJson = o.getJSONArray("gates")
        val gates = mutableListOf<Gate>()
        for (i in 0 until gatesJson.length()) {
            val g = gatesJson.getJSONObject(i)
            gates += Gate(
                id = g.getString("id"),
                e = g.getDouble("e"),
                n = g.getDouble("n"),
                u = g.getDouble("u"),
                normalE = g.getDouble("normal_e"),
                normalN = g.getDouble("normal_n"),
                normalU = g.optDouble("normal_u", 0.0),
                radiusM = g.optDouble("radius_m", 10.0),
                thicknessM = g.optDouble("thickness_m", 3.0),
                sequence = g.optInt("sequence", i),
                name = g.optString("name", "")
            )
        }
        return Track(
            name = o.getString("name"),
            origin = TrackOrigin(
                origin.getDouble("lat_deg"),
                origin.getDouble("lon_deg"),
                origin.optDouble("alt_m", 0.0)
            ),
            gates = gates,
            description = o.optString("description", "")
        )
    }
}
