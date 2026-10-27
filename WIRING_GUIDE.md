# 6-Transducer Acoustic Levitator — Complete Wiring & Pinout Guide

> **CORRECTED WIRING — Cross-Pair Architecture**
>
> **Rule:** A **Top** transducer and a **Bottom** transducer at the **same position** (e.g., Top Tx1 + Bottom Tx1) **MAY** share the same L293D bridge output — the geometry of opposing faces creates the acoustic opposition.
>
> **Two transducers from the SAME array (both top OR both bottom) MUST NOT share a bridge output.** This would short their drive signals and prevent individual standing-wave control.

---

## 1. Power Distribution & Rail Architecture

### Primary Power Sources
* **12V DC Input ($\ge 1.5\text{A}$):**
  * Connect $12\text{V (+)}$ to **LM2596 `IN+`**.
  * Connect $12\text{V (-)}$ to **Common Ground** (LM2596 `IN-`).
* **LM2596 Buck Converter Setup:**
  * Adjust the potentiometer until `OUT+` reads **precisely $5.0\text{V DC}$**.
  * Connect `OUT+` ($5.0\text{V}$) to the **5V Logic Rail**.
  * Connect `OUT-` to the **Common Ground Rail**.

### Power Rail Bus Distribution
| Rail Name | Voltage | Destinations |
| :--- | :--- | :--- |
| **12V Motor Rail** | $+12\text{V}$ | L293D Pin 8 (`VCC2`) on IC 1 and IC 2 |
| **5V Logic Rail** | $+5.0\text{V}$ | ESP32 `VIN` / `5V` pin<br>L293D Pin 16 (`VCC1`) on IC 1 and IC 2<br>L293D Pin 1 (`1,2EN`) and Pin 9 (`3,4EN`) on IC 1 and IC 2 |
| **Common GND** | $0\text{V}$ | LM2596 `IN-` and `OUT-`<br>ESP32 `GND` pins<br>L293D Pins 4, 5, 12, 13 on IC 1 and IC 2 |

### Decoupling Capacitors
* One **$470\text{ }\mu\text{F}$ electrolytic** between the $+12\text{V}$ rail and GND near each IC's power pins.
* One **$0.1\text{ }\mu\text{F}$ (100nF) ceramic** directly across Pin 8 (`VCC2`) and GND of each L293D.

---

## 2. ESP32 Signal Control Lines

The firmware generates 4 hardware-synchronized PWM signals (one timer, 4 phase-shifted channels):

| ESP32 Pin | Signal Label | Phase | Connected To |
| :--- | :--- | :--- | :--- |
| **GPIO 4**  | `IC1_SIG_A` | $0°$ (reference)        | **IC 1** Pins 2 (`1A`) & 15 (`4A`) |
| **GPIO 5**  | `IC1_SIG_B` | $180°$ (push-pull)      | **IC 1** Pins 7 (`2A`) & 10 (`3A`) |
| **GPIO 18** | `IC2_SIG_A` | $0°$ + Z-phase shift    | **IC 2** Pins 2 (`1A`) & 15 (`4A`) |
| **GPIO 19** | `IC2_SIG_B` | $180°$ + Z-phase shift  | **IC 2** Pins 7 (`2A`) & 10 (`3A`) |

The **standing wave** is created by the phase difference between IC1 (0° reference) and IC2 (Z-shifted). Adjusting `botPhaseTick` (0–255) moves the acoustic node up or down.

---

## 3. L293D Pinout Diagram (Top View, DIP-16)

```
                +---[ \/ ]---+
    1,2EN  (1) -|            |- (16) VCC1 (+5V Logic)
       1A  (2) -|            |- (15) 4A   (Input 4)
       1Y  (3) -|            |- (14) 4Y   (Output 4)
      GND  (4) -|   L293D    |- (13) GND
      GND  (5) -|            |- (12) GND
       2Y  (6) -|            |- (11) 3Y   (Output 3)
       2A  (7) -|            |- (10) 3A   (Input 3)
     VCC2  (8) -|            |- (9)  3,4EN (+5V Logic)
                +------------+
```

---

## 4. Complete Driver-by-Driver Connection Matrix

### IC 1 — Drives Tx1 Cross-Pair (Bridge 1) AND Tx2 Cross-Pair (Bridge 2)

**IC 1 operates at 0° reference phase (GPIO 4 / GPIO 5).**

* **Power & Enables:**
  * Pin 1  (`1,2EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 8  (`VCC2`)  $\rightarrow$ $+12\text{V}$ Motor Supply
  * Pin 9  (`3,4EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 16 (`VCC1`)  $\rightarrow$ $+5\text{V}$ Logic
  * Pins 4, 5, 12, 13 $\rightarrow$ Common `GND`
* **Signal Inputs (from ESP32):**
  * Pin 2  (`1A`) $\rightarrow$ ESP32 **GPIO 4** (`IC1_SIG_A` — 0° reference)
  * Pin 15 (`4A`) $\rightarrow$ ESP32 **GPIO 4** (`IC1_SIG_A` — 0° reference)
  * Pin 7  (`2A`) $\rightarrow$ ESP32 **GPIO 5** (`IC1_SIG_B` — 180° push-pull)
  * Pin 10 (`3A`) $\rightarrow$ ESP32 **GPIO 5** (`IC1_SIG_B` — 180° push-pull)

#### Bridge 1 — Top Tx1 ↔ Bottom Tx1 (cross-pair ✓)
> **Both** Top Transducer 1 and Bottom Transducer 1 connect to Bridge 1 outputs in parallel.
> This is the allowed cross-pair: one from the top array + one from the bottom array at the same position.

| Output Pin | Connected To |
| :--- | :--- |
| **Pin 3** (`1Y`) — positive drive | Top Transducer 1 Center Pin (+) |
| **Pin 3** (`1Y`) — positive drive | Bottom Transducer 1 Center Pin (+) &nbsp;⟵ cross-pair, parallel |
| **Pin 6** (`2Y`) — negative drive | Top Transducer 1 Outer Casing (−) |
| **Pin 6** (`2Y`) — negative drive | Bottom Transducer 1 Outer Casing (−) &nbsp;⟵ cross-pair, parallel |

#### Bridge 2 — Top Tx2 ↔ Bottom Tx2 (cross-pair ✓)
> Same logic: one top + one bottom at position 2 share Bridge 2.

| Output Pin | Connected To |
| :--- | :--- |
| **Pin 14** (`4Y`) — positive drive | Top Transducer 2 Center Pin (+) |
| **Pin 14** (`4Y`) — positive drive | Bottom Transducer 2 Center Pin (+) &nbsp;⟵ cross-pair, parallel |
| **Pin 11** (`3Y`) — negative drive | Top Transducer 2 Outer Casing (−) |
| **Pin 11** (`3Y`) — negative drive | Bottom Transducer 2 Outer Casing (−) &nbsp;⟵ cross-pair, parallel |

---

### IC 2 — Drives Tx3 Cross-Pair (Bridge 1 only; Bridge 2 unused)

**IC 2 operates at Z-phase shifted signal (GPIO 18 / GPIO 19).**

* **Power & Enables:**
  * Pin 1  (`1,2EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 8  (`VCC2`)  $\rightarrow$ $+12\text{V}$ Motor Supply
  * Pin 9  (`3,4EN`) $\rightarrow$ $+5\text{V}$ Logic *(enabled but Bridge 2 outputs left unconnected)*
  * Pin 16 (`VCC1`)  $\rightarrow$ $+5\text{V}$ Logic
  * Pins 4, 5, 12, 13 $\rightarrow$ Common `GND`
* **Signal Inputs (from ESP32):**
  * Pin 2  (`1A`) $\rightarrow$ ESP32 **GPIO 18** (`IC2_SIG_A` — 0°+Z shifted)
  * Pin 15 (`4A`) $\rightarrow$ ESP32 **GPIO 18** (`IC2_SIG_A` — 0°+Z shifted)
  * Pin 7  (`2A`) $\rightarrow$ ESP32 **GPIO 19** (`IC2_SIG_B` — 180°+Z shifted)
  * Pin 10 (`3A`) $\rightarrow$ ESP32 **GPIO 19** (`IC2_SIG_B` — 180°+Z shifted)

#### Bridge 1 — Top Tx3 ↔ Bottom Tx3 (cross-pair ✓)

| Output Pin | Connected To |
| :--- | :--- |
| **Pin 3** (`1Y`) — positive drive | Top Transducer 3 Center Pin (+) |
| **Pin 3** (`1Y`) — positive drive | Bottom Transducer 3 Center Pin (+) &nbsp;⟵ cross-pair, parallel |
| **Pin 6** (`2Y`) — negative drive | Top Transducer 3 Outer Casing (−) |
| **Pin 6** (`2Y`) — negative drive | Bottom Transducer 3 Outer Casing (−) &nbsp;⟵ cross-pair, parallel |

#### Bridge 2 — NOT USED
> Only 3 transducer cross-pairs are needed. IC 2's Bridge 2 (Pins 14, 11) is left unconnected.

---

## 5. Quick-Reference Summary Table

| IC & Bridge | GPIO Signals | Transducers Connected |
| :--- | :--- | :--- |
| **IC 1, Bridge 1** (Pins 3/6)   | GPIO 4 / GPIO 5  | **Top Tx1** (+/−) AND **Bottom Tx1** (+/−) — cross-pair ✓ |
| **IC 1, Bridge 2** (Pins 14/11) | GPIO 4 / GPIO 5  | **Top Tx2** (+/−) AND **Bottom Tx2** (+/−) — cross-pair ✓ |
| **IC 2, Bridge 1** (Pins 3/6)   | GPIO 18 / GPIO 19 | **Top Tx3** (+/−) AND **Bottom Tx3** (+/−) — cross-pair ✓ |
| **IC 2, Bridge 2** (Pins 14/11) | GPIO 18 / GPIO 19 | *NOT USED* |

---

## 6. What Was Wrong Before (and Why)

| ❌ Old (Incorrect) | ✅ New (Correct) |
| :--- | :--- |
| IC 1 = all 3 top transducers only | IC 1 = Tx1 cross-pair + Tx2 cross-pair (top + bottom mixed) |
| IC 2 = all 3 bottom transducers only | IC 2 = Tx3 cross-pair (top + bottom mixed) |
| Bridge 1 of IC 1: **Top Tx1 AND Top Tx2 in parallel** ← **ILLEGAL** (same array!) | Bridge 1 of IC 1: **Top Tx1 AND Bottom Tx1** ← ✓ cross-pair |
| Bridge 2 of IC 1: Top Tx3 alone (used only 1 of 2 bridge slots) | Bridge 2 of IC 1: **Top Tx2 AND Bottom Tx2** ← ✓ cross-pair |
| Bridge 1 of IC 2: **Bottom Tx1 AND Bottom Tx2 in parallel** ← **ILLEGAL** | Bridge 1 of IC 2: **Top Tx3 AND Bottom Tx3** ← ✓ cross-pair |
| Bridge 2 of IC 2: Bottom Tx3 alone | Bridge 2 of IC 2: Not used |

---

## 7. Physical Setup & Calibration

### Cavity Distance ($D$)
$$D = n \times 4.29\text{ mm}$$
* Recommended: **$n = 6 \implies D \approx 25.7\text{ mm}$** (in-phase mode) or **$n = 5 \implies D \approx 21.4\text{ mm}$** (anti-phase mode).

### Transducer Orientation
* **Top Transducers (Tx1, Tx2, Tx3):** Face **downward**.
* **Bottom Transducers (Tx1, Tx2, Tx3):** Face **upward**.
* Position each top/bottom pair (e.g., Top Tx1 above Bottom Tx1) to maximize wavefront overlap.

### Acoustic Particle Insertion
1. Power up and open Serial Monitor at **115200 baud**.
2. Press `?` to verify phase and IC states.
3. Place a ~1.5 mm polystyrene bead into the midpoint ($z \approx D/2$).
4. Press `+` or `-` to find peak resonance ($39.2–40.8\text{ kHz}$).
5. Use `u`/`d` to translate the particle vertically, `l`/`r` for horizontal steering.
