/*
 * =====================================================================================
 *  6-Transducer Ultrasonic Acoustic Levitator (3 Top + 3 Bottom)
 * =====================================================================================
 *  Microcontroller: ESP32 DevKit / NodeMCU-32S (GPIO 4, 5, 18, 19)
 *  Drivers:         2x L293D Dual H-Bridge ICs (Differential Push-Pull Drive, 24V p-p from 12V)
 *                   - IC 1: Top Array (3 Transducers: 2 on Bridge 1, 1 on Bridge 2)
 *                   - IC 2: Bottom Array (3 Transducers: 2 on Bridge 1, 1 on Bridge 2)
 *  Transducers:     6x 40 kHz Piezoelectric Transducers (3 Top facing DOWN, 3 Bottom facing UP)
 * 
 *  Physical Wiring Summary:
 *  -----------------------------------------------------------------------------------
 *  ESP32 Pin     Driver IC Pin                   Function
 *  -----------------------------------------------------------------------------------
 *  GPIO 4   ---> IC 1 Pin 2 (1A) & Pin 15 (4A)   Top Array Phase A (0 deg reference)
 *  GPIO 5   ---> IC 1 Pin 7 (2A) & Pin 10 (3A)   Top Array Phase B (180 deg push-pull)
 *  GPIO 18  ---> IC 2 Pin 2 (1A) & Pin 15 (4A)   Bottom Array Phase A (Z-phase shifted)
 *  GPIO 19  ---> IC 2 Pin 7 (2A) & Pin 10 (3A)   Bottom Array Phase B (Z-phase push-pull)
 * 
 *  Power Connections (Both IC 1 & IC 2):
 *  -----------------------------------------------------------------------------------
 *  12V (+) (from Power)  ---> Pin 8 (VCC2) on both ICs & LM2596 IN+
 *  Common GND            ---> Pins 4, 5, 12, 13, LM2596 IN-/OUT-, & ESP32 GND
 *  5V (from LM2596 OUT+) ---> Pin 1 (1,2EN), Pin 9 (3,4EN), Pin 16 (VCC1) on both ICs & ESP32 VIN
 * 
 *  Transducer Outputs:
 *  -----------------------------------------------------------------------------------
 *  IC 1 Bridge 1: Pin 3 (1Y) & Pin 6 (2Y)   ---> Top Transducers #1 & #2 (Parallel: (+) to 3, (-) to 6)
 *  IC 1 Bridge 2: Pin 14 (4Y) & Pin 11 (3Y) ---> Top Transducer #3 ((+) to 14, (-) to 11)
 *  IC 2 Bridge 1: Pin 3 (1Y) & Pin 6 (2Y)   ---> Bottom Transducers #1 & #2 (Parallel: (+) to 3, (-) to 6)
 *  IC 2 Bridge 2: Pin 14 (4Y) & Pin 11 (3Y) ---> Bottom Transducer #3 ((+) to 14, (-) to 11)
 *  -----------------------------------------------------------------------------------
 * 
 *  Dual Control:
 *    1. Web Dashboard (Connect to Wi-Fi hotspot or ESP32 AP "Acoustic-Levitator" / "12345678")
 *    2. Serial Monitor (115200 Baud):
 *       'p'       : Toggle Phase (0 deg In-Phase <-> 180 deg Anti-Phase)
 *       '+' / '-' : Tune frequency +/- 100 Hz
 *       'u' / 'd' : Translate particle UP / DOWN (+/- 4 ticks / ~5.6 deg)
 *       'w' / 's' : Move particle UP / DOWN
 *       'c'       : Center particle (Reset Z-phase to 0 deg)
 *       't' / 'b' : Toggle Top Array / Bottom Array ON / OFF
 *       'x'       : Auto-sweep frequency (38.5 kHz - 41.5 kHz)
 *       '?'       : Print live system status
 * =====================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "driver/ledc.h"

// ---------------------- Wi-Fi Configuration ------------------
// Set your phone hotspot credentials here:
const char* STA_SSID = "Parth's iPhone";
const char* STA_PASS = "Halomoto";

// Access Point fallback (used automatically if hotspot is not reachable)
const char* AP_SSID  = "Acoustic-Levitator";
const char* AP_PASS  = "12345678";

// ---------------------- Pin Definitions ----------------------
#define PIN_TOP_A   4   // Top Array Phase A (GPIO 4 -> IC 1 Pins 2 & 15)
#define PIN_TOP_B   5   // Top Array Phase B (GPIO 5 -> IC 1 Pins 7 & 10)
#define PIN_BOT_A  18   // Bottom Array Phase A (GPIO 18 -> IC 2 Pins 2 & 15)
#define PIN_BOT_B  19   // Bottom Array Phase B (GPIO 19 -> IC 2 Pins 7 & 10)

// ---------------------- Hardware LEDC Config -----------------
#if defined(CONFIG_IDF_TARGET_ESP32)
  #define LEV_LEDC_MODE    LEDC_HIGH_SPEED_MODE
#else
  #define LEV_LEDC_MODE    LEDC_LOW_SPEED_MODE
#endif

#define LEV_LEDC_TIMER   LEDC_TIMER_0
#define LEV_RESOLUTION   LEDC_TIMER_8_BIT   // 8-bit: 256 ticks per cycle (0..255)
#define DUTY_50_PERCENT  128                // 50% duty square wave

#define CH_TOP_A  LEDC_CHANNEL_0
#define CH_TOP_B  LEDC_CHANNEL_1
#define CH_BOT_A  LEDC_CHANNEL_2
#define CH_BOT_B  LEDC_CHANNEL_3

// ---------------------- System State -------------------------
uint32_t currentFreq   = 40000; // Nominal 40 kHz
uint8_t  botPhaseTick  = 0;     // 0 = 0 deg (In-phase), 128 = 180 deg (Anti-phase)
int8_t   xSteerTick    = 0;     // Virtual horizontal tilt (-64..+64)
bool     topEnabled    = true;
bool     botEnabled    = true;
String   wifiStatusMsg = "Starting...";

WebServer server(80);

// ---------------------- Function Prototypes ------------------
void configureTimer(uint32_t freq);
void configureChannels();
void updateBottomPhase(uint8_t tick);
void updateTopOutput();
void printStatus();
void setupWiFi();
void setupWebServer();
void sendCORSHeaders();
void sendJsonResponse();
void handleRoot();
void handleStatus();
void handleFreq();
void handlePhase();
void handleMove();
void handleToggle();
void handleSweep();
void handleOptions();

// ---------------------- HTML / Web Dashboard -----------------
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acoustic Levitator — 6-TX Mission Control</title>
  <style>
    :root {
      --bg: #070a12;
      --card-bg: rgba(16, 23, 38, 0.85);
      --border: rgba(0, 240, 255, 0.2);
      --cyan: #00f0ff;
      --violet: #a855f7;
      --green: #10b981;
      --red: #ef4444;
      --amber: #f59e0b;
      --text: #e2e8f0;
      --text-dim: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
    }
    header {
      width: 100%;
      max-width: 900px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 20px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 16px;
      backdrop-filter: blur(8px);
    }
    .brand h1 {
      font-size: 1.25rem;
      color: var(--cyan);
      letter-spacing: 1px;
    }
    .brand p {
      font-size: 0.8rem;
      color: var(--text-dim);
    }
    .status-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      background: rgba(16, 185, 129, 0.15);
      color: var(--green);
      padding: 6px 12px;
      border-radius: 20px;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      background: var(--green);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--green);
    }
    .main-grid {
      width: 100%;
      max-width: 900px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    @media (max-width: 768px) {
      .main-grid { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      backdrop-filter: blur(8px);
    }
    .card h2 {
      font-size: 1rem;
      color: var(--cyan);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .stat-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.9rem;
    }
    .stat-val {
      font-weight: bold;
      color: var(--cyan);
      font-family: monospace;
      font-size: 1rem;
    }
    .btn-group {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      margin-top: 14px;
    }
    button {
      background: rgba(0, 240, 255, 0.08);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 0.9rem;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s ease;
    }
    button:hover {
      background: rgba(0, 240, 255, 0.2);
      border-color: var(--cyan);
      transform: translateY(-1px);
    }
    button:active {
      transform: translateY(1px);
    }
    button.btn-violet {
      background: rgba(168, 85, 247, 0.12);
      border-color: rgba(168, 85, 247, 0.3);
      color: #d8b4fe;
    }
    button.btn-violet:hover {
      background: rgba(168, 85, 247, 0.25);
      border-color: var(--violet);
    }
    /* Visualizer box */
    .vis-box {
      width: 100%;
      height: 220px;
      background: rgba(5, 8, 16, 0.9);
      border: 1px solid rgba(0, 240, 255, 0.15);
      border-radius: 8px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
    }
    .tx-row {
      display: flex;
      gap: 32px;
      z-index: 2;
    }
    .tx-horn {
      width: 38px;
      height: 18px;
      background: #334155;
      border: 1px solid #64748b;
      border-radius: 3px;
      position: relative;
      display: flex;
      justify-content: center;
    }
    .tx-top { border-top: 3px solid var(--cyan); }
    .tx-bot { border-bottom: 3px solid var(--violet); }
    .tx-horn::after {
      content: "";
      position: absolute;
      width: 14px;
      height: 5px;
      background: #475569;
    }
    .tx-top::after { bottom: -5px; }
    .tx-bot::after { top: -5px; }
    .particle {
      width: 16px;
      height: 16px;
      background: radial-gradient(circle, #ffffff 30%, #38bdf8 100%);
      border-radius: 50%;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 18px rgba(56, 189, 248, 0.95);
      transition: top 0.2s ease-out;
      z-index: 3;
    }
    .wave-line {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      opacity: 0.35;
      pointer-events: none;
    }
    .log-box {
      width: 100%;
      max-width: 900px;
      margin-top: 16px;
      background: rgba(10, 15, 26, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 10px 14px;
      font-family: monospace;
      font-size: 0.8rem;
      color: #94a3b8;
      display: flex;
      justify-content: space-between;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>ACOUSTIC LEVITATOR <span>PRO 6-TX</span></h1>
      <p>3 Top Horns &middot; 3 Bottom Horns &middot; Hardware 40 kHz Push-Pull</p>
    </div>
    <div class="status-badge" id="wifi-badge">
      <span class="status-dot"></span>
      <span id="wifi-label">ONLINE</span>
    </div>
  </header>

  <div class="main-grid">
    <!-- Visualizer & Levitation State -->
    <div class="card">
      <h2>Acoustic Cavity & Particle (Standing Wave)</h2>
      <div class="vis-box">
        <div class="tx-row">
          <div class="tx-horn tx-top" title="Top Tx #1 (IC1 B1)"></div>
          <div class="tx-horn tx-top" title="Top Tx #2 (IC1 B1)"></div>
          <div class="tx-horn tx-top" title="Top Tx #3 (IC1 B2)"></div>
        </div>
        <div class="particle" id="lev-particle"></div>
        <canvas class="wave-line" id="wave-canvas"></canvas>
        <div class="tx-row">
          <div class="tx-horn tx-bot" title="Bottom Tx #1 (IC2 B1)"></div>
          <div class="tx-horn tx-bot" title="Bottom Tx #2 (IC2 B1)"></div>
          <div class="tx-horn tx-bot" title="Bottom Tx #3 (IC2 B2)"></div>
        </div>
      </div>

      <div style="margin-top: 16px;">
        <div class="stat-row">
          <span>Target Cavity Separation:</span>
          <span class="stat-val">34.3 mm (n=8) / 25.7 mm (n=6)</span>
        </div>
        <div class="stat-row">
          <span>Operating Mode:</span>
          <span class="stat-val" id="mode-text">ANTI-PHASE (180°)</span>
        </div>
        <div class="stat-row">
          <span>Effective Voltage Swing:</span>
          <span class="stat-val" style="color:var(--green);">24.0 V p-p</span>
        </div>
      </div>
    </div>

    <!-- Frequency & Phase Controls -->
    <div class="card">
      <h2>Transmitter Controls</h2>
      
      <div class="stat-row">
        <span>Resonance Frequency:</span>
        <span class="stat-val" id="freq-text">40,000 Hz</span>
      </div>
      <div class="btn-group">
        <button onclick="changeFreq(-100)">- 100 Hz</button>
        <button onclick="changeFreq(100)">+ 100 Hz</button>
        <button onclick="changeFreq(-1000)">- 1.0 kHz</button>
        <button onclick="changeFreq(1000)">+ 1.0 kHz</button>
      </div>

      <div class="stat-row" style="margin-top: 18px;">
        <span>Bottom Relative Phase:</span>
        <span class="stat-val" id="phase-text">0°</span>
      </div>
      <div class="btn-group">
        <button class="btn-violet" id="btn-phase" onclick="togglePhase()">Toggle 0° / 180°</button>
        <button class="btn-violet" onclick="moveZ('up')">Move UP (Z+)</button>
        <button class="btn-violet" onclick="moveZ('down')">Move DOWN (Z-)</button>
        <button class="btn-violet" onclick="centerTrap()">Reset Center</button>
      </div>

      <div class="stat-row" style="margin-top: 18px;">
        <span>Array Isolation Mute:</span>
      </div>
      <div class="btn-group">
        <button id="btn-top" onclick="toggleArray('top')">Top Array (3 Tx): ON</button>
        <button id="btn-bot" onclick="toggleArray('bot')">Bot Array (3 Tx): ON</button>
      </div>
      <div style="margin-top: 10px;">
        <button style="width: 100%;" class="btn-violet" onclick="triggerSweep()">Run Frequency Sweep (38.5 - 41.5 kHz)</button>
      </div>
    </div>
  </div>

  <div class="log-box">
    <span id="log-status">System Ready. Polling ESP32...</span>
    <span id="ip-status">IP: Connecting...</span>
  </div>

  <script>
    let currentFreq = 40000;
    let botPhase = 0;
    let topOn = true;
    let botOn = true;

    function updateUI(data) {
      currentFreq = data.freq;
      botPhase = data.phaseDeg;
      topOn = data.topOn;
      botOn = data.botOn;

      document.getElementById('freq-text').innerText = data.freq.toLocaleString() + ' Hz';
      document.getElementById('phase-text').innerText = data.phaseDeg + '° (' + data.phaseTick + '/256)';
      document.getElementById('mode-text').innerText = (data.phaseDeg === 0) ? 'IN-PHASE (0°)' : 'ANTI-PHASE (' + data.phaseDeg + '°)';
      document.getElementById('wifi-label').innerText = data.wifi;
      document.getElementById('ip-status').innerText = 'Net: ' + data.wifi;

      const particle = document.getElementById('lev-particle');
      const offsetPercent = ((data.phaseTick - 128) / 256) * 35;
      particle.style.top = (50 + offsetPercent) + '%';

      document.getElementById('btn-top').innerText = 'Top Array: ' + (topOn ? 'ON' : 'MUTED');
      document.getElementById('btn-bot').innerText = 'Bot Array: ' + (botOn ? 'ON' : 'MUTED');
      document.getElementById('btn-top').style.borderColor = topOn ? 'var(--cyan)' : 'var(--red)';
      document.getElementById('btn-bot').style.borderColor = botOn ? 'var(--violet)' : 'var(--red)';
    }

    async function pollStatus() {
      try {
        const res = await fetch('/api/status');
        if (res.ok) {
          const data = await res.json();
          updateUI(data);
          document.getElementById('log-status').innerText = 'Telemetry Synced';
        }
      } catch (e) {
        document.getElementById('log-status').innerText = 'Reconnecting to ESP32...';
      }
    }

    async function changeFreq(delta) {
      document.getElementById('log-status').innerText = 'Tuning frequency...';
      const res = await fetch('/api/freq?delta=' + delta);
      if (res.ok) updateUI(await res.json());
    }

    async function togglePhase() {
      document.getElementById('log-status').innerText = 'Toggling Phase...';
      const res = await fetch('/api/phase?toggle=1');
      if (res.ok) updateUI(await res.json());
    }

    async function moveZ(dir) {
      document.getElementById('log-status').innerText = 'Moving ' + dir + '...';
      const res = await fetch('/api/move?dir=' + dir);
      if (res.ok) updateUI(await res.json());
    }

    async function centerTrap() {
      document.getElementById('log-status').innerText = 'Centering trap...';
      const res = await fetch('/api/move?dir=center');
      if (res.ok) updateUI(await res.json());
    }

    async function toggleArray(which) {
      const res = await fetch('/api/toggle?target=' + which);
      if (res.ok) updateUI(await res.json());
    }

    async function triggerSweep() {
      document.getElementById('log-status').innerText = 'Running sweep (38.5 - 41.5 kHz)...';
      fetch('/api/sweep');
    }

    function drawWave() {
      const canvas = document.getElementById('wave-canvas');
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.beginPath();
      ctx.strokeStyle = '#00f0ff';
      ctx.lineWidth = 2;
      const midX = canvas.width / 2;
      const h = canvas.height;

      for (let y = 0; y <= h; y += 2) {
        const normY = (y / h) * Math.PI * 4;
        const wave = Math.sin(normY) * 45 * Math.sin(Date.now() / 200);
        const x = midX + wave;
        if (y === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      requestAnimationFrame(drawWave);
    }

    setInterval(pollStatus, 600);
    pollStatus();
    drawWave();
  </script>
</body>
</html>
)rawliteral";

// ---------------------- Setup --------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n========================================================");
  Serial.println("  6-TRANSDUCER ULTRASONIC ACOUSTIC LEVITATOR (3 TOP + 3 BOT)");
  Serial.println("========================================================");
  Serial.println("ESP32 Control Lines:");
  Serial.println("  GPIO 4  -> IC 1 Pins 2 & 15 (Top Array Phase A - 0 deg)");
  Serial.println("  GPIO 5  -> IC 1 Pins 7 & 10 (Top Array Phase B - 180 deg push-pull)");
  Serial.println("  GPIO 18 -> IC 2 Pins 2 & 15 (Bottom Array Phase A - Z phase)");
  Serial.println("  GPIO 19 -> IC 2 Pins 7 & 10 (Bottom Array Phase B - Z push-pull)");
  Serial.println("Driver Output Distribution:");
  Serial.println("  IC 1 Bridge 1 (Pins 3 & 6)   -> Top Transducers #1 & #2 (Parallel)");
  Serial.println("  IC 1 Bridge 2 (Pins 14 & 11) -> Top Transducer #3");
  Serial.println("  IC 2 Bridge 1 (Pins 3 & 6)   -> Bottom Transducers #1 & #2 (Parallel)");
  Serial.println("  IC 2 Bridge 2 (Pins 14 & 11) -> Bottom Transducer #3");
  Serial.println("--------------------------------------------------------");

  // 1. Initialize hardware PWM timers (Starts 40 kHz ultrasound immediately)
  configureTimer(currentFreq);
  configureChannels();
  updateBottomPhase(botPhaseTick);

  uint32_t actualFreq = ledc_get_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER);
  Serial.printf("[HARDWARE] APB Clock Active | Actual Frequency: %u Hz\n", actualFreq);
  Serial.println("[OK] Ultrasound Field Started Successfully.");

  // 2. Setup Wi-Fi and Web Dashboard (Station with AP fallback)
  setupWiFi();
  setupWebServer();

  printStatus();
}

// ---------------------- Main Loop ----------------------------
void loop() {
  server.handleClient();

  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '\r' || cmd == '\n') return;

    switch (cmd) {
      // Frequency Tuning
      case '+':
      case '=':
        currentFreq += 100;
        ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
        Serial.printf("[FREQ +] %u Hz\n", currentFreq);
        break;

      case '-':
      case '_':
        if (currentFreq > 1000) currentFreq -= 100;
        ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
        Serial.printf("[FREQ -] %u Hz\n", currentFreq);
        break;

      // Phase Flip (0 deg <-> 180 deg)
      case 'p':
      case 'P':
        botPhaseTick = (botPhaseTick == 0) ? 128 : 0;
        updateBottomPhase(botPhaseTick);
        Serial.printf("[PHASE FLIP] Bottom Phase: %u deg (%s)\n",
                      (botPhaseTick * 360) / 256,
                      (botPhaseTick == 0) ? "IN-PHASE (D=25.7mm or 34.3mm)" : "ANTI-PHASE (D=21.4mm or 30.0mm)");
        break;

      // Particle Translation UP / DOWN
      case 'u':
      case 'U':
      case 'w':
      case 'W':
        botPhaseTick = (botPhaseTick + 4) % 256;
        updateBottomPhase(botPhaseTick);
        Serial.printf("[MOVE UP] Phase: %u deg (%u/256)\n", (botPhaseTick * 360) / 256, botPhaseTick);
        break;

      case 'd':
      case 'D':
      case 's':
      case 'S':
        botPhaseTick = (botPhaseTick + 256 - 4) % 256;
        updateBottomPhase(botPhaseTick);
        Serial.printf("[MOVE DOWN] Phase: %u deg (%u/256)\n", (botPhaseTick * 360) / 256, botPhaseTick);
        break;

      // Reset to Center
      case 'c':
      case 'C':
        botPhaseTick = 0;
        updateBottomPhase(botPhaseTick);
        Serial.println("[CENTER] Particle reset to center (Phase: 0 deg).");
        break;

      // Array Muting / Isolation
      case 't':
      case 'T':
        topEnabled = !topEnabled;
        updateTopOutput();
        Serial.printf("[TOP ARRAY (3 Tx)] %s\n", topEnabled ? "ACTIVE" : "MUTED");
        break;

      case 'b':
      case 'B':
        botEnabled = !botEnabled;
        if (botEnabled) {
          updateBottomPhase(botPhaseTick);
        } else {
          ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_A, 0, 0);
          ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_B, 0, 0);
          ledc_update_duty(LEV_LEDC_MODE, CH_BOT_A);
          ledc_update_duty(LEV_LEDC_MODE, CH_BOT_B);
        }
        Serial.printf("[BOTTOM ARRAY (3 Tx)] %s\n", botEnabled ? "ACTIVE" : "MUTED");
        break;

      // Frequency Sweep
      case 'x':
      case 'X':
        Serial.println("\n[SWEEP START] Sweeping 38,500 Hz -> 41,500 Hz...");
        for (uint32_t f = 38500; f <= 41500; f += 200) {
          currentFreq = f;
          ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
          server.handleClient();
          delay(300);
        }
        Serial.println("[SWEEP FINISHED] Lock frequency with '+' or '-'.\n");
        break;

      case '?':
      case 'h':
      case 'H':
      default:
        printStatus();
        break;
    }
  }
}

// ---------------------- Hardware PWM Functions ---------------
void configureTimer(uint32_t freq) {
  ledc_timer_config_t timer_conf = {
    .speed_mode       = LEV_LEDC_MODE,
    .duty_resolution  = LEV_RESOLUTION,
    .timer_num        = LEV_LEDC_TIMER,
    .freq_hz          = freq,
    .clk_cfg          = LEDC_USE_APB_CLK   // Explicitly lock to APB 80 MHz clock
  };
  ledc_timer_config(&timer_conf);
}

void configureChannels() {
  // Top Phase A: GPIO 4 (0 deg, hpoint = 0)
  ledc_channel_config_t ch0 = {
    .gpio_num   = PIN_TOP_A,
    .speed_mode = LEV_LEDC_MODE,
    .channel    = CH_TOP_A,
    .intr_type  = LEDC_INTR_DISABLE,
    .timer_sel  = LEV_LEDC_TIMER,
    .duty       = DUTY_50_PERCENT,
    .hpoint     = 0
  };
  ledc_channel_config(&ch0);

  // Top Phase B: GPIO 5 (180 deg, hpoint = 128) -> Push-Pull
  ledc_channel_config_t ch1 = {
    .gpio_num   = PIN_TOP_B,
    .speed_mode = LEV_LEDC_MODE,
    .channel    = CH_TOP_B,
    .intr_type  = LEDC_INTR_DISABLE,
    .timer_sel  = LEV_LEDC_TIMER,
    .duty       = DUTY_50_PERCENT,
    .hpoint     = 128
  };
  ledc_channel_config(&ch1);

  // Bottom Phase A: GPIO 18 (hpoint = botPhaseTick)
  ledc_channel_config_t ch2 = {
    .gpio_num   = PIN_BOT_A,
    .speed_mode = LEV_LEDC_MODE,
    .channel    = CH_BOT_A,
    .intr_type  = LEDC_INTR_DISABLE,
    .timer_sel  = LEV_LEDC_TIMER,
    .duty       = DUTY_50_PERCENT,
    .hpoint     = botPhaseTick
  };
  ledc_channel_config(&ch2);

  // Bottom Phase B: GPIO 19 (Complementary push-pull)
  ledc_channel_config_t ch3 = {
    .gpio_num   = PIN_BOT_B,
    .speed_mode = LEV_LEDC_MODE,
    .channel    = CH_BOT_B,
    .intr_type  = LEDC_INTR_DISABLE,
    .timer_sel  = LEV_LEDC_TIMER,
    .duty       = DUTY_50_PERCENT,
    .hpoint     = (uint32_t)((botPhaseTick + 128) % 256)
  };
  ledc_channel_config(&ch3);
}

void updateBottomPhase(uint8_t tick) {
  botPhaseTick = tick;
  if (!botEnabled) return;

  uint32_t hpA = botPhaseTick;
  uint32_t hpB = (botPhaseTick + 128) % 256;

  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_A, DUTY_50_PERCENT, hpA);
  ledc_update_duty(LEV_LEDC_MODE, CH_BOT_A);

  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_B, DUTY_50_PERCENT, hpB);
  ledc_update_duty(LEV_LEDC_MODE, CH_BOT_B);
}

void updateTopOutput() {
  if (topEnabled) {
    ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_TOP_A, DUTY_50_PERCENT, 0);
    ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_TOP_B, DUTY_50_PERCENT, 128);
  } else {
    ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_TOP_A, 0, 0);
    ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_TOP_B, 0, 0);
  }
  ledc_update_duty(LEV_LEDC_MODE, CH_TOP_A);
  ledc_update_duty(LEV_LEDC_MODE, CH_TOP_B);
}

// ---------------------- Wi-Fi & WebServer Setup --------------
void setupWiFi() {
  Serial.println("\n[WIFI] Initializing Wi-Fi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(STA_SSID, STA_PASS);

  // Wait up to 6 seconds for hotspot connection
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 6000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    wifiStatusMsg = WiFi.localIP().toString();
    Serial.println("[WIFI SUCCESS] Connected to Hotspot: " + String(STA_SSID));
    Serial.println("  >>> Open Dashboard in Browser: http://" + wifiStatusMsg);
  } else {
    // Hotspot not available -> Fall back to AP mode
    WiFi.disconnect();
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    IPAddress apIP = WiFi.softAPIP();
    wifiStatusMsg = "AP: " + apIP.toString();
    Serial.println("[WIFI NOTICE] Hotspot unreachable -> Running in Access Point Mode!");
    Serial.println("  1. Connect your Phone/PC Wi-Fi to: '" + String(AP_SSID) + "' (Password: " + String(AP_PASS) + ")");
    Serial.println("  2. Open Dashboard in Browser at:  http://" + apIP.toString());
  }
}

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/freq", HTTP_GET, handleFreq);
  server.on("/api/phase", HTTP_GET, handlePhase);
  server.on("/api/move", HTTP_GET, handleMove);
  server.on("/api/toggle", HTTP_GET, handleToggle);
  server.on("/api/sweep", HTTP_GET, handleSweep);

  // CORS OPTIONS preflight handler
  server.on("/api/status", HTTP_OPTIONS, handleOptions);
  server.on("/api/freq", HTTP_OPTIONS, handleOptions);
  server.on("/api/phase", HTTP_OPTIONS, handleOptions);
  server.on("/api/move", HTTP_OPTIONS, handleOptions);
  server.on("/api/toggle", HTTP_OPTIONS, handleOptions);
  server.on("/api/sweep", HTTP_OPTIONS, handleOptions);

  server.begin();
  Serial.println("[HTTP SERVER] Web Dashboard Server Active on Port 80.");
}

void sendCORSHeaders() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "*");
}

void handleOptions() {
  sendCORSHeaders();
  server.send(204);
}

// ---------------------- HTTP Handlers ------------------------
void handleRoot() {
  server.send_P(200, "text/html", INDEX_HTML);
}

void sendJsonResponse() {
  uint32_t deg = (botPhaseTick * 360) / 256;
  sendCORSHeaders();

  String json = "{";
  json += "\"freq\":" + String(currentFreq) + ",";
  json += "\"phaseDeg\":" + String(deg) + ",";
  json += "\"phaseTick\":" + String(botPhaseTick) + ",";
  json += "\"zPhase\":" + String(botPhaseTick) + ",";
  json += "\"xSteer\":" + String(xSteerTick) + ",";
  json += "\"topOn\":" + String(topEnabled ? "true" : "false") + ",";
  json += "\"botOn\":" + String(botEnabled ? "true" : "false") + ",";
  json += "\"wifi\":\"" + wifiStatusMsg + "\"";
  json += "}";
  server.send(200, "application/json", json);
}

void handleStatus() {
  sendJsonResponse();
}

void handleFreq() {
  if (server.hasArg("val")) {
    currentFreq = server.arg("val").toInt();
  } else if (server.hasArg("delta")) {
    int32_t delta = server.arg("delta").toInt();
    if ((int32_t)currentFreq + delta >= 1000) {
      currentFreq += delta;
    }
  }
  ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
  sendJsonResponse();
}

void handlePhase() {
  if (server.hasArg("toggle")) {
    botPhaseTick = (botPhaseTick == 0) ? 128 : 0;
  } else if (server.hasArg("tick")) {
    botPhaseTick = server.arg("tick").toInt() % 256;
  } else if (server.hasArg("step")) {
    String step = server.arg("step");
    if (step == "up") {
      botPhaseTick = (botPhaseTick + 4) % 256;
    } else if (step == "down") {
      botPhaseTick = (botPhaseTick + 256 - 4) % 256;
    }
  } else if (server.hasArg("deg")) {
    uint32_t deg = server.arg("deg").toInt();
    botPhaseTick = (uint8_t)((deg * 256) / 360);
  }
  updateBottomPhase(botPhaseTick);
  sendJsonResponse();
}

void handleMove() {
  if (server.hasArg("zTick")) {
    botPhaseTick = server.arg("zTick").toInt() % 256;
    updateBottomPhase(botPhaseTick);
  }
  if (server.hasArg("xTick")) {
    xSteerTick = (int8_t)server.arg("xTick").toInt();
  }
  if (server.hasArg("dir")) {
    String dir = server.arg("dir");
    if (dir == "up") {
      botPhaseTick = (botPhaseTick + 4) % 256;
      updateBottomPhase(botPhaseTick);
    } else if (dir == "down") {
      botPhaseTick = (botPhaseTick + 256 - 4) % 256;
      updateBottomPhase(botPhaseTick);
    } else if (dir == "center") {
      botPhaseTick = 0;
      xSteerTick = 0;
      updateBottomPhase(botPhaseTick);
    } else if (dir == "left") {
      xSteerTick = max(-64, xSteerTick - 4);
    } else if (dir == "right") {
      xSteerTick = min(64, xSteerTick + 4);
    }
  }
  sendJsonResponse();
}

void handleToggle() {
  String target = "";
  if (server.hasArg("target")) target = server.arg("target");
  else if (server.hasArg("array")) target = server.arg("array");

  if (target == "top") {
    if (server.hasArg("state")) topEnabled = (server.arg("state").toInt() == 1);
    else topEnabled = !topEnabled;
    updateTopOutput();
  } else if (target == "bot") {
    if (server.hasArg("state")) botEnabled = (server.arg("state").toInt() == 1);
    else botEnabled = !botEnabled;
    if (botEnabled) {
      updateBottomPhase(botPhaseTick);
    } else {
      ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_A, 0, 0);
      ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_BOT_B, 0, 0);
      ledc_update_duty(LEV_LEDC_MODE, CH_BOT_A);
      ledc_update_duty(LEV_LEDC_MODE, CH_BOT_B);
    }
  }
  sendJsonResponse();
}

void handleSweep() {
  sendJsonResponse();
  // Perform smooth frequency sweep
  for (uint32_t f = 38500; f <= 41500; f += 200) {
    currentFreq = f;
    ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
    server.handleClient();
    delay(200);
  }
}

void printStatus() {
  uint32_t actualFreq = ledc_get_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER);
  Serial.println("\n---------------- SYSTEM STATUS ----------------");
  Serial.printf("  Carrier Freq:       %u Hz (Hardware Timer: %u Hz)\n", currentFreq, actualFreq);
  Serial.printf("  Top Array (3 Tx):   %s (GPIO 4: 0 deg | GPIO 5: 180 deg)\n", topEnabled ? "ACTIVE" : "MUTED");
  Serial.printf("  Bottom Array (3 Tx):%s (GPIO 18: %u deg | GPIO 19: %u deg)\n",
                botEnabled ? "ACTIVE" : "MUTED",
                (botPhaseTick * 360) / 256,
                (((botPhaseTick + 128) % 256) * 360) / 256);
  Serial.printf("  Current Mode:       %s\n",
                (botPhaseTick == 0) ? "0 deg IN-PHASE (D = 25.7mm or 34.3mm)" :
                                      "180 deg ANTI-PHASE (D = 21.4mm or 30.0mm)");
  Serial.printf("  Wi-Fi Status:       %s\n", wifiStatusMsg.c_str());
  Serial.println("---------------- CONTROLS ---------------------");
  Serial.println("  [p]       : Toggle Phase (0 deg <-> 180 deg)");
  Serial.println("  [+] / [-] : Tune Frequency (+/- 100 Hz)");
  Serial.println("  [u] / [d] : Translate Particle UP / DOWN (also [w] / [s])");
  Serial.println("  [c]       : Reset particle to center");
  Serial.println("  [t] / [b] : Toggle Top Array / Bottom Array ON/OFF");
  Serial.println("  [x]       : Auto-sweep frequency (38.5 kHz - 41.5 kHz)");
  Serial.println("  [?]       : Print status menu");
  Serial.println("-----------------------------------------------\n");
}
