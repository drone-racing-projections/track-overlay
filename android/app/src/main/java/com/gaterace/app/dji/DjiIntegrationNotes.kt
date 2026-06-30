package com.gaterace.app.dji

/**
 * Field integration checklist (not linked in SIM builds):
 *
 * 1. MSDK V5 app key for applicationId com.gaterace.app (developer.dji.com)
 * 2. Add MSDK AAR; set SIM_MODE=false in build.gradle.kts
 * 3. Init SDK; liveview under or composited with GateOverlayView
 * 4. Pose from aircraft/gimbal keys → track ENU → Pose(t = phone heat time)
 * 5. RC ↔ phone over USB on phone-centric remotes (OTG / USB prompts as on stock DJI apps)
 * 6. Optional delayed spectator RTMP to the race box — docs/SPECTATOR.md
 * 7. Race box URL on the field LAN (not 10.0.2.2)
 *
 * Spike order: telemetry-only → overlay on black → overlay on liveview → latency check
 */
object DjiIntegrationNotes
