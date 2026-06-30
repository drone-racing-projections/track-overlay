package com.gaterace.app.ui

import android.content.Context
import android.os.Bundle
import android.os.SystemClock
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.gaterace.app.BuildConfig
import com.gaterace.app.R
import com.gaterace.app.geo.TrackLoader
import com.gaterace.app.race.ConnState
import com.gaterace.app.race.RaceClient
import com.gaterace.app.race.SessionState
import com.gaterace.app.sim.SimFlight
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * GateRace main UI.
 *
 * SIM_MODE=true: synthetic world + Layer-1 ring projection.
 * Race box URL editable (prefs); default emulator host 10.0.2.2 or LAN IP on phone.
 *
 * Clock: pose.t is phone-monotonic seconds from app start of sim flight (reset on Arm via new SimFlight).
 */
class MainActivity : AppCompatActivity() {
    private lateinit var overlay: GateOverlayView
    private lateinit var hudTop: TextView
    private lateinit var hudTimer: TextView
    private lateinit var hudConn: TextView
    private lateinit var hudErr: TextView
    private lateinit var editUrl: EditText
    private lateinit var editPilot: EditText
    private lateinit var race: RaceClient
    private var session = SessionState()
    private var sim: SimFlight? = null
    private var lastTelemetryUptime = 0L
    private var lastError: String? = null
    private var connLabel = "…"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        overlay = findViewById(R.id.overlay)
        hudTop = findViewById(R.id.hudTop)
        hudTimer = findViewById(R.id.hudTimer)
        hudConn = findViewById(R.id.hudConn)
        hudErr = findViewById(R.id.hudErr)
        editUrl = findViewById(R.id.editUrl)
        editPilot = findViewById(R.id.editPilot)

        val prefs = getSharedPreferences("gaterace", Context.MODE_PRIVATE)
        val defaultUrl = prefs.getString("race_box_url", BuildConfig.DEFAULT_RACE_BOX)
            ?: BuildConfig.DEFAULT_RACE_BOX
        val defaultPilot = prefs.getString("pilot_id", "pilot1") ?: "pilot1"
        editUrl.setText(defaultUrl)
        editPilot.setText(defaultPilot)

        val track = TrackLoader.fromAssets(this, "demo_field")
        overlay.setTrack(track)
        sim = SimFlight(track)

        race = RaceClient(
            baseUrl = defaultUrl.trimEnd('/'),
            scope = lifecycleScope,
            onSession = { s ->
                runOnUiThread {
                    session = s
                    updateHud()
                }
            },
            onConn = { c ->
                runOnUiThread {
                    connLabel = when (c) {
                        is ConnState.Connected -> "WS ok"
                        is ConnState.Connecting -> "connecting…"
                        is ConnState.Disconnected -> "disconnected"
                        is ConnState.Error -> "err ${c.message}"
                    }
                    updateHud()
                }
            },
            onError = { msg ->
                runOnUiThread {
                    lastError = msg
                    updateHud()
                }
            }
        )
        race.setPilotId(defaultPilot)
        race.reconnect()

        findViewById<Button>(R.id.btnArm).setOnClickListener {
            val url = editUrl.text.toString().trim().trimEnd('/')
            val pilot = editPilot.text.toString().trim().ifBlank { "pilot1" }
            prefs.edit().putString("race_box_url", url).putString("pilot_id", pilot).apply()
            race.setPilotId(pilot)
            if (url != race.baseUrl()) race.setBaseUrl(url)
            // Reset sim clock for new heat (phone_monotonic from 0)
            sim = SimFlight(track)
            race.arm("demo_field")
            lastError = null
        }
        findViewById<Button>(R.id.btnSimBoost).setOnClickListener { sim?.boost() }
        findViewById<Button>(R.id.btnReconnect).setOnClickListener {
            val url = editUrl.text.toString().trim().trimEnd('/')
            prefs.edit().putString("race_box_url", url).apply()
            race.setBaseUrl(url)
        }

        lifecycleScope.launch {
            var last = SystemClock.elapsedRealtime()
            while (isActive) {
                val now = SystemClock.elapsedRealtime()
                val dt = ((now - last) / 1000.0).coerceIn(0.0, 0.05)
                last = now
                val flight = sim ?: continue
                flight.tick(dt, session.nextGateId)
                val pose = flight.current()
                overlay.setPose(pose, session.nextGateId)
                if (!session.finished && now - lastTelemetryUptime > 80) {
                    lastTelemetryUptime = now
                    race.sendTelemetry(pose)
                }
                updateHud(pose.t)
                delay(16)
            }
        }
        updateHud()
    }

    override fun onDestroy() {
        if (::race.isInitialized) race.shutdown()
        super.onDestroy()
    }

    private fun updateHud(poseT: Double? = null) {
        val mode = if (BuildConfig.SIM_MODE) "SIM" else "DJI"
        hudConn.text = connLabel
        hudTop.text = "$mode  ${session.state}  next=${session.nextGateId ?: "—"}  hits=${session.gatesHit.joinToString(",")}"
        hudErr.text = lastError ?: ""
        when {
            session.finished && session.elapsedS != null ->
                hudTimer.text = "FINISH ${"%.2f".format(session.elapsedS)}s — Arm for next"
            session.state == "running" && session.elapsedS != null ->
                hudTimer.text = "%.2f s".format(session.elapsedS)
            session.tStart != null && poseT != null && session.state == "running" ->
                hudTimer.text = "%.2f s".format(poseT - session.tStart!!)
            session.state == "armed" ->
                hudTimer.text = "armed"
            session.elapsedS != null ->
                hudTimer.text = "%.2f s".format(session.elapsedS)
            else -> hudTimer.text = "—"
        }
    }
}
