/**
 * ACOUSTIC LEVITATOR MISSION CONTROL
 * 2D Particle Trapping & Beam Steering Control System
 */

// ----------------- System State -----------------
const state = {
  espIp: '192.168.4.1',
  connected: false,
  simulationMode: true, // Default to true if hardware ping fails
  currentFreq: 40000,
  zPhaseTick: 0,        // 0..255 (0 = 0 deg, 128 = 180 deg)
  xSteerTick: 0,        // -64..+64 (horizontal phase tilt)
  topEnabled: true,
  botEnabled: true,
  stepSize: 4,          // In ticks
  cavityDistanceMm: 25.7,
  
  // Physical particle position for canvas renderer (in relative units: -100 to +100)
  particle: {
    x: 0,
    y: 0,
    targetX: 0,
    targetY: 0,
    vx: 0,
    vy: 0,
    jitterX: 0,
    jitterY: 0
  },
  
  showInterference: true,
  isSweeping: false
};

// ----------------- DOM Element Selectors -----------------
const elements = {
  // Top telemetry
  topFreq: document.getElementById('top-freq-display'),
  topPhase: document.getElementById('top-phase-display'),
  topSteer: document.getElementById('top-steer-display'),
  connBadge: document.getElementById('connection-badge'),
  connStatusText: document.getElementById('connection-status-text'),
  networkToggleBtn: document.getElementById('network-toggle-btn'),
  configFlyout: document.getElementById('config-flyout'),
  closeFlyoutBtn: document.getElementById('close-flyout'),
  espIpInput: document.getElementById('esp-ip-input'),
  applyIpBtn: document.getElementById('apply-ip-btn'),
  simModeToggle: document.getElementById('sim-mode-toggle'),

  // D-Pad buttons
  btnUp: document.getElementById('btn-up'),
  btnDown: document.getElementById('btn-down'),
  btnLeft: document.getElementById('btn-left'),
  btnRight: document.getElementById('btn-right'),
  btnCenter: document.getElementById('btn-center'),
  valXOffset: document.getElementById('val-x-offset'),
  valXPhase: document.getElementById('val-x-phase'),
  valZOffset: document.getElementById('val-z-offset'),
  valZPhase: document.getElementById('val-z-phase'),
  segButtons: document.querySelectorAll('.seg-btn'),

  // Cavity visualizer
  canvas: document.getElementById('cavity-canvas'),
  modeBadge: document.getElementById('standing-wave-mode-badge'),
  toggleInterferenceBtn: document.getElementById('toggle-interference-btn'),
  btnTogglePhase: document.getElementById('btn-toggle-phase'),
  btnTriggerSweep: document.getElementById('btn-trigger-sweep'),

  // Frequency section
  mainFreqValue: document.getElementById('main-freq-value'),
  freqSlider: document.getElementById('freq-slider'),
  sliderTooltip: document.getElementById('slider-tooltip'),
  freqMinus500: document.getElementById('freq-minus-500'),
  freqMinus100: document.getElementById('freq-minus-100'),
  freqReset: document.getElementById('freq-reset'),
  freqPlus100: document.getElementById('freq-plus-100'),
  freqPlus500: document.getElementById('freq-plus-500'),

  // Array toggles
  cardTopArray: document.getElementById('card-top-array'),
  cardBotArray: document.getElementById('card-bot-array'),
  btnToggleTop: document.getElementById('btn-toggle-top'),
  btnToggleBot: document.getElementById('btn-toggle-bot'),

  // Console
  consoleStream: document.getElementById('console-stream'),
  btnClearConsole: document.getElementById('btn-clear-console'),
  btnStatusQuery: document.getElementById('btn-status-query')
};

// ----------------- Canvas 2D Acoustic Visualizer -----------------
const ctx = elements.canvas.getContext('2d');
let animationFrameId = null;
let wavePhase = 0;

function resizeCanvas() {
  const rect = elements.canvas.getBoundingClientRect();
  elements.canvas.width = rect.width * window.devicePixelRatio;
  elements.canvas.height = rect.height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function drawAcousticCavity() {
  const rect = elements.canvas.getBoundingClientRect();
  const W = rect.width;
  const H = rect.height;

  ctx.clearRect(0, 0, W, H);

  // Grid background
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.05)';
  ctx.lineWidth = 1;
  const gridSize = 25;
  for (let x = 0; x < W; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, H);
    ctx.stroke();
  }
  for (let y = 0; y < H; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(W, y);
    ctx.stroke();
  }

  // Cavity geometry limits
  const topTransducerY = 45;
  const bottomTransducerY = H - 45;
  const cavityMidY = (topTransducerY + bottomTransducerY) / 2;
  const centerX = W / 2;
  const transducerSpacing = 80;

  // 1. Draw Transducer Arrays (4 Top, 4 Bottom)
  const transducerSpacing = 65;
  const topTransducers = [
    { x: centerX - 1.5 * transducerSpacing, label: 'Tx 1' },
    { x: centerX - 0.5 * transducerSpacing, label: 'Tx 2' },
    { x: centerX + 0.5 * transducerSpacing, label: 'Tx 3' },
    { x: centerX + 1.5 * transducerSpacing, label: 'Tx 4' }
  ];
  const botTransducers = [
    { x: centerX - 1.5 * transducerSpacing, label: 'Tx 5' },
    { x: centerX - 0.5 * transducerSpacing, label: 'Tx 6' },
    { x: centerX + 0.5 * transducerSpacing, label: 'Tx 7' },
    { x: centerX + 1.5 * transducerSpacing, label: 'Tx 8' }
  ];

  // Draw Top Plate
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = state.topEnabled ? 'rgba(0, 240, 255, 0.5)' : 'rgba(239, 68, 68, 0.4)';
  ctx.lineWidth = 2;
  ctx.fillRect(centerX - 150, 10, 300, 20);
  ctx.strokeRect(centerX - 150, 10, 300, 20);

  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.font = '9px "JetBrains Mono"';
  ctx.textAlign = 'center';
  ctx.fillText('TOP ARRAY (4x TRANSMITTERS - FACING DOWN)', centerX, 23);

  // Draw Bottom Plate
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = state.botEnabled ? 'rgba(0, 240, 255, 0.5)' : 'rgba(239, 68, 68, 0.4)';
  ctx.lineWidth = 2;
  ctx.fillRect(centerX - 150, H - 30, 300, 20);
  ctx.strokeRect(centerX - 150, H - 30, 300, 20);

  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.fillText('BOTTOM ARRAY (4x TRANSMITTERS - FACING UP)', centerX, H - 17);

  // Render individual transducer horns
  function renderHorn(x, y, isTop, active, label) {
    const width = 44;
    const height = 18;
    const hornY = isTop ? y - 15 : y;

    // Metal can body
    ctx.fillStyle = active ? '#1e293b' : '#0f172a';
    ctx.strokeStyle = active ? '#38bdf8' : '#64748b';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(x - width / 2, hornY, width, height, 4);
    ctx.fill();
    ctx.stroke();

    // Piezo emitter rim
    ctx.fillStyle = active ? '#00f0ff' : '#475569';
    ctx.beginPath();
    ctx.arc(x, isTop ? hornY + height : hornY, 5, 0, Math.PI * 2);
    ctx.fill();

    // Transducer label
    ctx.fillStyle = active ? '#94a3b8' : '#475569';
    ctx.font = '8px "JetBrains Mono"';
    ctx.fillText(label, x, isTop ? hornY - 3 : hornY + height + 10);
  }

  topTransducers.forEach(tx => renderHorn(tx.x, topTransducerY, true, state.topEnabled, tx.label));
  botTransducers.forEach(tx => renderHorn(tx.x, bottomTransducerY, false, state.botEnabled, tx.label));

  // 2. Render Standing Wavefield & Acoustic Interference Waves
  if (state.showInterference && (state.topEnabled || state.botEnabled)) {
    wavePhase += 0.08;

    // Wavefront arcs from Top transducers
    if (state.topEnabled) {
      topTransducers.forEach((tx, idx) => {
        // Apply horizontal phase tilt
        const phaseOffset = (idx - 1) * (state.xSteerTick * 0.05);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)';
        ctx.lineWidth = 1.5;
        for (let r = 20; r < 140; r += 24) {
          const arcR = r + ((wavePhase + phaseOffset) % 24);
          ctx.beginPath();
          ctx.arc(tx.x, topTransducerY + 5, arcR, 0.15 * Math.PI, 0.85 * Math.PI);
          ctx.stroke();
        }
      });
    }

    // Wavefront arcs from Bottom transducers
    if (state.botEnabled) {
      botTransducers.forEach((tx, idx) => {
        const phaseOffset = (idx - 1) * (state.xSteerTick * 0.05) + (state.zPhaseTick * (Math.PI / 128));
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.15)';
        ctx.lineWidth = 1.5;
        for (let r = 20; r < 140; r += 24) {
          const arcR = r + ((wavePhase + phaseOffset) % 24);
          ctx.beginPath();
          ctx.arc(tx.x, bottomTransducerY - 5, arcR, 1.15 * Math.PI, 1.85 * Math.PI);
          ctx.stroke();
        }
      });
    }

    // Standing Wave Node Planes (Horizontal interference bands)
    const nodeCount = 5;
    const nodeSpan = (bottomTransducerY - topTransducerY - 40) / (nodeCount + 1);
    const zPhaseShift = (state.zPhaseTick / 256) * nodeSpan;

    for (let i = 1; i <= nodeCount; i++) {
      const nodeY = topTransducerY + 20 + i * nodeSpan + zPhaseShift;
      if (nodeY > topTransducerY + 15 && nodeY < bottomTransducerY - 15) {
        ctx.strokeStyle = (i === 3) ? 'rgba(16, 185, 129, 0.45)' : 'rgba(56, 189, 248, 0.18)';
        ctx.lineWidth = (i === 3) ? 1.5 : 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(centerX - 130, nodeY);
        ctx.lineTo(centerX + 130, nodeY);
        ctx.stroke();
        ctx.setLineDash([]);

        if (i === 3) {
          ctx.fillStyle = 'rgba(16, 185, 129, 0.7)';
          ctx.font = '8px "JetBrains Mono"';
          ctx.textAlign = 'right';
          ctx.fillText('PRIMARY TRAP NODE', centerX - 135, nodeY + 3);
        }
      }
    }
  }

  // 3. Levitated Particle (Physics + Rendering)
  // Target position mapped to canvas coordinates
  // X: -64..+64 ticks -> +/- 80 pixels
  // Z: 0..255 ticks -> +/- 40 pixels
  const targetCanvasX = centerX + (state.xSteerTick / 64) * 85;
  const targetCanvasZ = cavityMidY - ((state.zPhaseTick - 64) / 128) * 35;

  state.particle.targetX = targetCanvasX;
  state.particle.targetY = targetCanvasZ;

  // Spring physics towards target
  const k = 0.08;
  const damping = 0.82;
  const ax = (state.particle.targetX - state.particle.x) * k;
  const ay = (state.particle.targetY - state.particle.y) * k;

  state.particle.vx = (state.particle.vx + ax) * damping;
  state.particle.vy = (state.particle.vy + ay) * damping;

  state.particle.x += state.particle.vx;
  state.particle.y += state.particle.vy;

  // Brownian micro-jitter in standing wave trap
  state.particle.jitterX = (Math.random() - 0.5) * 0.8;
  state.particle.jitterY = (Math.random() - 0.5) * 0.8;

  const drawX = state.particle.x + state.particle.jitterX;
  const drawY = state.particle.y + state.particle.jitterY;

  // Only render particle if both arrays (or at least one) are active
  if (state.topEnabled && state.botEnabled) {
    // Particle outer glow
    const grad = ctx.createRadialGradient(drawX, drawY, 2, drawX, drawY, 16);
    grad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
    grad.addColorStop(0.3, 'rgba(0, 240, 255, 0.8)');
    grad.addColorStop(0.7, 'rgba(168, 85, 247, 0.3)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(drawX, drawY, 16, 0, Math.PI * 2);
    ctx.fill();

    // Particle core (expanded polystyrene styrofoam bead, ~2mm visual)
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(drawX, drawY, 4.5, 0, Math.PI * 2);
    ctx.fill();

    // Crosshair lock indicators
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(drawX, drawY, 10, 0, Math.PI * 2);
    ctx.stroke();

    // Coordinates tooltip floating over particle
    ctx.fillStyle = 'rgba(0, 240, 255, 0.9)';
    ctx.font = '9px "JetBrains Mono"';
    ctx.textAlign = 'center';
    const xMm = ((state.xSteerTick / 64) * 5.0).toFixed(1);
    const zMm = (((state.zPhaseTick - 64) / 128) * 4.3).toFixed(1);
    ctx.fillText(`(${xMm > 0 ? '+' : ''}${xMm}, ${zMm > 0 ? '+' : ''}${zMm}) mm`, drawX, drawY - 14);
  } else {
    // Particle dropped / fallen message
    ctx.fillStyle = 'rgba(239, 68, 68, 0.8)';
    ctx.font = '12px "Orbitron"';
    ctx.textAlign = 'center';
    ctx.fillText('ACOUSTIC TRAP INACTIVE — ARRAY MUTED', centerX, cavityMidY);
  }

  animationFrameId = requestAnimationFrame(drawAcousticCavity);
}

// Initialize particle to center
state.particle.x = window.innerWidth > 800 ? 300 : 150;
state.particle.y = 190;
drawAcousticCavity();

// ----------------- Console Stream Logger -----------------
function logConsole(message, type = 'info') {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
  elements.consoleStream.appendChild(entry);
  elements.consoleStream.scrollTop = elements.consoleStream.scrollHeight;
}

// ----------------- ESP32 REST API Communication -----------------
async function sendCommand(endpoint, params = {}) {
  const query = new URLSearchParams(params).toString();
  const url = `http://${state.espIp}/api/${endpoint}${query ? '?' + query : ''}`;

  if (state.simulationMode) {
    // Hardware Emulation Mode
    logConsole(`[SIMULATOR] Sent /api/${endpoint} ${JSON.stringify(params)}`, 'info');
    return { ok: true, simulated: true };
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);

    const res = await fetch(url, {
      method: 'GET',
      mode: 'cors',
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      setConnectionStatus(true);
      const data = await res.json().catch(() => ({}));
      return { ok: true, data };
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    logConsole(`[OFFLINE] Could not reach ESP32 at ${state.espIp}. Running in simulation mode.`, 'warning');
    setConnectionStatus(false);
    return { ok: false, error: err.message };
  }
}

function setConnectionStatus(online) {
  state.connected = online;
  if (online) {
    elements.connBadge.className = 'status-indicator connected';
    elements.connStatusText.textContent = `ESP32 LIVE (${state.espIp})`;
    state.simulationMode = false;
    elements.simModeToggle.checked = false;
  } else {
    elements.connBadge.className = 'status-indicator simulation';
    elements.connStatusText.textContent = 'SIMULATION MODE';
    state.simulationMode = true;
    elements.simModeToggle.checked = true;
  }
}

// ----------------- UI State Synchronization -----------------
function updateUI() {
  // Frequency displays
  const formattedFreq = state.currentFreq.toLocaleString();
  elements.topFreq.textContent = `${formattedFreq} Hz`;
  elements.mainFreqValue.textContent = formattedFreq;
  elements.freqSlider.value = state.currentFreq;
  elements.sliderTooltip.textContent = `${formattedFreq} Hz`;

  // Phase displays (Z-axis translation)
  const zDeg = Math.round((state.zPhaseTick * 360) / 256);
  elements.topPhase.textContent = `${zDeg}°`;
  elements.valZPhase.textContent = `Phase: ${zDeg}°`;
  const zMm = (((state.zPhaseTick - 64) / 128) * 4.3).toFixed(2);
  elements.valZOffset.textContent = `${zMm > 0 ? '+' : ''}${zMm} mm`;

  // Steering displays (X-axis translation)
  const xDeg = Math.round((state.xSteerTick * 180) / 64);
  elements.topSteer.textContent = `${xDeg > 0 ? '+' : ''}${xDeg}°`;
  elements.valXPhase.textContent = `Phase: ${xDeg > 0 ? '+' : ''}${xDeg}°`;
  const xMm = ((state.xSteerTick / 64) * 5.0).toFixed(2);
  elements.valXOffset.textContent = `${xMm > 0 ? '+' : ''}${xMm} mm`;

  // Standing wave mode badge
  if (state.zPhaseTick === 0 || state.zPhaseTick === 256) {
    elements.modeBadge.textContent = '0° IN-PHASE (D ≈ 25.7mm, 34.3mm)';
    elements.modeBadge.className = 'badge-mode';
  } else if (state.zPhaseTick === 128) {
    elements.modeBadge.textContent = '180° ANTI-PHASE (D ≈ 21.4mm, 30.0mm)';
    elements.modeBadge.className = 'badge-mode text-purple';
  } else {
    elements.modeBadge.textContent = `PHASE SHIFT: ${zDeg}° (Z-STEER ACTIVE)`;
    elements.modeBadge.className = 'badge-mode text-amber';
  }

  // Array toggles
  elements.cardTopArray.className = state.topEnabled ? 'array-card active' : 'array-card muted';
  elements.btnToggleTop.querySelector('.state-text').textContent = state.topEnabled ? 'ACTIVE' : 'MUTED';

  elements.cardBotArray.className = state.botEnabled ? 'array-card active' : 'array-card muted';
  elements.btnToggleBot.querySelector('.state-text').textContent = state.botEnabled ? 'ACTIVE' : 'MUTED';
}

// ----------------- Motion Control Handlers -----------------
async function moveParticle(direction) {
  let step = state.stepSize;

  switch (direction) {
    case 'up':
      // Move Z Up (increase bottom phase delay)
      state.zPhaseTick = (state.zPhaseTick + step) % 256;
      animateButton(elements.btnUp);
      logConsole(`[MOVE UP] Z-Phase: ${(state.zPhaseTick * 360 / 256).toFixed(0)}°`, 'info');
      break;

    case 'down':
      // Move Z Down (decrease bottom phase delay)
      state.zPhaseTick = (state.zPhaseTick + 256 - step) % 256;
      animateButton(elements.btnDown);
      logConsole(`[MOVE DOWN] Z-Phase: ${(state.zPhaseTick * 360 / 256).toFixed(0)}°`, 'info');
      break;

    case 'left':
      // Move X Left (tilt phase leftwards)
      state.xSteerTick = Math.max(-64, state.xSteerTick - step);
      animateButton(elements.btnLeft);
      logConsole(`[STEER LEFT] X-Tilt: ${(state.xSteerTick * 180 / 64).toFixed(0)}°`, 'info');
      break;

    case 'right':
      // Move X Right (tilt phase rightwards)
      state.xSteerTick = Math.min(64, state.xSteerTick + step);
      animateButton(elements.btnRight);
      logConsole(`[STEER RIGHT] X-Tilt: ${(state.xSteerTick * 180 / 64).toFixed(0)}°`, 'info');
      break;

    case 'center':
      state.zPhaseTick = 0;
      state.xSteerTick = 0;
      animateButton(elements.btnCenter);
      logConsole('[CENTER] Reset acoustic trap to dead center (X: 0mm, Z: 0mm)', 'success');
      break;
  }

  updateUI();
  await sendCommand('move', { 
    dir: direction, 
    zTick: state.zPhaseTick, 
    xTick: state.xSteerTick 
  });
}

function animateButton(btn) {
  if (!btn) return;
  btn.classList.add('pressed');
  setTimeout(() => btn.classList.remove('pressed'), 140);
}

// ----------------- Frequency Control Handlers -----------------
async function setFrequency(newFreq) {
  state.currentFreq = Math.max(37000, Math.min(43000, newFreq));
  updateUI();
  logConsole(`[FREQ] Carrier tuned to ${state.currentFreq} Hz`, 'info');
  await sendCommand('freq', { val: state.currentFreq });
}

// ----------------- Phase Toggle Handler -----------------
async function togglePhase() {
  if (state.zPhaseTick === 0) {
    state.zPhaseTick = 128; // Anti-phase (180 deg)
    logConsole('[PHASE] Switched to 180° ANTI-PHASE (Best for odd D ≈ 21.4mm)', 'warning');
  } else {
    state.zPhaseTick = 0;   // In-phase (0 deg)
    logConsole('[PHASE] Switched to 0° IN-PHASE (Best for even D ≈ 25.7mm, 34.3mm)', 'success');
  }
  updateUI();
  await sendCommand('phase', { tick: state.zPhaseTick });
}

// ----------------- Auto-Sweep Handler -----------------
async function runAutoSweep() {
  if (state.isSweeping) return;
  state.isSweeping = true;
  elements.btnTriggerSweep.disabled = true;
  logConsole('[SWEEP] Starting resonance sweep from 38,500 Hz to 41,500 Hz...', 'warning');

  const startF = 38500;
  const endF = 41500;
  const stepF = 200;

  for (let f = startF; f <= endF; f += stepF) {
    state.currentFreq = f;
    updateUI();
    logConsole(`  >> Scanning: ${f} Hz`, 'info');
    await new Promise(r => setTimeout(r, 120));
  }

  state.currentFreq = 40000;
  state.isSweeping = false;
  elements.btnTriggerSweep.disabled = false;
  updateUI();
  logConsole('[SWEEP FINISHED] Frequency locked back to nominal 40,000 Hz.', 'success');
  await sendCommand('freq', { val: 40000 });
}

// ----------------- Array Toggle Handlers -----------------
async function toggleTopArray() {
  state.topEnabled = !state.topEnabled;
  updateUI();
  logConsole(`[ARRAY] Top Array (3 Transmitters) is now ${state.topEnabled ? 'ACTIVE' : 'MUTED'}`, state.topEnabled ? 'success' : 'error');
  await sendCommand('toggle', { target: 'top', state: state.topEnabled ? 1 : 0 });
}

async function toggleBottomArray() {
  state.botEnabled = !state.botEnabled;
  updateUI();
  logConsole(`[ARRAY] Bottom Array (3 Transmitters) is now ${state.botEnabled ? 'ACTIVE' : 'MUTED'}`, state.botEnabled ? 'success' : 'error');
  await sendCommand('toggle', { target: 'bot', state: state.botEnabled ? 1 : 0 });
}

// ----------------- Event Listeners -----------------
// D-Pad clicks
elements.btnUp.addEventListener('click', () => moveParticle('up'));
elements.btnDown.addEventListener('click', () => moveParticle('down'));
elements.btnLeft.addEventListener('click', () => moveParticle('left'));
elements.btnRight.addEventListener('click', () => moveParticle('right'));
elements.btnCenter.addEventListener('click', () => moveParticle('center'));

// Sensitivity Segmented buttons
elements.segButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    elements.segButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.stepSize = parseInt(btn.dataset.step, 10);
    logConsole(`[CONFIG] Step sensitivity set to ${btn.textContent}`, 'info');
  });
});

// Phase toggle & Sweep
elements.btnTogglePhase.addEventListener('click', togglePhase);
elements.btnTriggerSweep.addEventListener('click', runAutoSweep);
elements.toggleInterferenceBtn.addEventListener('click', () => {
  state.showInterference = !state.showInterference;
  logConsole(`[VIEW] Standing wave field vectors ${state.showInterference ? 'ENABLED' : 'HIDDEN'}`, 'info');
});

// Frequency Controls
elements.freqMinus500.addEventListener('click', () => setFrequency(state.currentFreq - 500));
elements.freqMinus100.addEventListener('click', () => setFrequency(state.currentFreq - 100));
elements.freqReset.addEventListener('click', () => setFrequency(40000));
elements.freqPlus100.addEventListener('click', () => setFrequency(state.currentFreq + 100));
elements.freqPlus500.addEventListener('click', () => setFrequency(state.currentFreq + 500));

elements.freqSlider.addEventListener('input', (e) => {
  const val = parseInt(e.target.value, 10);
  elements.sliderTooltip.textContent = `${val.toLocaleString()} Hz`;
  elements.mainFreqValue.textContent = val.toLocaleString();
});

elements.freqSlider.addEventListener('change', (e) => {
  setFrequency(parseInt(e.target.value, 10));
});

// Array Power Toggles
elements.btnToggleTop.addEventListener('click', toggleTopArray);
elements.btnToggleBot.addEventListener('click', toggleBottomArray);

// Console buttons
elements.btnClearConsole.addEventListener('click', () => {
  elements.consoleStream.innerHTML = '';
});

elements.btnStatusQuery.addEventListener('click', async () => {
  logConsole('[STATUS] Polling live hardware telemetry...', 'info');
  const res = await sendCommand('status');
  if (res.ok && res.data) {
    if (res.data.freq) state.currentFreq = res.data.freq;
    if (res.data.zPhase !== undefined) state.zPhaseTick = res.data.zPhase;
    if (res.data.xSteer !== undefined) state.xSteerTick = res.data.xSteer;
    updateUI();
    logConsole(`[STATUS] Telemetry Synced: ${state.currentFreq} Hz | Z-Phase: ${state.zPhaseTick} | X-Steer: ${state.xSteerTick}`, 'success');
  }
});

// Network / Configuration Flyout
elements.networkToggleBtn.addEventListener('click', () => {
  elements.configFlyout.classList.toggle('active');
});

elements.closeFlyoutBtn.addEventListener('click', () => {
  elements.configFlyout.classList.remove('active');
});

elements.applyIpBtn.addEventListener('click', () => {
  const ip = elements.espIpInput.value.trim();
  if (ip) {
    state.espIp = ip;
    state.simulationMode = false;
    elements.simModeToggle.checked = false;
    logConsole(`[NETWORK] Target ESP32 IP set to: http://${state.espIp}`, 'success');
    elements.configFlyout.classList.remove('active');
    sendCommand('status');
  }
});

elements.simModeToggle.addEventListener('change', (e) => {
  state.simulationMode = e.target.checked;
  setConnectionStatus(!state.simulationMode);
  logConsole(`[MODE] Hardware Emulation Mode ${state.simulationMode ? 'ACTIVATED' : 'DEACTIVATED'}`, 'warning');
});

// Keyboard Navigation Listener
window.addEventListener('keydown', (e) => {
  // Ignore typing inside inputs
  if (e.target.tagName === 'INPUT') return;

  switch (e.key.toLowerCase()) {
    case 'w':
    case 'arrowup':
      e.preventDefault();
      moveParticle('up');
      break;

    case 's':
    case 'arrowdown':
      e.preventDefault();
      moveParticle('down');
      break;

    case 'a':
    case 'arrowleft':
      e.preventDefault();
      moveParticle('left');
      break;

    case 'd':
    case 'arrowright':
      e.preventDefault();
      moveParticle('right');
      break;

    case ' ':
      e.preventDefault();
      moveParticle('center');
      break;

    case 'p':
      e.preventDefault();
      togglePhase();
      break;

    case '+':
    case '=':
      e.preventDefault();
      setFrequency(state.currentFreq + 100);
      break;

    case '-':
    case '_':
      e.preventDefault();
      setFrequency(state.currentFreq - 100);
      break;

    case 't':
      e.preventDefault();
      toggleTopArray();
      break;

    case 'b':
      e.preventDefault();
      toggleBottomArray();
      break;
  }
});

// Initial boot check
updateUI();
setTimeout(() => {
  sendCommand('status');
}, 600);
