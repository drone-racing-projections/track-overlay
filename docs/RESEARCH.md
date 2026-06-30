# Research notes

Optional background. Safe to skip if you only want to run or extend the current design.

## Options considered for v1

| Option | Idea | Role in v1 |
|--------|------|------------|
| **A. MSDK app on phone** | AR on live view; race box scores | Primary approach |
| **B. Ground compositor** | Capture HDMI, overlay on a PC | Useful for spectators; weak pilot latency |
| **C. Open FPV + companion computer** | Custom air stack | Maximum control; not “buy DJI and go” |
| **D. Goggles + ground scoring only** | No AR in pilot eyes | Different product |
| **E. Enterprise DJI + RTK** | Higher cost / accuracy | Later or budget-dependent |

Cloud livestream protocols are fine for audiences, not for piloting AR.

Track maths and race state (`track_core`, `race_box`) stay reusable if video sources change later. Locked product choices are summarized in [HOW_IT_WORKS.md](HOW_IT_WORKS.md).
