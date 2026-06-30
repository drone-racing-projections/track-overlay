package com.gaterace.app.dji

/**
 * Real aircraft integration checklist (not linked in SIM builds):
 *
 * 1. Register at developer.dji.com — MSDK V5 key for applicationId com.gaterace.app
 * 2. Add MSDK AAR from Mobile-SDK-Android-V5 sample; set SIM_MODE=false in build.gradle.kts
 * 3. Init SDK with API key; liveview SurfaceView under GateOverlayView (or GL composite)
 * 4. Pose: KeyAircraftLocation3D + attitude + gimbal → TrackOrigin.toEnu → Pose(t=phone_monotonic, …)
 * 5. Use same phone_monotonic `t` for all telemetry in a heat (reset on Arm)
 * 6. Never send pilot video to race box
 * 7. Field race box URL: set in UI prefs (LAN IP), not 10.0.2.2
 *
 * Spike order: telemetry-only app → overlay on black → overlay on liveview → latency clap test.
 *
 * Spectator (optional, delayed): publish a secondary RTMP copy to
 * rtmp://<race-box-lan-ip>:1935/live/pilot — see docs/SPECTATOR.md.
 * Never use that stream as the pilot display.
 */
object DjiIntegrationNotes
