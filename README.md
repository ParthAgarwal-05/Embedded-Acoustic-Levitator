# 🔊 Acoustic Levitator Pro

**A 6-transducer ultrasonic acoustic levitator with Wi-Fi web dashboard and 2D particle manipulation.**

Built with an ESP32, 2× L293D H-bridge ICs, and 6× 40 kHz piezoelectric transducers arranged in a cross-pair wiring architecture.

---

## ✨ Features

- **2D Particle Control** — Move a levitated bead in Z (vertical) and X (horizontal) axes
- **Wi-Fi Dashboard** — Connect to the ESP32 access point and control everything from a browser at `192.168.4.1`
- **Serial Monitor Interface** — Full keyboard control over 115200 baud
- **Hardware PWM** — Zero-jitter 40 kHz drive via ESP32 LEDC peripheral (0% CPU overhead)
- **Resonance Sweep** — Automated 38.5–41.5 kHz sweep to find peak trapping frequency
- **Array Isolation** — Independently mute IC1 (Tx1/Tx2 pairs) or IC2 (Tx3 pair)

---

## 🔧 Hardware

| Component | Qty | Notes |
|-----------|-----|-------|
| ESP32 DevKit / NodeMCU-32S | 1 | Main MCU — GPIO 4, 5, 18, 19 |
| L293D H-Bridge IC | 2 | IC1: Tx1+Tx2 cross-pairs · IC2: Tx3 cross-pair |
| 40 kHz Ultrasonic Transducer | 6 | 3 top (facing down) + 3 bottom (facing up) |
| LM2596 Buck Converter | 1 | 12V → 5V for logic |
| 12V DC Power Supply | 1 | ≥ 1.5A recommended |

---

## ⚡ Wiring Architecture (Cross-Pair)

> **Rule:** A Top and Bottom transducer at the **same position** MAY share one L293D bridge.  
> Two transducers from the **same array** (both top OR both bottom) must **never** share a bridge.

| IC & Bridge | GPIO | Transducers |
|-------------|------|-------------|
| IC 1 — Bridge 1 | GPIO 4 / 5 | Top Tx1 + Bottom Tx1 |
| IC 1 — Bridge 2 | GPIO 4 / 5 | Top Tx2 + Bottom Tx2 |
| IC 2 — Bridge 1 | GPIO 18 / 19 | Top Tx3 + Bottom Tx3 |
| IC 2 — Bridge 2 | — | *Not used* |

See [`Acoustic_Levitator_6Tx_Wiring.xlsx`](Acoustic_Levitator_6Tx_Wiring.xlsx) for the full pinout table and [`WIRING_GUIDE.md`](WIRING_GUIDE.md) for the detailed guide.

---

## 📁 Repository Structure

```
📦 Embedded-Acoustic-Levitator
 ┣ 📄 project.ino                      ← ESP32 firmware (Arduino / IDF LEDC)
 ┣ 📄 Acoustic_Levitator_6Tx_Wiring.xlsx ← Complete wiring connection table
 ┣ 📄 WIRING_GUIDE.md                  ← Detailed wiring & calibration guide
 ┣ 📄 acoustic_levitator_schematic.pdf ← Circuit schematic
 ┗ 📂 web_dashboard/
    ┣ 📄 index.html                    ← Dashboard UI
    ┣ 📄 app.js                        ← Dashboard logic & API calls
    ┗ 📄 style.css                     ← Dashboard styles
```

---

## 🚀 Getting Started

### 1. Flash the Firmware
1. Open `project.ino` in Arduino IDE (or PlatformIO).
2. Install dependencies: `WiFi`, `WebServer`, `ESPmDNS` (bundled with ESP32 board package).
3. Select **ESP32 Dev Module** as the board.
4. Upload to your ESP32.

### 2. Connect to the Levitator
1. On your phone/laptop, connect to Wi-Fi: **`Acoustic-Levitator`** (password: `levitate123`).
2. Open a browser and go to **`http://192.168.4.1`**.
3. The web dashboard will load automatically.

### 3. Serial Monitor Controls (115200 baud)
| Key | Action |
|-----|--------|
| `w` / `s` | Move particle UP / DOWN |
| `a` / `d` | Steer particle LEFT / RIGHT |
| `c` | Reset to center trap node |
| `p` | Toggle phase (0° ↔ 180°) |
| `+` / `-` | Tune frequency ±100 Hz |
| `S` | Auto-sweep 38.5–41.5 kHz |
| `t` | Toggle IC1 (Tx1+Tx2 pairs) |
| `b` | Toggle IC2 (Tx3 pair) |
| `?` | Print live status |

---

## 🔬 Physics

The standing wave is created by the **phase difference between IC1 (0° reference) and IC2 (Z-phase shifted)**. The acoustic pressure nodes — points of minimum pressure — act as traps for small lightweight objects (~1–2 mm polystyrene beads).

- **Drive frequency:** 40,000 Hz (tunable 38–42 kHz)  
- **Wavelength:** λ = 343/40000 ≈ **8.58 mm**  
- **Node spacing:** λ/2 ≈ **4.29 mm**  
- **Recommended cavity gap:** ~25.7 mm (6× λ/2) in-phase mode

---

## 📝 License

MIT — free to use, modify and distribute with attribution.
