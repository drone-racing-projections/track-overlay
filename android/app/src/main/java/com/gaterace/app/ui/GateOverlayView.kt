package com.gaterace.app.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import com.gaterace.app.geo.*

class GateOverlayView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
    private var track: Track? = null
    private var pose: Pose? = null
    private var nextGateId: String? = null

    private val paintActive = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(0, 255, 80)
        style = Paint.Style.STROKE
        strokeWidth = 8f
    }
    private val paintIdle = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(0, 160, 255)
        style = Paint.Style.STROKE
        strokeWidth = 4f
    }
    private val paintText = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        textSize = 36f
    }
    private val paintBg = Paint().apply { color = Color.rgb(30, 45, 70) }
    private val paintGround = Paint().apply { color = Color.rgb(35, 70, 40) }

    fun setTrack(t: Track) { track = t; invalidate() }
    fun setPose(p: Pose, nextId: String?) {
        pose = p
        nextGateId = nextId
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val w = width
        val h = height
        // Synthetic horizon (SIM feed stand-in for liveview)
        val p = pose
        val pitch = p?.gimbalPitchDeg ?: p?.pitchDeg ?: 0.0
        val horizon = (h / 2 + pitch * 8).toInt().coerceIn(0, h)
        canvas.drawRect(0f, 0f, w.toFloat(), horizon.toFloat(), paintBg)
        canvas.drawRect(0f, horizon.toFloat(), w.toFloat(), h.toFloat(), paintGround)

        val tr = track ?: return
        val poseNow = p ?: return
        for (g in tr.orderedGates()) {
            val ring = gateRingPoints(g, 64)
            val proj = projectPoints(poseNow, ring, w, h, 72.0)
            val paint = if (g.id == nextGateId) paintActive else paintIdle
            for (i in proj.indices) {
                val a = proj[i] ?: continue
                val b = proj[(i + 1) % proj.size] ?: continue
                canvas.drawLine(a.first, a.second, b.first, b.second, paint)
            }
            val c = projectPoints(poseNow, listOf(g.center()), w, h)[0]
            if (c != null) {
                canvas.drawText(g.name.ifEmpty { g.id }, c.first - 20f, c.second, paintText)
            }
        }
    }
}
