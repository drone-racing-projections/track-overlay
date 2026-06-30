# How this works (read this like a person, not a protocol)

## The 30-second version

You get a **DJI-style drone with a camera**. The drone sends video and flight data to the **remote controller over radio** (DJI’s link — not Wi‑Fi to your laptop).

You **plug the controller into your phone with a USB cable** (the short cable that came with the RC, or the matching Lightning / USB‑C / Micro‑USB one). Your phone is mounted on the controller.

You open **GateRace** (our app) instead of only using the stock Fly app. The phone now shows the live camera feed **and** floating race gates. You fly through the gates. A laptop on the field keeps official time over normal Wi‑Fi.

That’s the product.

```
  [ Drone + camera ]
         │
         │  radio (video + telemetry to the RC)
         ▼
  [ Remote controller ] ---- USB cable ---- [ Your phone ]
                                              │
                                              │  GateRace draws gates on the live video
                                              │
                          light Wi‑Fi data ───┼──► [ Laptop = race box = official times ]
                                              │
                         optional delayed TV ─┘    (never for flying)
```

USB is not a footnote. **No USB (or equivalent link) between RC and phone → no live view in our app on a phone-centric controller.** That’s how DJI’s “phone as screen” remotes work in the real world: the cable is how the phone gets the stream and talks to the aircraft stack, with the app asking for the usual USB / file-transfer / OTG permissions on Android.

(If you use a remote that already has its own screen, that’s a different setup — our v1 target is **phone on the RC**, USB in, app on the phone.)

---

## What you actually experience as a pilot

1. Charge the drone and the controller. Put your **normal phone** in the clamp (sun hood helps outdoors).  
2. Power on aircraft + RC. **Plug USB** from RC into the phone. Accept the phone’s USB/OTG prompt if it asks.  
3. Open GateRace. Connect / wait until you see live video.  
4. On the laptop, someone hits **Arm** for your heat (or you do it from the app).  
5. Fly through the rings in order. You hear/see passes. Land. Look at the time on the phone or on the laptop screen.

You did not set up a video server. You did not “stream to the cloud to pilot.” You plugged in USB and flew.

---

## What each box is for (still human)

| Thing | Job | What it’s *not* |
|-------|-----|------------------|
| **Drone** | Camera in the sky + flies where you point it | Not running our app |
| **Remote (RC)** | Sticks + radio to the drone; **USB to the phone** | Not the race computer |
| **Phone + GateRace** | Live video **for your eyes** + drawing gates + sending small position updates over Wi‑Fi | Not the official stopwatch for the event |
| **Laptop (race box)** | Official times, leaderboard, optional TV/internet video for **spectators** | Not something you stare at to fly |
| **USB cable RC → phone** | Carries the live link the app needs on phone-centric RCs | Not optional decoration |

Spectators (people on a TV or online) can watch a **delayed** copy later. That’s a different pipe. **You never fly by looking at the TV.**

---

## Why we obsess over “don’t send pilot video to the laptop”

If the picture you fly on goes phone → Wi‑Fi → laptop → back, it feels late. Gates swim. It’s not fun and it’s less safe.

So:

- **Eyes / flying:** phone, fed from the RC over **USB**, video from the drone over **radio**.  
- **Scorekeeping:** tiny messages on Wi‑Fi to the laptop.  
- **Audience:** optional delayed video; laptop may help redistribute that.

---

## Smart glasses — can we plug those in too?

Short answer: **maybe for showing the same picture, but it’s not “USB next to the DJI cable” on one phone port without homework.** We checked how these devices actually connect; we are not inventing a magic Y-cable.

### What most “AR / XR display glasses” really are

Products like **Xreal**, **Viture**, and similar **USB‑C glasses** usually behave like a **monitor for your phone**, not like a second DJI receiver.

They want the phone’s USB‑C port in **DisplayPort Alt Mode** — the phone **outputs video** over USB‑C. Vendors and compatibility guides are explicit that phones need **DP Alt Mode** (or an approved adapter path); many phones don’t have it.

So the glasses are saying: *“Mirror or extend the phone screen into my lenses.”*  
If GateRace is full-screen on the phone, the glasses can show **that same GateRace picture** — live video + gates — *if* the phone can drive the glasses.

### What the DJI RC cable needs

Phone-centric DJI remotes use a **USB data/OTG-style link** so the phone runs the flight app and receives live view from the controller. DJI’s own cables and support docs describe connecting the RC to the phone over USB; Android often needs the right cable, OTG, and the USB mode prompt (charge vs file transfer / debugging depending on device).

So the RC is saying: *“Phone, you’re the computer; I’m plugged in as a USB device / link.”*

### The awkward part: one USB‑C port, two jobs

Typical phones have **one** USB‑C port.

| Plug | Phone role |
|------|------------|
| DJI RC cable | Phone acts as **USB host / OTG** toward the controller |
| Xreal / Viture–class glasses | Phone acts as **video source** (DisplayPort Alt Mode **out**) |

Those are different uses of the port. You generally **cannot** assume one cable does both at once. Public compatibility threads for Viture/Xreal are full of “my phone has no DP Alt Mode” and adapter questions — not “and also leave OTG free for a drone RC.”

### Ways that *can* work (research-backed patterns, not guarantees)

1. **Glasses mirror GateRace, DJI on the same phone, only if your hardware allows both roles somehow**  
   Rare: phones with **two USB‑C ports**, or a dock that officially supports **host + display** at once (uncommon; verify per device — don’t buy on hope).

2. **Phone does DJI + GateRace on the built-in screen; glasses are a second display only when you’re not relying on one port for the RC**  
   Example mental model: RC linked as usual; if you unplug glasses vs RC you’re choosing. Not great in flight.

3. **Charge-and-play / splitter accessories (common in glasses ecosystems)**  
   Xreal/Viture users often use **USB‑C adapters that pass video to the glasses and add charging**. Those solve *power + glasses*, not *glasses + DJI OTG on one phone*. Different problem.

4. **Wireless glasses / phone casting**  
   Some glasses/ecosystems lean on apps and wireless links. Fine for media; **extra delay** is risky for piloting. We would only treat that as experimental for racing.

5. **Best honest product angle for GateRace + glasses**  
   - GateRace runs on the **phone** (USB to DJI RC as today).  
   - If the pilot’s phone supports **DP Alt Mode**, plug **USB‑C glasses** into a setup that can show the phone’s screen (possibly via a **supported** hub/dock **documented for that phone + glasses pair**).  
   - Treat glasses as **“big FPV goggles that are really an external monitor for GateRace”**, not as a second flight receiver.  
   - Validate **latency and brightness outdoors** before promising race use. Sunlight and DP Alt Mode flakiness are real.

6. **What we are *not* claiming**  
   - That Meta-style **Bluetooth AI glasses** (camera/mic heavy, not full DP FPV monitors) are a drop-in FPV race display.  
   - That any USB‑C glasses work with any phone while the DJI cable is also attached.  
   - That DJI’s radio terminates in the glasses. It doesn’t: **radio → RC → USB → phone → (optional) video out → glasses.**

### Practical recommendation

| Goal | Approach |
|------|----------|
| Ship v1 racing | Phone on RC, **USB RC→phone**, GateRace on the phone screen. Ignore glasses. |
| Try glasses | Buy glasses only after checking **your phone’s DP Alt Mode** on the vendor’s list; try GateRace full screen mirrored to glasses **on the bench** before the field; solve the **second plug** problem (dock / second port / sequence) deliberately. |
| Event “wow” for spectators | Use the **race box spectator** path (TV), not glasses on bystanders’ faces, unless you equip them on purpose. |

If we later adopt glasses as a first-class pilot display, the engineering work is: **confirm phone can host DJI link and output video concurrently (or use a tiny companion display path)** — not more race maths. The race box stays the same.

---

## One heat, one flyer feeding the laptop

The laptop trusts **one** telemetry stream per heat (your phone). Don’t also run the fake “drone on the laptop” tool against the same heat.

Time for scoring is “seconds since this heat on the phone,” not the wall clock on the TV.

---

## What’s built vs what’s still “real DJI”

| Works in this repo today | Still needs DJI developer bits / aircraft |
|--------------------------|-------------------------------------------|
| Race box times a heat | Official MSDK live video in GateRace |
| Fake telemetry / Android simulator | USB to a real RC with MSDK permissions |
| Director page, leaderboard | Field calibration on real GPS noise |
| Spectator demo video through the laptop | Phone publishing a delayed copy for TV |

The **story** above is the real product. The **simulator** is how we practice the story without a drone.

---

## Next

- Plug things in and run software: [START.md](START.md)  
- What to buy (USB cable included in the RC kit): [HARDWARE.md](HARDWARE.md)  
- Laptop API (for programmers): [API.md](API.md)  
