# 6-Transducer Ultrasonic Acoustic Levitator — Complete Wiring Guide

This guide details the complete, proven wiring for the **6-Transducer Acoustic Levitator** (3 Top + 3 Bottom) using an **ESP32**, **LM2596 buck converter**, and **2x L293D dual H-bridge motor drivers**, adapted from the original proven reference architecture.

---

## 1. Power Distribution & Rail Architecture

### Primary Power Sources
* **12V DC Input (≥ 1.5A):**
  * Connect **12V (+)** to **LM2596 `IN+`** and **L293D Pin 8 (`VCC2`)** on both IC 1 and IC 2.
  * Connect **12V (−)** to **LM2596 `IN−`** (Common Ground).
* **LM2596 Buck Converter Setup:**
  * Adjust the brass potentiometer on the LM2596 until `OUT+` reads **precisely 5.0V DC** on a multimeter.
  * Connect `OUT+` (5.0V) to the **5V Logic Rail**.
  * Connect `OUT−` to the **Common Ground Rail**.

### Power Rail Bus Distribution
| Rail Name | Voltage | Destinations |
| :--- | :--- | :--- |
| **12V Motor Rail** | $+12\text{V}$ | L293D Pin 8 (`VCC2`) on **IC 1** and **IC 2** |
| **5V Logic Rail** | $+5.0\text{V}$ | ESP32 `VIN` / `5V` pin<br>L293D Pin 16 (`VCC1`) on **IC 1** and **IC 2**<br>L293D Pin 1 (`1,2EN`) and Pin 9 (`3,4EN`) on **IC 1** and **IC 2** |
| **Common GND** | $0\text{V}$ | LM2596 `IN−` and `OUT−`<br>ESP32 `GND` pins<br>L293D Pins 4, 5, 12, 13 (Center ground heat-sink pins) on **IC 1** and **IC 2** |

### Decoupling Capacitors (Essential for clean 40 kHz square waves)
* Place one **470 µF electrolytic capacitor** between $+12\text{V}$ and `GND` near the L293D power pins.
* Place one **0.1 µF (100nF) ceramic capacitor** directly across Pin 8 (`VCC2`) and Pin 4/5 (`GND`) of each L293D chip.

---

## 2. ESP32 Signal Lines

The ESP32 hardware LEDC PWM generates 4 synchronized, crystal-accurate 40 kHz signals:

| ESP32 Pin | Signal Label | Phase Relationship | Connected Driver |
| :--- | :--- | :--- | :--- |
| **GPIO 4** | `TOP_SIG_A` | $0^\circ$ (In-phase reference) | **IC 1** (Top Array): Pins 2 (`1A`) & 15 (`4A`) |
| **GPIO 5** | `TOP_SIG_B` | $180^\circ$ (Complementary push-pull) | **IC 1** (Top Array): Pins 7 (`2A`) & 10 (`3A`) |
| **GPIO 18** | `BOT_SIG_A` | Variable Phase ($180^\circ$ anti-phase default) | **IC 2** (Bottom Array): Pins 2 (`1A`) & 15 (`4A`) |
| **GPIO 19** | `BOT_SIG_B` | Complementary to `BOT_SIG_A` | **IC 2** (Bottom Array): Pins 7 (`2A`) & 10 (`3A`) |

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

## 4. Complete Driver-by-Driver Connection Matrix (6 Transducers)

### IC 1 — Top Array (3 Transducers, Facing DOWN)
* **Power & Enables:**
  * Pin 1 (`1,2EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 8 (`VCC2`) $\rightarrow$ $+12\text{V}$ Motor Supply
  * Pin 9 (`3,4EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 16 (`VCC1`) $\rightarrow$ $+5\text{V}$ Logic
  * Pins 4, 5, 12, 13 $\rightarrow$ Common `GND`
* **Signal Inputs (from ESP32):**
  * Pin 2 (`1A`) $\rightarrow$ ESP32 **GPIO 4** (`TOP_SIG_A`)
  * Pin 15 (`4A`) $\rightarrow$ ESP32 **GPIO 4** (`TOP_SIG_A`)
  * Pin 7 (`2A`) $\rightarrow$ ESP32 **GPIO 5** (`TOP_SIG_B`)
  * Pin 10 (`3A`) $\rightarrow$ ESP32 **GPIO 5** (`TOP_SIG_B`)
* **Outputs to Transducers (Top Array):**
  * **Bridge 1:**
    * Pin 3 (`1Y`) $\rightarrow$ **Top Tx #1 & Top Tx #2 Center Pins (+)** (wired in parallel)
    * Pin 6 (`2Y`) $\rightarrow$ **Top Tx #1 & Top Tx #2 Outer Casings (−)** (wired in parallel)
  * **Bridge 2:**
    * Pin 14 (`4Y`) $\rightarrow$ **Top Tx #3 Center Pin (+)**
    * Pin 11 (`3Y`) $\rightarrow$ **Top Tx #3 Outer Casing (−)**

---

### IC 2 — Bottom Array (3 Transducers, Facing UP)
* **Power & Enables:**
  * Pin 1 (`1,2EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 8 (`VCC2`) $\rightarrow$ $+12\text{V}$ Motor Supply
  * Pin 9 (`3,4EN`) $\rightarrow$ $+5\text{V}$ Logic
  * Pin 16 (`VCC1`) $\rightarrow$ $+5\text{V}$ Logic
  * Pins 4, 5, 12, 13 $\rightarrow$ Common `GND`
* **Signal Inputs (from ESP32):**
  * Pin 2 (`1A`) $\rightarrow$ ESP32 **GPIO 18** (`BOT_SIG_A`)
  * Pin 15 (`4A`) $\rightarrow$ ESP32 **GPIO 18** (`BOT_SIG_A`)
  * Pin 7 (`2A`) $\rightarrow$ ESP32 **GPIO 19** (`BOT_SIG_B`)
  * Pin 10 (`3A`) $\rightarrow$ ESP32 **GPIO 19** (`BOT_SIG_B`)
* **Outputs to Transducers (Bottom Array):**
  * **Bridge 1:**
    * Pin 3 (`1Y`) $\rightarrow$ **Bottom Tx #1 & Bottom Tx #2 Center Pins (+)** (wired in parallel)
    * Pin 6 (`2Y`) $\rightarrow$ **Bottom Tx #1 & Bottom Tx #2 Outer Casings (−)** (wired in parallel)
  * **Bridge 2:**
    * Pin 14 (`4Y`) $\rightarrow$ **Bottom Tx #3 Center Pin (+)**
    * Pin 11 (`3Y`) $\rightarrow$ **Bottom Tx #3 Outer Casing (−)**

---

## 5. Summary Quick Table

| Driver IC | Input Pins | ESP32 GPIO | Bridge Outputs | Transducers Connected |
| :--- | :--- | :--- | :--- | :--- |
| **IC 1 (Top Array)** | Pins 2 & 15<br>Pins 7 & 10 | **GPIO 4** (0°)<br>**GPIO 5** (180°) | Pins 3 & 6 (Bridge 1)<br>Pins 14 & 11 (Bridge 2) | **Top Tx #1 & #2** (parallel)<br>**Top Tx #3** |
| **IC 2 (Bottom Array)** | Pins 2 & 15<br>Pins 7 & 10 | **GPIO 18** (Z-phase)<br>**GPIO 19** (Z-phase push-pull) | Pins 3 & 6 (Bridge 1)<br>Pins 14 & 11 (Bridge 2) | **Bottom Tx #1 & #2** (parallel)<br>**Bottom Tx #3** |

---

## 6. Physical Setup & Calibration Rules

### Cavity Distance ($D$)
* Separation between the top transducer faces and bottom transducer faces must follow:
  $$D = n \times 4.29\text{ mm}$$
* Recommended test height: **$n = 8 \implies D \approx 34.3\text{ mm}$** (or $n = 6 \implies D \approx 25.7\text{ mm}$).
* Use M4 threaded rods with adjustment thumb nuts to calibrate the height.

### Levitation Procedure
1. Flash the ESP32 and open Serial Monitor at **115200 baud** (or open the Web Dashboard at `http://192.168.4.1`).
2. Make sure the Bottom Array phase is set to **180° (Anti-phase)** for $D = 34.3\text{ mm}$ (or press `p` to toggle if using $D = 25.7\text{ mm}$).
3. Place a lightweight EPS styrofoam bead (1.5–2.5 mm diameter) on a thin piece of paper or fine wire loop.
4. Slowly slide the bead into the midpoint between the top and bottom arrays.
5. Release the bead — it will snap into the acoustic pressure node and remain suspended in mid-air!
6. If the trapping force is weak, press `+` or `−` (or use the web dashboard buttons) to tune the frequency closer to the transducers' exact resonance (usually between $39.5\text{ kHz}$ and $40.5\text{ kHz}$).
