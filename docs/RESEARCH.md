# Research notes (optional)

Alternatives we considered before locking the design in [HOW_IT_WORKS.md](HOW_IT_WORKS.md). You can ignore this for building or flying.

## Options in short

| Option | Idea | Verdict for v1 |
|--------|------|----------------|
| **A. MSDK app on phone** | AR on liveview; race box scores | **Chosen** |
| **B. Ground compositor** | Capture HDMI, overlay on PC | OK for **spectators**, bad latency for **pilots** |
| **C. Open FPV + companion computer** | Full custom stack | Max control, not “buy DJI and go” |
| **D. Goggles + ground scoring only** | No AR in pilot eyes | Different product |
| **E. Enterprise DJI + RTK** | Higher cost/accuracy | Later / budget dependent |

Livestream protocols (RTMP to cloud, etc.) are fine for audiences, not for piloting AR.

Track maths and race state (`track_core`, `race_box`) stay usable if we later add B or C for video.
