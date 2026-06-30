package com.gaterace.app.race

import com.gaterace.app.geo.Pose
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

data class SessionState(
    val track: String = "",
    val state: String = "idle",
    val gatesHit: List<String> = emptyList(),
    val nextGateId: String? = null,
    val elapsedS: Double? = null,
    val finished: Boolean = false,
    val tStart: Double? = null,
    val tFinish: Double? = null,
    val pilotId: String? = null,
    val heatId: String? = null,
    val lastPoseT: Double? = null
)

sealed class ConnState {
    data object Connecting : ConnState()
    data object Connected : ConnState()
    data class Error(val message: String) : ConnState()
    data object Disconnected : ConnState()
}

class RaceClient(
    private var baseUrl: String,
    private val scope: CoroutineScope,
    private val onSession: (SessionState) -> Unit,
    private val onConn: (ConnState) -> Unit = {},
    private val onError: (String) -> Unit = {}
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(3, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS)
        .pingInterval(20, TimeUnit.SECONDS)
        .build()
    private val jsonType = "application/json; charset=utf-8".toMediaType()
    private var ws: WebSocket? = null
    private val latest = AtomicReference(SessionState())
    private val connected = AtomicBoolean(false)
    private var reconnectJob: Job? = null
    private var pilotId: String = "pilot1"
    @Volatile private var closed = false

    fun setPilotId(id: String) { pilotId = id.ifBlank { "pilot1" } }

    fun setBaseUrl(url: String) {
        baseUrl = url.trimEnd('/')
        reconnect()
    }

    fun baseUrl(): String = baseUrl

    private fun wsUrl(): String {
        // OkHttp HttpUrl only allows http(s) schemes — build ws URL as a string
        val http = baseUrl.toHttpUrlOrNull()
        if (http != null) {
            val scheme = if (http.isHttps) "wss" else "ws"
            val port = when {
                http.isHttps && http.port == 443 -> ""
                !http.isHttps && http.port == 80 -> ""
                else -> ":${http.port}"
            }
            return "$scheme://${http.host}$port/ws"
        }
        val trimmed = baseUrl.trimEnd('/')
        return when {
            trimmed.startsWith("https://") -> "wss://" + trimmed.removePrefix("https://") + "/ws"
            trimmed.startsWith("http://") -> "ws://" + trimmed.removePrefix("http://") + "/ws"
            else -> "ws://$trimmed/ws"
        }
    }

    fun reconnect() {
        if (closed) return
        ws?.close(1000, "reconnect")
        ws = null
        connected.set(false)
        onConn(ConnState.Connecting)
        reconnectJob?.cancel()
        val req = Request.Builder().url(wsUrl()).build()
        ws = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                connected.set(true)
                onConn(ConnState.Connected)
                webSocket.send(JSONObject().put("type", "hello").put("pilot_id", pilotId).toString())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val msg = JSONObject(text)
                    when (msg.getString("type")) {
                        "session" -> applySessionJson(msg.getJSONObject("payload"))
                        "error" -> {
                            val err = msg.getJSONObject("payload").optString("error", "error")
                            onError(err)
                        }
                        "finish" -> {
                            val fin = msg.getJSONObject("payload")
                            val cur = latest.get()
                            val hits = buildList {
                                val arr = fin.optJSONArray("gates_hit")
                                if (arr != null) for (i in 0 until arr.length()) add(arr.getString(i))
                                else addAll(cur.gatesHit)
                            }
                            val s = cur.copy(
                                state = "finished",
                                finished = true,
                                elapsedS = if (fin.has("elapsed_s")) fin.optDouble("elapsed_s") else cur.elapsedS,
                                gatesHit = hits,
                                pilotId = if (fin.has("pilot_id")) fin.optString("pilot_id") else cur.pilotId,
                                heatId = if (fin.has("heat_id")) fin.optString("heat_id") else cur.heatId
                            )
                            latest.set(s)
                            onSession(s)
                        }
                        "pass" -> { /* session updates carry hits */ }
                    }
                } catch (e: Exception) {
                    onError("ws parse: ${e.message}")
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                connected.set(false)
                onConn(ConnState.Error(t.message ?: "ws failure"))
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                connected.set(false)
                onConn(ConnState.Disconnected)
                if (!closed) scheduleReconnect()
            }
        })
        scope.launch(Dispatchers.IO) {
            try {
                val r = client.newCall(Request.Builder().url("$baseUrl/session").get().build()).execute()
                r.body?.string()?.let { applySessionJson(JSONObject(it)) }
            } catch (e: Exception) {
                onError("session poll: ${e.message}")
            }
        }
    }

    private fun scheduleReconnect() {
        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            delay(1500)
            if (!closed && !connected.get()) reconnect()
        }
    }

    private fun applySessionJson(p: JSONObject) {
        val hits = mutableListOf<String>()
        val arr = p.optJSONArray("gates_hit")
        if (arr != null) for (i in 0 until arr.length()) hits += arr.getString(i)
        val s = SessionState(
            track = p.optString("track"),
            state = p.optString("state"),
            gatesHit = hits,
            nextGateId = if (p.isNull("next_gate_id")) null else p.optString("next_gate_id"),
            elapsedS = if (p.has("elapsed_s") && !p.isNull("elapsed_s")) p.optDouble("elapsed_s") else null,
            finished = p.optBoolean("finished"),
            tStart = if (p.has("t_start") && !p.isNull("t_start")) p.optDouble("t_start") else null,
            tFinish = if (p.has("t_finish") && !p.isNull("t_finish")) p.optDouble("t_finish") else null,
            pilotId = if (p.has("pilot_id") && !p.isNull("pilot_id")) p.optString("pilot_id") else null,
            heatId = if (p.has("heat_id") && !p.isNull("heat_id")) p.optString("heat_id") else null,
            lastPoseT = if (p.has("last_pose_t") && !p.isNull("last_pose_t")) p.optDouble("last_pose_t") else null
        )
        latest.set(s)
        onSession(s)
    }

    fun arm(track: String = "demo_field") {
        scope.launch(Dispatchers.IO) {
            try {
                val body = JSONObject().put("track", track).put("pilot_id", pilotId)
                    .toString().toRequestBody(jsonType)
                val r = client.newCall(
                    Request.Builder().url("$baseUrl/session/arm").post(body).build()
                ).execute()
                val text = r.body?.string()
                if (!r.isSuccessful) {
                    onError("arm HTTP ${r.code}: ${text ?: ""}")
                    return@launch
                }
                text?.let { applySessionJson(JSONObject(it)) }
            } catch (e: Exception) {
                onError("arm failed: ${e.message}")
            }
        }
    }

    fun sendTelemetry(pose: Pose) {
        // Always attempt; server returns 409 when finished / ownership mismatch (surfaces via onError)
        scope.launch(Dispatchers.IO) {
            try {
                val o = JSONObject()
                    .put("t", pose.t)
                    .put("e", pose.e)
                    .put("n", pose.n)
                    .put("u", pose.u)
                    .put("yaw_deg", pose.yawDeg)
                    .put("pitch_deg", pose.pitchDeg)
                    .put("roll_deg", pose.rollDeg)
                    .put("pilot_id", pilotId)
                pose.gimbalPitchDeg?.let { o.put("gimbal_pitch_deg", it) }
                pose.gimbalYawDeg?.let { o.put("gimbal_yaw_deg", it) }
                val sent = connected.get() && ws?.send(
                    JSONObject().put("type", "telemetry").put("payload", o).toString()
                ) == true
                if (!sent) {
                    val body = o.toString().toRequestBody(jsonType)
                    val r = client.newCall(
                        Request.Builder().url("$baseUrl/telemetry").post(body).build()
                    ).execute()
                    val text = r.body?.string()
                    if (r.code == 409) {
                        // finished or ownership — surface once
                        try {
                            val err = JSONObject(text ?: "{}")
                            onError(err.optString("error", "telemetry rejected"))
                            if (err.has("session")) applySessionJson(err.getJSONObject("session"))
                        } catch (_: Exception) {
                            onError("telemetry HTTP 409")
                        }
                        return@launch
                    }
                    if (!r.isSuccessful) {
                        onError("telemetry HTTP ${r.code}")
                        return@launch
                    }
                    text?.let { applySessionJson(JSONObject(it)) }
                }
            } catch (e: Exception) {
                onError("telemetry: ${e.message}")
            }
        }
    }

    fun current() = latest.get()
    fun isConnected() = connected.get()

    fun shutdown() {
        closed = true
        reconnectJob?.cancel()
        ws?.close(1000, "shutdown")
    }
}
