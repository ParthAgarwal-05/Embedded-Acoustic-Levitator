/*
 * =====================================================================================
 *  ACOUSTIC LEVITATOR PRO — MISSION CONTROL FIRMWARE
 *  6-Transducer Acoustic Array (3 Top Facing DOWN + 3 Bottom Facing UP)
 *
 *  WIRING ARCHITECTURE — CROSS-PAIR (CORRECTED):
 *   IC 1 (GPIO 4 / GPIO 5)  — Bridge 1: Top Tx1 + Bottom Tx1 (cross-pair)
 *                            — Bridge 2: Top Tx2 + Bottom Tx2 (cross-pair)
 *   IC 2 (GPIO 18 / GPIO 19)— Bridge 1: Top Tx3 + Bottom Tx3 (cross-pair)
 *                            — Bridge 2: NOT USED
 *
 *  RULE: A top transducer and the bottom transducer at the same position
 *        MAY share one IC bridge output (cross-pair is OK).
 *        Two transducers from the SAME array (both top OR both bottom)
 *        MUST NOT share a bridge output.
 *
 *  Standing wave is formed by the PHASE DIFFERENCE between IC1 (0° ref)
 *  and IC2 (Z-phase shifted via botPhaseTick) driving opposing transducers.
 * =====================================================================================
 *  Microcontroller: ESP32 DevKit / NodeMCU-32S (GPIO 4, 5, 18, 19)
 *  Dual Control:    1. Wi-Fi Web Dashboard (AP: "Acoustic-Levitator" -> 192.168.4.1)
 *                   2. Interactive Serial Monitor (115200 Baud)
 *
 *  2D Particle Manipulation:
 *   - Z-Axis (UP / DOWN)   : Phase delay between IC1 (Tx1/Tx2 pairs) and IC2 (Tx3 pair)
 *   - X-Axis (LEFT / RIGHT): Horizontal acoustic positioning & UI visualizer
 *   - Carrier Tuning       : 38,000 Hz to 42,000 Hz in +/- 100 Hz steps
 *   - Resonance Sweep      : Automated frequency sweep 38.5 kHz -> 41.5 kHz
 *   - Array Isolation      : Mute Tx1/Tx2 pairs (IC1) or Tx3 pair (IC2)
 * =====================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include "driver/ledc.h"

// ---------------------- Pin Definitions ----------------------
// Hardware PWM Channels (Strictly 4 Pins: GPIO 4, 5, 18, 19)
//
// IC 1 signals (drives Tx1 cross-pair on Bridge 1 & Tx2 cross-pair on Bridge 2):
#define PIN_IC1_A        4   // IC1 Phase A (GPIO 4: 0° reference)  → IC1 Pins 2 & 15
#define PIN_IC1_B        5   // IC1 Phase B (GPIO 5: 180° push-pull) → IC1 Pins 7 & 10
//
// IC 2 signals (drives Tx3 cross-pair on Bridge 1; Bridge 2 unused):
#define PIN_IC2_A       18   // IC2 Phase A (GPIO 18: 0°+Z shifted)  → IC2 Pins 2 & 15
#define PIN_IC2_B       19   // IC2 Phase B (GPIO 19: 180°+Z shifted)→ IC2 Pins 7 & 10

// ---------------------- Hardware LEDC Config -----------------
#if defined(CONFIG_IDF_TARGET_ESP32)
  #define LEV_LEDC_MODE    LEDC_HIGH_SPEED_MODE
#else
  #define LEV_LEDC_MODE    LEDC_LOW_SPEED_MODE
#endif

#define LEV_LEDC_TIMER   LEDC_TIMER_0
#define LEV_RESOLUTION   LEDC_TIMER_8_BIT   // 8-bit: 256 ticks per cycle (0..255)
#define DUTY_50_PERCENT  128                // 50% duty square wave

// 4 Hardware LEDC Channels
// CH_IC1_A / CH_IC1_B → IC1 (Top Tx1+Bot Tx1 cross-pair & Top Tx2+Bot Tx2 cross-pair)
// CH_IC2_A / CH_IC2_B → IC2 (Top Tx3+Bot Tx3 cross-pair)
#define CH_IC1_A         LEDC_CHANNEL_0
#define CH_IC1_B         LEDC_CHANNEL_1
#define CH_IC2_A         LEDC_CHANNEL_2
#define CH_IC2_B         LEDC_CHANNEL_3

// ---------------------- Wi-Fi Access Point Config ------------
const char* AP_SSID = "Acoustic-Levitator";
const char* AP_PASS = "levitate123"; // Or set to "" for open network

WebServer server(80);

// ---------------------- System State -------------------------
uint32_t currentFreq  = 40000;  // Nominal 40 kHz
uint8_t  botPhaseTick = 0;      // 0..255 (0 = In-phase 0 deg, 128 = Anti-phase 180 deg)
                                 // Controls phase difference between IC1 (ref) and IC2 (shifted)
int8_t   xSteerTick   = 0;      // -64..+64 (horizontal phase tilt)
bool     ic1Enabled   = true;   // IC1 = Tx1 cross-pair (Bridge 1) + Tx2 cross-pair (Bridge 2)
bool     ic2Enabled   = true;   // IC2 = Tx3 cross-pair (Bridge 1)
// NOTE: Kept as topEnabled/botEnabled aliases for web API backward compatibility
bool&    topEnabled   = ic1Enabled;  // 'top' button controls IC1 (Tx1+Tx2 pairs)
bool&    botEnabled   = ic2Enabled;  // 'bot' button controls IC2 (Tx3 pair)
bool     isSweeping   = false;

// ---------------------- Function Prototypes ------------------
void configureTimer(uint32_t freq);
void configureChannels();
void updatePhases();
void printStatus();
void setupWebServer();

// ---------------------- Embedded Web Dashboard HTML ----------
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Acoustic Levitator Pro — Mission Control</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Orbitron:wght@600;900&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #060911; --card: rgba(13,20,36,0.85); --border: rgba(56,189,248,0.2);
      --cyan: #00f0ff; --purple: #a855f7; --amber: #f59e0b; --emerald: #10b981; --coral: #ef4444;
      --text: #f1f5f9; --muted: #94a3b8; --dim: #64748b;
    }
    * { margin:0; padding:0; box-sizing:border-box; font-family:'Plus Jakarta Sans',sans-serif; }
    body { background:var(--bg); color:var(--text); min-height:100vh; display:flex; flex-direction:column; overflow-x:hidden; }
    .top-bar { display:flex; align-items:center; justify-content:space-between; padding:0.9rem 1.5rem; background:rgba(10,16,28,0.9); border-bottom:1px solid rgba(255,255,255,0.08); flex-wrap:wrap; gap:0.5rem; }
    .brand h1 { font-family:'Orbitron',sans-serif; font-size:1.1rem; letter-spacing:0.08em; color:#fff; display:flex; align-items:center; gap:0.5rem; }
    .badge-pro { font-size:0.65rem; font-family:'JetBrains Mono',monospace; background:linear-gradient(90deg,var(--cyan),var(--purple)); color:#000; padding:0.15rem 0.4rem; border-radius:4px; font-weight:800; }
    .subtitle { font-size:0.75rem; color:var(--muted); }
    .telemetry-group { display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap; }
    .pill { background:rgba(17,24,39,0.8); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:0.3rem 0.65rem; display:flex; flex-direction:column; min-width:85px; }
    .pill-lbl { font-size:0.6rem; font-family:'JetBrains Mono',monospace; color:var(--dim); font-weight:700; }
    .pill-val { font-size:0.85rem; font-family:'JetBrains Mono',monospace; font-weight:700; }
    .text-cyan { color:var(--cyan); text-shadow:0 0 8px rgba(0,240,255,0.4); }
    .text-purple { color:var(--purple); text-shadow:0 0 8px rgba(168,85,247,0.4); }
    .text-amber { color:var(--amber); text-shadow:0 0 8px rgba(245,158,11,0.4); }
    .grid { flex:1; padding:1.2rem; display:grid; grid-template-columns:320px 1fr 340px; gap:1.2rem; }
    @media(max-width:1100px){ .grid { grid-template-columns:1fr 1fr; } .col-ctrl { grid-column:span 2; } }
    @media(max-width:768px){ .grid { grid-template-columns:1fr; } .col-ctrl { grid-column:span 1; } }
    .card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:1.2rem; backdrop-filter:blur(16px); box-shadow:0 10px 25px -10px rgba(0,0,0,0.6); display:flex; flex-direction:column; gap:1rem; }
    .card-header { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:0.6rem; }
    .card-header h3 { font-family:'Orbitron',sans-serif; font-size:0.88rem; font-weight:700; letter-spacing:0.04em; }
    .dpad-container { position:relative; width:220px; height:220px; margin:0.5rem auto; }
    .dpad-btn { position:absolute; background:linear-gradient(135deg,#15223c,#0d1526); border:1px solid rgba(0,240,255,0.3); border-radius:12px; color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; cursor:pointer; transition:all 0.15s; width:68px; height:68px; user-select:none; }
    .dpad-btn:hover { border-color:var(--cyan); box-shadow:0 0 15px rgba(0,240,255,0.35); transform:scale(1.04); }
    .dpad-btn:active, .dpad-btn.pressed { background:var(--cyan); color:#000; box-shadow:0 0 20px var(--cyan); transform:scale(0.95); }
    .btn-up { top:0; left:50%; transform:translateX(-50%); }
    .btn-down { bottom:0; left:50%; transform:translateX(-50%); }
    .btn-left { top:50%; left:0; transform:translateY(-50%); }
    .btn-right { top:50%; right:0; transform:translateY(-50%); }
    .btn-center { top:50%; left:50%; transform:translate(-50%,-50%); border-radius:50%; border-color:rgba(168,85,247,0.4); width:64px; height:64px; }
    .btn-center:hover { border-color:var(--purple); box-shadow:0 0 15px rgba(168,85,247,0.4); }
    .btn-lbl { font-size:0.62rem; font-family:'JetBrains Mono',monospace; font-weight:700; margin-top:2px; }
    .coord-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; width:100%; }
    .coord-box { background:rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:0.6rem; display:flex; flex-direction:column; }
    .coord-title { font-size:0.6rem; font-family:'JetBrains Mono',monospace; color:var(--dim); font-weight:700; }
    .coord-val { font-family:'Orbitron',sans-serif; font-size:1.1rem; font-weight:700; color:#fff; margin:0.15rem 0; }
    .coord-sub { font-size:0.65rem; font-family:'JetBrains Mono',monospace; color:var(--cyan); }
    .seg-group { display:flex; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:3px; gap:3px; }
    .seg-btn { flex:1; background:transparent; border:none; color:var(--dim); padding:0.4rem; border-radius:6px; font-size:0.7rem; font-family:'JetBrains Mono',monospace; font-weight:700; cursor:pointer; }
    .seg-btn.active { background:rgba(0,240,255,0.2); color:var(--cyan); border:1px solid rgba(0,240,255,0.4); }
    .canvas-wrap { position:relative; width:100%; height:340px; border-radius:12px; background:radial-gradient(circle at center,#0d1a33 0%,#050914 100%); border:1px solid rgba(0,240,255,0.2); overflow:hidden; }
    canvas { width:100%; height:100%; display:block; }
    .quick-bar { display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; }
    .glow-btn { padding:0.75rem 0.5rem; border-radius:10px; font-family:'Orbitron',sans-serif; font-size:0.78rem; font-weight:700; cursor:pointer; border:1px solid; display:flex; align-items:center; justify-content:center; gap:0.4rem; transition:all 0.2s; user-select:none; }
    .btn-phase { background:rgba(168,85,247,0.15); border-color:rgba(168,85,247,0.4); color:#fff; }
    .btn-phase:hover { background:rgba(168,85,247,0.3); border-color:var(--purple); box-shadow:0 0 15px rgba(168,85,247,0.4); }
    .btn-sweep { background:rgba(0,240,255,0.15); border-color:rgba(0,240,255,0.4); color:#fff; }
    .btn-sweep:hover { background:rgba(0,240,255,0.3); border-color:var(--cyan); box-shadow:0 0 15px rgba(0,240,255,0.4); }
    .freq-box { background:rgba(0,0,0,0.4); border:1px solid rgba(0,240,255,0.3); border-radius:12px; padding:0.6rem; text-align:center; }
    .freq-num { font-family:'Orbitron',sans-serif; font-size:1.8rem; font-weight:900; color:#fff; text-shadow:0 0 15px rgba(0,240,255,0.4); }
    .freq-btns { display:grid; grid-template-columns:repeat(5,1fr); gap:0.35rem; }
    .f-btn { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:0.4rem 0.1rem; border-radius:6px; font-family:'JetBrains Mono',monospace; font-size:0.68rem; font-weight:600; cursor:pointer; }
    .f-btn:hover { background:rgba(0,240,255,0.2); border-color:var(--cyan); }
    input[type=range] { width:100%; height:6px; border-radius:4px; outline:none; -webkit-appearance:none; background:rgba(255,255,255,0.15); }
    input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; border-radius:50%; background:var(--cyan); cursor:pointer; box-shadow:0 0 10px var(--cyan); }
    .array-card { display:flex; align-items:center; justify-content:space-between; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:0.65rem 0.8rem; }
    .array-card.active { border-color:rgba(16,185,129,0.4); background:rgba(16,185,129,0.08); }
    .array-card.muted { border-color:rgba(239,68,68,0.4); background:rgba(239,68,68,0.08); }
    .arr-btn { background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color:#fff; padding:0.35rem 0.6rem; border-radius:6px; font-family:'JetBrains Mono',monospace; font-size:0.68rem; font-weight:700; cursor:pointer; }
    .console-footer { background:rgba(6,9,17,0.95); border-top:1px solid rgba(255,255,255,0.08); padding:0.5rem 1.5rem; font-family:'JetBrains Mono',monospace; font-size:0.75rem; }
    .log-stream { height:65px; overflow-y:auto; color:var(--muted); display:flex; flex-direction:column; gap:0.25rem; }
  </style>
</head>
<body>
  <div class="top-bar">
    <div class="brand">
      <h1>ACOUSTIC LEVITATOR <span class="badge-pro">PRO 6-TX</span></h1>
      <p class="subtitle">2D Acoustic Trapping & Positioning (3 Top + 3 Bottom)</p>
    </div>
    <div class="telemetry-group">
      <div class="pill"><span class="pill-lbl">CARRIER</span><span class="pill-val text-cyan" id="disp-freq">40,000 Hz</span></div>
      <div class="pill"><span class="pill-lbl">Z-PHASE</span><span class="pill-val text-purple" id="disp-z">0°</span></div>
      <div class="pill"><span class="pill-lbl">X-STEER</span><span class="pill-val text-amber" id="disp-x">0°</span></div>
    </div>
  </div>

  <div class="grid">
    <!-- Col 1: 2D Motion -->
    <div class="card">
      <div class="card-header">
        <h3>2D Particle Motion</h3>
        <span style="font-size:0.6rem;color:var(--dim);font-family:'JetBrains Mono';">ACOUSTIC STEERING</span>
      </div>
      <div class="dpad-container">
        <button class="dpad-btn btn-up" id="btn-up"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4l-8 8h6v8h4v-8h6z"/></svg><span class="btn-lbl">UP (Z+)</span></button>
        <button class="dpad-btn btn-left" id="btn-left"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M4 12l8-8v6h8v4h-8v6z"/></svg><span class="btn-lbl">LEFT (X-)</span></button>
        <button class="dpad-btn btn-center" id="btn-center"><div style="width:12px;height:12px;border:2px solid var(--purple);border-radius:50%;"></div><span class="btn-lbl">CENTER</span></button>
        <button class="dpad-btn btn-right" id="btn-right"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M20 12l-8 8v-6H4v-4h8V4z"/></svg><span class="btn-lbl">RIGHT (X+)</span></button>
        <button class="dpad-btn btn-down" id="btn-down"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 20l8-8h-6V4h-4v8H4z"/></svg><span class="btn-lbl">DOWN (Z-)</span></button>
      </div>
      <div class="coord-grid">
        <div class="coord-box"><span class="coord-title">X-STEER (LATERAL)</span><span class="coord-val" id="val-x">0.0 mm</span><span class="coord-sub" id="sub-x">Phase: 0°</span></div>
        <div class="coord-box"><span class="coord-title">Z-HEIGHT (VERTICAL)</span><span class="coord-val" id="val-z">0.0 mm</span><span class="coord-sub" id="sub-z">Phase: 0°</span></div>
      </div>
      <div class="seg-group">
        <button class="seg-btn" data-step="1">Fine (0.2mm)</button>
        <button class="seg-btn active" data-step="4">Normal (0.8mm)</button>
        <button class="seg-btn" data-step="8">Coarse (1.6mm)</button>
      </div>
    </div>

    <!-- Col 2: Hologram Canvas -->
    <div class="card">
      <div class="card-header">
        <h3>Cavity Standing Wave Hologram</h3>
        <span id="mode-badge" style="font-family:'JetBrains Mono';font-size:0.68rem;color:var(--cyan);background:rgba(0,240,255,0.12);padding:0.2rem 0.5rem;border-radius:4px;">0° IN-PHASE (D ≈ 25.7mm)</span>
      </div>
      <div class="canvas-wrap">
        <canvas id="cavity-canvas"></canvas>
      </div>
      <div class="quick-bar">
        <button class="glow-btn btn-phase" id="btn-phase">FLIP PHASE (0° &harr; 180°) [P]</button>
        <button class="glow-btn btn-sweep" id="btn-sweep">AUTO-SWEEP [S]</button>
      </div>
    </div>

    <!-- Col 3: Controls -->
    <div class="card col-ctrl">
      <div class="card-header">
        <h3>Carrier Frequency & Arrays</h3>
        <span style="font-size:0.6rem;color:var(--dim);font-family:'JetBrains Mono';">PWM ENGINE</span>
      </div>
      <div class="freq-box">
        <span class="freq-num" id="big-freq">40,000</span> <span style="color:var(--cyan);font-family:'JetBrains Mono';font-size:0.9rem;">Hz</span>
      </div>
      <div class="freq-btns">
        <button class="f-btn" id="f-m500">-500</button>
        <button class="f-btn" id="f-m100">-100 [-]</button>
        <button class="f-btn" id="f-reset">40k</button>
        <button class="f-btn" id="f-p100">+100 [+]</button>
        <button class="f-btn" id="f-p500">+500</button>
      </div>
      <input type="range" id="freq-slider" min="38000" max="42000" step="50" value="40000">
      
      <div style="display:flex;flex-direction:column;gap:0.5rem;margin-top:0.4rem;">
        <div class="array-card active" id="card-top">
          <div><h4 style="font-size:0.8rem;">Top Array (3x Tx)</h4><p style="font-size:0.65rem;color:var(--dim);font-family:'JetBrains Mono';">GPIO 4, 5 &bull; IC 1 &bull; DOWN</p></div>
          <button class="arr-btn" id="btn-top">ACTIVE [T]</button>
        </div>
        <div class="array-card active" id="card-bot">
          <div><h4 style="font-size:0.8rem;">Bottom Array (3x Tx)</h4><p style="font-size:0.65rem;color:var(--dim);font-family:'JetBrains Mono';">GPIO 18, 19 &bull; IC 2 &bull; UP</p></div>
          <button class="arr-btn" id="btn-bot">ACTIVE [B]</button>
        </div>
      </div>
    </div>
  </div>

  <div class="console-footer">
    <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
      <span style="color:var(--dim);font-weight:700;">LIVE SYSTEM TELEMETRY</span>
      <span style="color:var(--emerald);">ESP32 ONLINE (192.168.4.1)</span>
    </div>
    <div class="log-stream" id="logs">
      <div>[SYSTEM] Mission Control loaded. APB 80 MHz hardware PWM active.</div>
    </div>
  </div>

  <script>
    const S = { freq:40000, zPhase:0, xSteer:0, top:true, bot:true, step:4 };
    const cvs = document.getElementById('cavity-canvas');
    const ctx = cvs.getContext('2d');
    let W, H, pX=150, pY=170, vX=0, vY=0, wavePh=0;

    function resize() {
      const r = cvs.getBoundingClientRect();
      cvs.width = r.width * window.devicePixelRatio;
      cvs.height = r.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      W = r.width; H = r.height;
    }
    window.addEventListener('resize', resize);
    resize();

    function log(msg) {
      const el = document.getElementById('logs');
      const d = document.createElement('div');
      d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
      el.appendChild(d);
      el.scrollTop = el.scrollHeight;
    }

    async function api(path, q={}) {
      const s = new URLSearchParams(q).toString();
      try {
        const res = await fetch('/api/' + path + (s ? '?' + s : ''));
        return await res.json();
      } catch(e) {
        return null;
      }
    }

    function syncUI() {
      document.getElementById('disp-freq').textContent = S.freq.toLocaleString() + ' Hz';
      document.getElementById('big-freq').textContent = S.freq.toLocaleString();
      document.getElementById('freq-slider').value = S.freq;
      const zD = Math.round((S.zPhase * 360)/256);
      const xD = Math.round((S.xSteer * 180)/64);
      document.getElementById('disp-z').textContent = zD + '°';
      document.getElementById('sub-z').textContent = 'Phase: ' + zD + '°';
      document.getElementById('val-z').textContent = (((S.zPhase-64)/128)*4.3).toFixed(2) + ' mm';
      document.getElementById('disp-x').textContent = xD + '°';
      document.getElementById('sub-x').textContent = 'Phase: ' + xD + '°';
      document.getElementById('val-x').textContent = ((S.xSteer/64)*5.0).toFixed(2) + ' mm';

      const mb = document.getElementById('mode-badge');
      if (S.zPhase === 0) mb.textContent = '0° IN-PHASE (D ≈ 25.7mm)';
      else if (S.zPhase === 128) mb.textContent = '180° ANTI-PHASE (D ≈ 21.4mm)';
      else mb.textContent = 'PHASE: ' + zD + '° (Z-SHIFT ACTIVE)';

      document.getElementById('card-top').className = S.top ? 'array-card active' : 'array-card muted';
      document.getElementById('btn-top').textContent = S.top ? 'ACTIVE [T]' : 'MUTED';
      document.getElementById('card-bot').className = S.bot ? 'array-card active' : 'array-card muted';
      document.getElementById('btn-bot').textContent = S.bot ? 'ACTIVE [B]' : 'MUTED';
    }

    async function move(dir) {
      if (dir === 'up') S.zPhase = (S.zPhase + S.step) % 256;
      else if (dir === 'down') S.zPhase = (S.zPhase + 256 - S.step) % 256;
      else if (dir === 'left') S.xSteer = Math.max(-64, S.xSteer - S.step);
      else if (dir === 'right') S.xSteer = Math.min(64, S.xSteer + S.step);
      else if (dir === 'center') { S.zPhase = 0; S.xSteer = 0; }
      syncUI();
      log(`Moved ${dir.toUpperCase()} (Z: ${S.zPhase}, X: ${S.xSteer})`);
      await api('move', { dir, zTick: S.zPhase, xTick: S.xSteer });
    }

    async function setFreq(f) {
      S.freq = Math.max(37000, Math.min(43000, f));
      syncUI();
      log(`Frequency set to ${S.freq} Hz`);
      await api('freq', { val: S.freq });
    }

    async function flipPhase() {
      S.zPhase = (S.zPhase === 0) ? 128 : 0;
      syncUI();
      log(`Phase flipped to ${S.zPhase === 0 ? '0° IN-PHASE' : '180° ANTI-PHASE'}`);
      await api('phase', { tick: S.zPhase });
    }

    async function sweep() {
      log('Starting resonance sweep 38.5 kHz -> 41.5 kHz...');
      for (let f = 38500; f <= 41500; f += 200) {
        S.freq = f;
        syncUI();
        await new Promise(r => setTimeout(r, 100));
      }
      S.freq = 40000;
      syncUI();
      log('Resonance sweep finished. Locked to 40,000 Hz.');
      await api('freq', { val: 40000 });
    }

    async function toggleArray(target) {
      if (target === 'top') S.top = !S.top;
      else S.bot = !S.bot;
      syncUI();
      log(`Array ${target.toUpperCase()} toggled: ${target === 'top' ? S.top : S.bot}`);
      await api('toggle', { target, state: (target === 'top' ? S.top : S.bot) ? 1 : 0 });
    }

    document.getElementById('btn-up').onclick = () => move('up');
    document.getElementById('btn-down').onclick = () => move('down');
    document.getElementById('btn-left').onclick = () => move('left');
    document.getElementById('btn-right').onclick = () => move('right');
    document.getElementById('btn-center').onclick = () => move('center');
    document.getElementById('btn-phase').onclick = flipPhase;
    document.getElementById('btn-sweep').onclick = sweep;
    document.getElementById('btn-top').onclick = () => toggleArray('top');
    document.getElementById('btn-bot').onclick = () => toggleArray('bot');

    document.querySelectorAll('.seg-btn').forEach(b => {
      b.onclick = () => {
        document.querySelectorAll('.seg-btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        S.step = parseInt(b.dataset.step, 10);
      };
    });

    document.getElementById('f-m500').onclick = () => setFreq(S.freq - 500);
    document.getElementById('f-m100').onclick = () => setFreq(S.freq - 100);
    document.getElementById('f-reset').onclick = () => setFreq(40000);
    document.getElementById('f-p100').onclick = () => setFreq(S.freq + 100);
    document.getElementById('f-p500').onclick = () => setFreq(S.freq + 500);
    document.getElementById('freq-slider').oninput = e => { S.freq = parseInt(e.target.value, 10); syncUI(); };
    document.getElementById('freq-slider').onchange = e => setFreq(parseInt(e.target.value, 10));

    window.onkeydown = e => {
      if (e.target.tagName === 'INPUT') return;
      const k = e.key.toLowerCase();
      if (k==='w'||k==='arrowup') move('up');
      else if (k==='s'||k==='arrowdown') move('down');
      else if (k==='a'||k==='arrowleft') move('left');
      else if (k==='d'||k==='arrowright') move('right');
      else if (k===' ') move('center');
      else if (k==='p') flipPhase();
      else if (k==='+'||k==='=') setFreq(S.freq+100);
      else if (k==='-'||k==='_') setFreq(S.freq-100);
      else if (k==='t') toggleArray('top');
      else if (k==='b') toggleArray('bot');
    };

    function render() {
      ctx.clearRect(0,0,W,H);
      const cX = W/2, topY = 40, botY = H - 40, midY = (topY+botY)/2;
      const sp = 70;

      // Draw 3 top horns
      [-80, 0, 80].forEach((ox, i) => {
        ctx.fillStyle = S.top ? '#1e293b' : '#0f172a';
        ctx.strokeStyle = S.top ? '#00f0ff' : '#475569';
        ctx.lineWidth = 1.5;
        ctx.fillRect(cX + ox - 20, topY - 14, 40, 14);
        ctx.strokeRect(cX + ox - 20, topY - 14, 40, 14);
      });

      // Draw 3 bot horns
      [-80, 0, 80].forEach((ox, i) => {
        ctx.fillStyle = S.bot ? '#1e293b' : '#0f172a';
        ctx.strokeStyle = S.bot ? '#a855f7' : '#475569';
        ctx.lineWidth = 1.5;
        ctx.fillRect(cX + ox - 20, botY, 40, 14);
        ctx.strokeRect(cX + ox - 20, botY, 40, 14);
      });

      // Wavefield
      wavePh += 0.08;
      if (S.top || S.bot) {
        ctx.strokeStyle = 'rgba(0,240,255,0.12)';
        [-80, 0, 80].forEach((ox, i) => {
          const tilt = (i - 1) * (S.xSteer * 0.04);
          for (let r=20; r<120; r+=24) {
            ctx.beginPath();
            ctx.arc(cX+ox, topY, r+((wavePh+tilt)%24), 0.2*Math.PI, 0.8*Math.PI);
            ctx.stroke();
          }
        });
      }

      // Particle physics
      const tX = cX + (S.xSteer/64)*75;
      const tY = midY - ((S.zPhase-64)/128)*35;
      vX = (vX + (tX - pX)*0.08)*0.82;
      vY = (vY + (tY - pY)*0.08)*0.82;
      pX += vX; pY += vY;

      if (S.top && S.bot) {
        ctx.fillStyle = 'rgba(255,255,255,0.95)';
        ctx.beginPath();
        ctx.arc(pX, pY, 5, 0, Math.PI*2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(0,240,255,0.6)';
        ctx.stroke();
      }

      requestAnimationFrame(render);
    }
    render();
    syncUI();
  </script>
</body>
</html>
)rawliteral";

// ---------------------- Setup & Hardware Init ----------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n========================================================");
  Serial.println("  ACOUSTIC LEVITATOR PRO (6-TRANSDUCER SYSTEM)");
  Serial.println("  3 Top Transducers (DOWN) + 3 Bottom Transducers (UP)");
  Serial.println("  Driver: 2x L293D (IC 1 = Top 3, IC 2 = Bottom 3)");
  Serial.println("========================================================");

  // 1. Initialize hardware PWM timers (80 MHz APB Clock)
  configureTimer(currentFreq);
  configureChannels();
  updatePhases();

  // 2. Start Wi-Fi Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  IPAddress IP = WiFi.softAPIP();

  Serial.printf("[WI-FI] Access Point Started: %s\n", AP_SSID);
  Serial.printf("[WI-FI] Connect and Open: http://%s\n", IP.toString().c_str());

  if (MDNS.begin("levitator")) {
    Serial.println("[MDNS] Available at: http://levitator.local");
  }

  // 3. Configure Web Server Routes
  setupWebServer();
  server.begin();

  Serial.printf("[HARDWARE] APB Timer Active: %u Hz (0%% CPU Load)\n", ledc_get_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER));
  printStatus();
}

void loop() {
  // Handle HTTP client requests
  server.handleClient();

  // Handle Serial Monitor commands
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '\r' || cmd == '\n') return;

    switch (cmd) {
      // Frequency tuning
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

      // Phase flip (0 deg <-> 180 deg)
      case 'p':
      case 'P':
        botPhaseTick = (botPhaseTick == 0) ? 128 : 0;
        updatePhases();
        Serial.printf("\n>>> [PHASE] Bottom Phase: %u deg (%s) <<<\n\n", 
                      (botPhaseTick * 360) / 256,
                      (botPhaseTick == 0) ? "IN-PHASE (D ≈ 25.7mm)" : "ANTI-PHASE (D ≈ 21.4mm)");
        break;

      // Vertical translation (UP / DOWN)
      case 'u':
      case 'U':
        botPhaseTick = (botPhaseTick + 4) % 256;
        updatePhases();
        Serial.printf("[MOVE UP] Z-Phase: %u deg\n", (botPhaseTick * 360) / 256);
        break;

      case 'd':
      case 'D':
        botPhaseTick = (botPhaseTick + 256 - 4) % 256;
        updatePhases();
        Serial.printf("[MOVE DOWN] Z-Phase: %u deg\n", (botPhaseTick * 360) / 256);
        break;

      // Horizontal beam steering (LEFT / RIGHT)
      case 'l':
      case 'L':
        xSteerTick = max(-64, xSteerTick - 4);
        updatePhases();
        Serial.printf("[STEER LEFT] X-Steer: %d deg\n", (xSteerTick * 180) / 64);
        break;

      case 'r':
      case 'R':
        xSteerTick = min(64, xSteerTick + 4);
        updatePhases();
        Serial.printf("[STEER RIGHT] X-Steer: %d deg\n", (xSteerTick * 180) / 64);
        break;

      case 'c':
      case 'C':
        botPhaseTick = 0;
        xSteerTick = 0;
        updatePhases();
        Serial.println("[CENTER] Particle reset to central node.");
        break;

      // Array muting
      case 't':
      case 'T':
        topEnabled = !topEnabled;
        updatePhases();
        Serial.printf("[TOP ARRAY] %s\n", topEnabled ? "ACTIVE" : "MUTED");
        break;

      case 'b':
      case 'B':
        botEnabled = !botEnabled;
        updatePhases();
        Serial.printf("[BOTTOM ARRAY] %s\n", botEnabled ? "ACTIVE" : "MUTED");
        break;

      // Auto-sweep
      case 's':
      case 'S':
        Serial.println("\n[SWEEP] Scanning 38.5 kHz -> 41.5 kHz...");
        for (uint32_t f = 38500; f <= 41500; f += 200) {
          currentFreq = f;
          ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
          delay(80);
        }
        currentFreq = 40000;
        ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
        Serial.println("[SWEEP FINISHED] Locked to nominal 40,000 Hz.\n");
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

// ---------------------- Hardware PWM Config ------------------
void configureTimer(uint32_t freq) {
  ledc_timer_config_t timer_conf = {
    .speed_mode       = LEV_LEDC_MODE,
    .duty_resolution  = LEV_RESOLUTION,
    .timer_num        = LEV_LEDC_TIMER,
    .freq_hz          = freq,
    .clk_cfg          = LEDC_USE_APB_CLK   // Explicitly lock to 80 MHz APB crystal clock
  };
  ledc_timer_config(&timer_conf);
}

void configureChannels() {
  // ---- IC 1 — drives Tx1 cross-pair (Bridge 1) AND Tx2 cross-pair (Bridge 2) ----
  // IC1 Phase A (GPIO 4: 0° reference) → IC1 Pin 2 (1A) and Pin 15 (4A)
  ledc_channel_config_t c0 = {
    .gpio_num = PIN_IC1_A, .speed_mode = LEV_LEDC_MODE, .channel = CH_IC1_A,
    .intr_type = LEDC_INTR_DISABLE, .timer_sel = LEV_LEDC_TIMER, .duty = DUTY_50_PERCENT, .hpoint = 0
  };
  ledc_channel_config(&c0);

  // IC1 Phase B (GPIO 5: 180° push-pull complement) → IC1 Pin 7 (2A) and Pin 10 (3A)
  ledc_channel_config_t c1 = {
    .gpio_num = PIN_IC1_B, .speed_mode = LEV_LEDC_MODE, .channel = CH_IC1_B,
    .intr_type = LEDC_INTR_DISABLE, .timer_sel = LEV_LEDC_TIMER, .duty = DUTY_50_PERCENT, .hpoint = 128
  };
  ledc_channel_config(&c1);

  // ---- IC 2 — drives Tx3 cross-pair (Bridge 1 only; Bridge 2 unused) ----
  // IC2 Phase A (GPIO 18: 0°+Z shifted via botPhaseTick) → IC2 Pin 2 (1A) and Pin 15 (4A)
  ledc_channel_config_t c2 = {
    .gpio_num = PIN_IC2_A, .speed_mode = LEV_LEDC_MODE, .channel = CH_IC2_A,
    .intr_type = LEDC_INTR_DISABLE, .timer_sel = LEV_LEDC_TIMER, .duty = DUTY_50_PERCENT, .hpoint = 0
  };
  ledc_channel_config(&c2);

  // IC2 Phase B (GPIO 19: 180°+Z shifted complement) → IC2 Pin 7 (2A) and Pin 10 (3A)
  ledc_channel_config_t c3 = {
    .gpio_num = PIN_IC2_B, .speed_mode = LEV_LEDC_MODE, .channel = CH_IC2_B,
    .intr_type = LEDC_INTR_DISABLE, .timer_sel = LEV_LEDC_TIMER, .duty = DUTY_50_PERCENT, .hpoint = 128
  };
  ledc_channel_config(&c3);
}

void updatePhases() {
  // IC1 drives Tx1 cross-pair (Bridge 1) and Tx2 cross-pair (Bridge 2)
  uint32_t ic1Duty = ic1Enabled ? DUTY_50_PERCENT : 0;
  // IC2 drives Tx3 cross-pair (Bridge 1); Bridge 2 unused
  uint32_t ic2Duty = ic2Enabled ? DUTY_50_PERCENT : 0;

  // 1. IC1 (GPIO 4 & 5): 0° reference phase — drives Tx1 & Tx2 cross-pairs
  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_IC1_A, ic1Duty, 0);
  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_IC1_B, ic1Duty, 128);
  ledc_update_duty(LEV_LEDC_MODE, CH_IC1_A);
  ledc_update_duty(LEV_LEDC_MODE, CH_IC1_B);

  // 2. IC2 (GPIO 18 & 19): Phase shifted by botPhaseTick for Z-height control
  //    Drives Tx3 cross-pair (Bridge 1). The phase difference between IC1 and
  //    IC2 creates the standing wave node position for vertical particle control.
  uint32_t ic2HpointA = botPhaseTick;
  uint32_t ic2HpointB = (botPhaseTick + 128) % 256;
  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_IC2_A, ic2Duty, ic2HpointA);
  ledc_set_duty_with_hpoint(LEV_LEDC_MODE, CH_IC2_B, ic2Duty, ic2HpointB);
  ledc_update_duty(LEV_LEDC_MODE, CH_IC2_A);
  ledc_update_duty(LEV_LEDC_MODE, CH_IC2_B);
}

// ---------------------- Web Server Endpoints -----------------
void setupWebServer() {
  server.enableCORS(true);

  // Serve Main Dashboard
  server.on("/", HTTP_GET, []() {
    server.send_P(200, "text/html", INDEX_HTML);
  });

  // REST API: System Status
  server.on("/api/status", HTTP_GET, []() {
    char buf[256];
    snprintf(buf, sizeof(buf), 
      "{\"freq\":%u,\"zPhase\":%u,\"xSteer\":%d,\"topEnabled\":%s,\"botEnabled\":%s}",
      currentFreq, botPhaseTick, xSteerTick,
      topEnabled ? "true" : "false",
      botEnabled ? "true" : "false"
    );
    server.send(200, "application/json", buf);
  });

  // REST API: 2D Motion (Up/Down/Left/Right/Center)
  server.on("/api/move", HTTP_GET, []() {
    if (server.hasArg("dir")) {
      String dir = server.arg("dir");
      if (server.hasArg("zTick")) botPhaseTick = server.arg("zTick").toInt() % 256;
      if (server.hasArg("xTick")) xSteerTick = constrain(server.arg("xTick").toInt(), -64, 64);

      if (!server.hasArg("zTick") && !server.hasArg("xTick")) {
        if (dir == "up") botPhaseTick = (botPhaseTick + 4) % 256;
        else if (dir == "down") botPhaseTick = (botPhaseTick + 256 - 4) % 256;
        else if (dir == "left") xSteerTick = max(-64, xSteerTick - 4);
        else if (dir == "right") xSteerTick = min(64, xSteerTick + 4);
        else if (dir == "center") { botPhaseTick = 0; xSteerTick = 0; }
      }
      updatePhases();
    }
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });

  // REST API: Carrier Frequency Tuning
  server.on("/api/freq", HTTP_GET, []() {
    if (server.hasArg("val")) {
      uint32_t f = server.arg("val").toInt();
      if (f >= 37000 && f <= 43000) {
        currentFreq = f;
        ledc_set_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER, currentFreq);
      }
    }
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });

  // REST API: Phase Flip
  server.on("/api/phase", HTTP_GET, []() {
    if (server.hasArg("tick")) {
      botPhaseTick = server.arg("tick").toInt() % 256;
    } else {
      botPhaseTick = (botPhaseTick == 0) ? 128 : 0;
    }
    updatePhases();
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });

  // REST API: Array Power Isolation
  server.on("/api/toggle", HTTP_GET, []() {
    if (server.hasArg("target")) {
      String target = server.arg("target");
      if (target == "top") {
        topEnabled = server.hasArg("state") ? (server.arg("state").toInt() == 1) : !topEnabled;
      } else if (target == "bot") {
        botEnabled = server.hasArg("state") ? (server.arg("state").toInt() == 1) : !botEnabled;
      }
      updatePhases();
    }
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });
}

void printStatus() {
  uint32_t actualFreq = ledc_get_freq(LEV_LEDC_MODE, LEV_LEDC_TIMER);
  Serial.println("\n---------------- LIVE STATUS ----------------");
  Serial.printf("  Requested Freq:     %u Hz\n", currentFreq);
  Serial.printf("  Hardware APB Timer: %u Hz (80 MHz Silicon Lock)\n", actualFreq);
  Serial.printf("  Z-Height Phase:     %u deg (Tick: %u)\n", (botPhaseTick * 360) / 256, botPhaseTick);
  Serial.printf("  X-Steer Tilt:       %d deg (Tick: %d)\n", (xSteerTick * 180) / 64, xSteerTick);
  Serial.printf("  IC1 (Tx1+Tx2 pairs, GPIO 4/5):  %s\n", ic1Enabled ? "ACTIVE" : "MUTED");
  Serial.printf("  IC2 (Tx3 pair,      GPIO 18/19): %s\n", ic2Enabled ? "ACTIVE" : "MUTED");
  Serial.printf("  Standing Wave Mode: %s\n",
                (botPhaseTick == 0)  ? "[0 deg]   IN-PHASE   (IC1 ref, IC2 in phase  — D ≈ 25.7mm)" :
                (botPhaseTick == 128)? "[180 deg] ANTI-PHASE (IC1 ref, IC2 anti-phase — D ≈ 21.4mm)" :
                                       "CUSTOM PHASE SHIFT (Z-translation active)");
  Serial.println("  Wiring: IC1 Br1=Top Tx1+Bot Tx1 | IC1 Br2=Top Tx2+Bot Tx2 | IC2 Br1=Top Tx3+Bot Tx3");
  Serial.printf("  Wi-Fi Access Point: %s (IP: 192.168.4.1)\n", AP_SSID);
  Serial.println("---------------- CONTROLS -------------------");
  Serial.println("  [w/s] or [u/d] : Translate Particle UP / DOWN");
  Serial.println("  [a/d] or [l/r] : Steer Particle LEFT / RIGHT");
  Serial.println("  [c] / [Space]  : Reset to Center Trap Node");
  Serial.println("  [p]            : Toggle Phase (0 deg <-> 180 deg)");
  Serial.println("  [+] / [-]      : Tune Carrier Frequency (+/- 100 Hz)");
  Serial.println("  [s]            : Auto-sweep frequency (38.5 kHz - 41.5 kHz)");
  Serial.println("  [t]            : Toggle IC1 (Tx1+Tx2 cross-pairs) ON/OFF");
  Serial.println("  [b]            : Toggle IC2 (Tx3 cross-pair) ON/OFF");
  Serial.println("  [?]            : Print this live status menu");
  Serial.println("---------------------------------------------\n");
}
