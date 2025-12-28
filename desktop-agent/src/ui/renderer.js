// ZION Desktop Mining Agent v2.9 - Renderer Process
// UI logic and state management

let currentView = 'dashboard';
let config = {};
let isRunning = false;

let cpuThreadMax = 32;

// Hashrate units
const HASHRATE_UNIT_CYCLE = ['auto', 'H/s', 'kH/s', 'MH/s', 'GH/s'];
let hashrateUnitMode = 'auto';
let lastMilestoneBucket = 0;
let lastAcceptedForMilestone = 0;
let milestoneInitialized = false;

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
  console.log('Renderer DOMContentLoaded fired');

  try {
    console.log('Step 1: Init starfield...');
    initWarpStarfield();
    console.log('✓ Starfield OK');
    
    console.log('Step 2: Load config...');
    config = await window.electronAPI.getConfig();
    console.log('✓ Config loaded:', config);
    
    console.log('Step 3: Load system limits...');
    await loadSystemLimits();
    console.log('✓ System limits loaded');
    
    console.log('Step 4: Update settings UI...');
    updateSettingsUI();
    console.log('✓ Settings UI updated');
    
    console.log('Step 5: Setup threads control...');
    setupThreadsControl();
    console.log('✓ Threads control setup');
    
    console.log('Step 6: Setup navigation...');
    setupNavigation();
    console.log('✓ Navigation setup');
    
    console.log('Step 7: Setup controls...');
    setupControls();
    console.log('✓ Controls setup');
    
    console.log('Step 8: Setup wallet controls...');
    setupWalletControls();
    console.log('✓ Wallet controls setup');

    console.log('Step 8b: Setup AI/chat controls...');
    setupAiControls();
    setupChatControls();
    console.log('✓ AI/chat controls setup');
    
    console.log('Step 9: Setup event listeners...');
    setupEventListeners();
    console.log('✓ Event listeners setup');
    
    console.log('Step 10: Start polling stats...');
    pollStats();
    console.log('✓ Polling started');

    console.log('✅ Renderer initialization complete!');
  } catch (err) {
    console.error('❌ Renderer initialization failed:', err);
    console.error('Error stack:', err?.stack);
    alert(`Failed to initialize UI:\n\n${err?.message || String(err)}\n\nCheck DevTools console for details.`);
    throw err;
  }
});

async function loadSystemLimits() {
  try {
    if (typeof window.electronAPI?.getSystemInfo !== 'function') {
      console.warn('getSystemInfo not available');
      return;
    }
    const info = await window.electronAPI.getSystemInfo();
    console.log('System info:', info);
    const cpuCount = Number(info?.cpuCount);
    if (Number.isFinite(cpuCount) && cpuCount > 0) {
      cpuThreadMax = Math.max(1, Math.floor(cpuCount));
      console.log('CPU thread max:', cpuThreadMax);
    }
  } catch (err) {
    console.error('Failed to load system limits:', err);
  }
}

function setupThreadsControl() {
  const threadsInput = document.getElementById('threads-input');
  const threadsValueEl = document.getElementById('threads-value');
  const threadsMaxEl = document.getElementById('threads-max');

  if (!(threadsInput instanceof HTMLInputElement)) return;

  threadsInput.min = '1';
  threadsInput.max = String(cpuThreadMax);

  const clampThreads = (value) => {
    const n = Number(value);
    if (!Number.isFinite(n)) return 1;
    return Math.min(cpuThreadMax, Math.max(1, Math.floor(n)));
  };

  const initial = clampThreads(config.threads ?? 4);
  config.threads = initial;
  threadsInput.value = String(initial);

  if (threadsValueEl) threadsValueEl.textContent = String(initial);
  if (threadsMaxEl) threadsMaxEl.textContent = String(cpuThreadMax);

  threadsInput.addEventListener('input', () => {
    const next = clampThreads(threadsInput.value);
    config.threads = next;
    if (threadsValueEl) threadsValueEl.textContent = String(next);
  });
}

function initWarpStarfield() {
  const canvas = document.getElementById('warp-starfield');
  if (!(canvas instanceof HTMLCanvasElement)) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const starColor = [200, 118, 255]; // galactic-core
  // Performance-aware parameters
  let dpr = window.devicePixelRatio || 1;
  let w = 0;
  let h = 0;
  // Dynamic density scales with resolution and honors reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const baseDensity = prefersReducedMotion ? 120 : 240;
  let density = baseDensity;
  let speed = prefersReducedMotion ? 2.4 : 3.2;
  let trailOpacity = prefersReducedMotion ? 0.06 : 0.045;
  const backgroundGradient = (w, h) => {
    const gradient = ctx.createRadialGradient(w * 0.4, h * 0.6, 0, w * 0.4, h * 0.6, Math.max(w, h));
    gradient.addColorStop(0, 'rgba(22, 8, 32, 0.90)');
    gradient.addColorStop(1, 'rgba(4, 2, 12, 0.98)');
    return gradient;
  };

  const stars = [];
  let frameId = 0;
  let running = true;

  const resize = () => {
    dpr = window.devicePixelRatio || 1;
    w = Math.floor(window.innerWidth);
    h = Math.floor(window.innerHeight);
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Recompute density based on area and DPR (cap to avoid overdraw)
    const areaScale = Math.sqrt((w * h) / (1280 * 800));
    density = Math.max(80, Math.min(320, Math.round(baseDensity * areaScale / Math.sqrt(dpr))));
  };

  const seed = () => {
    stars.length = 0;
    for (let i = 0; i < density; i++) {
      stars.push({
        x: Math.random() * w - w / 2,
        y: Math.random() * h - h / 2,
        z: Math.random() * w,
        size: Math.random() * 2 + 0.5,
        px: 0,
        py: 0,
      });
    }
  };

  const animate = () => {
    if (!running) return;
    ctx.fillStyle = `rgba(0, 0, 0, ${Math.min(Math.max(trailOpacity, 0.02), 0.3)})`;
    ctx.fillRect(0, 0, w, h);

    // Subtle gradient base to match web warp deck
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = backgroundGradient(w, h);
    ctx.globalAlpha = 0.22;
    ctx.fillRect(0, 0, w, h);
    ctx.globalAlpha = 1;

    for (const star of stars) {
      // Previous projected point (for streak)
      const prevX = (star.x / star.z) * w + w / 2;
      const prevY = (star.y / star.z) * h + h / 2;

      star.z -= speed;
      if (star.z <= 0) {
        star.z = w;
        star.x = Math.random() * w - w / 2;
        star.y = Math.random() * h - h / 2;
        star.px = prevX;
        star.py = prevY;
        continue;
      }

      const x = (star.x / star.z) * w + w / 2;
      const y = (star.y / star.z) * h + h / 2;
      const size = (1 - star.z / w) * star.size * 2;

      const brightness = 1 - star.z / w;
      const alpha = Math.min(1, 0.08 + brightness * 0.92);

      // Warp streaks
      ctx.strokeStyle = `rgba(${starColor[0]}, ${starColor[1]}, ${starColor[2]}, ${alpha})`;
      // DPR-aware line width to avoid overly thick strokes
      ctx.lineWidth = Math.max(0.5, (size * 0.5) / Math.sqrt(dpr));
      ctx.beginPath();
      ctx.moveTo(prevX, prevY);
      ctx.lineTo(x, y);
      ctx.stroke();

      // Bright head dot for depth
      ctx.fillStyle = `rgba(${starColor[0]}, ${starColor[1]}, ${starColor[2]}, ${Math.min(1, alpha + 0.15)})`;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(size * 0.65, 0.55), 0, Math.PI * 2);
      ctx.fill();

      star.px = x;
      star.py = y;
    }

    frameId = window.requestAnimationFrame(animate);
  };

  resize();
  seed();
  animate();

  window.addEventListener('resize', () => {
    resize();
    seed();
  });

  window.addEventListener('beforeunload', () => {
    if (frameId) window.cancelAnimationFrame(frameId);
  });

  // Pause animation when tab/app is not visible to save CPU/GPU
  document.addEventListener('visibilitychange', () => {
    const nowHidden = document.hidden;
    running = !nowHidden;
    if (running) {
      // Re-seed lightly on resume for a smoother feel
      seed();
      if (!frameId) animate();
    }
  });
}

// Navigation
function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const view = item.dataset.view;
      switchView(view);
      
      // Update active state
      navItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
    });
  });
}

function switchView(view) {
  // Hide all views
  document.querySelectorAll('[id$="-view"]').forEach(v => {
    v.style.display = 'none';
  });
  
  // Show selected view
  document.getElementById(`${view}-view`).style.display = 'block';
  currentView = view;
}

// Control setup
function setupControls() {
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');
  const saveSettingsBtn = document.getElementById('save-settings-btn');
  const openLogsBtn = document.getElementById('open-logs-btn');
  const hashrateUnitEl = document.getElementById('hashrate-unit');
  const algoSelect = document.getElementById('algo-select');
  const algoSaveBtn = document.getElementById('algo-save-btn');
  const algoStatusEl = document.getElementById('algo-status');

  // Load persisted unit preference
  try {
    const saved = window.localStorage.getItem('zion.hashrateUnitMode');
    if (saved && HASHRATE_UNIT_CYCLE.includes(saved)) {
      hashrateUnitMode = saved;
    }
  } catch {
    // ignore
  }

  const renderHashrateUnitLabel = () => {
    if (!hashrateUnitEl) return;
    hashrateUnitEl.textContent = hashrateUnitMode === 'auto' ? 'Auto' : hashrateUnitMode;
  };

  const cycleHashrateUnit = () => {
    const idx = HASHRATE_UNIT_CYCLE.indexOf(hashrateUnitMode);
    hashrateUnitMode = HASHRATE_UNIT_CYCLE[(idx + 1) % HASHRATE_UNIT_CYCLE.length];
    try {
      window.localStorage.setItem('zion.hashrateUnitMode', hashrateUnitMode);
    } catch {
      // ignore
    }
    renderHashrateUnitLabel();
    // Force redraw with current stats (if present)
    window.electronAPI.getStats().then(updateStats).catch(() => {});
  };

  if (hashrateUnitEl) {
    renderHashrateUnitLabel();
    hashrateUnitEl.addEventListener('click', cycleHashrateUnit);
  }

  const syncAlgoUi = () => {
    if (!algoSelect) return;
    algoSelect.value = (config.algorithm || 'cosmic_harmony');
    if (algoStatusEl) {
      algoStatusEl.textContent = `Current: ${algoSelect.value}${isRunning ? ' (restart miner to apply)' : ''}`;
    }
  };

  const applyAlgo = async () => {
    if (!algoSelect) return;
    config.algorithm = algoSelect.value;
    await window.electronAPI.saveConfig(config);
    if (algoStatusEl) {
      algoStatusEl.textContent = `Saved: ${config.algorithm}${isRunning ? ' (restart miner to apply)' : ''}`;
    }
    addLogEntry(`Algorithm set: ${config.algorithm}`, 'info');
    if (isRunning) {
      const ok = confirm('Algorithm saved. Restart mining now to apply the new algorithm?');
      if (ok) {
        addLogEntry(`Restarting miner to apply algorithm: ${config.algorithm}`, 'warning');
        await window.electronAPI.stopMining();
        const result = await window.electronAPI.startMining(config);
        if (!result?.success) {
          const msg = result?.error || 'Failed to restart miner.';
          addLogEntry(`Restart failed: ${msg}`, 'error');
          alert(msg);
          if (algoStatusEl) {
            algoStatusEl.textContent = `Saved: ${config.algorithm} (restart failed)`;
          }
          return;
        }
        if (algoStatusEl) {
          algoStatusEl.textContent = `Applied: ${config.algorithm}`;
        }
      } else {
        alert('Algorithm saved. Stop/Start mining to apply.');
      }
    }
  };

  algoSaveBtn?.addEventListener('click', applyAlgo);
  algoSelect?.addEventListener('change', () => {
    // Keep UX explicit: selection change doesn't silently affect mining.
    if (algoStatusEl) algoStatusEl.textContent = `Selected: ${algoSelect.value} (click Apply)`;
  });
  
  startBtn.addEventListener('click', async () => {
    if (!config.wallet) {
      alert('Please configure your wallet address in Settings first.');
      switchView('settings');
      return;
    }
    
    const result = await window.electronAPI.startMining(config);
    if (result.success) {
      console.log('Mining started');
      return;
    }

    const msg = result?.error || 'Failed to start mining.';
    addLogEntry(`Start failed: ${msg}`, 'error');
    alert(msg);
  });

  // Initial sync
  syncAlgoUi();
  
  stopBtn.addEventListener('click', async () => {
    const result = await window.electronAPI.stopMining();
    if (result.success) {
      console.log('Mining stopped');
    }
  });
  
  saveSettingsBtn.addEventListener('click', async () => {
    // Read settings from UI
    const poolInput = document.getElementById('pool-input').value;
    const [host, port] = poolInput.split(':');
    
    config = {
      pool: {
        host: host || 'pool.zionterranova.com',
        port: parseInt(port) || 3333
      },
      rpcUrl: document.getElementById('rpc-url')?.value || config.rpcUrl,
      algorithm: config.algorithm || 'cosmic_harmony',
      aiAfterburner: config.aiAfterburner !== false,
      chatEndpoint: config.chatEndpoint,
      chatModel: config.chatModel,
      wallet: document.getElementById('wallet-input').value,
      worker: document.getElementById('worker-input').value,
      threads: Math.min(
        cpuThreadMax,
        Math.max(1, parseInt(document.getElementById('threads-input').value) || 1)
      ),
      gpu: document.getElementById('gpu-checkbox').checked,
      autoStart: document.getElementById('autostart-checkbox').checked,
      minimizeToTray: true,
      startMinimized: false
    };
    
    const result = await window.electronAPI.saveConfig(config);
    if (result) {
      alert('Settings saved successfully!');
    } else {
      alert('Failed to save settings.');
    }
  });
  
  if (openLogsBtn) {
    openLogsBtn.addEventListener('click', async () => {
      await window.electronAPI.openLogs();
    });
  }
}

function formatHashrate(valueHs) {
  const hs = typeof valueHs === 'number' && Number.isFinite(valueHs) ? valueHs : 0;

  const toFixed = (v) => (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2));

  const unit = hashrateUnitMode;
  if (unit === 'H/s') return { value: toFixed(hs), unit: 'H/s' };
  if (unit === 'kH/s') return { value: toFixed(hs / 1e3), unit: 'kH/s' };
  if (unit === 'MH/s') return { value: toFixed(hs / 1e6), unit: 'MH/s' };
  if (unit === 'GH/s') return { value: toFixed(hs / 1e9), unit: 'GH/s' };

  // auto
  if (hs >= 1e9) return { value: toFixed(hs / 1e9), unit: 'GH/s' };
  if (hs >= 1e6) return { value: toFixed(hs / 1e6), unit: 'MH/s' };
  if (hs >= 1e3) return { value: toFixed(hs / 1e3), unit: 'kH/s' };
  return { value: toFixed(hs), unit: 'H/s' };
}

function updateSettingsUI() {
  document.getElementById('wallet-input').value = config.wallet || '';
  document.getElementById('pool-input').value = `${config.pool?.host || 'pool.zionterranova.com'}:${config.pool?.port || 3333}`;
  const rpcUrlEl = document.getElementById('rpc-url');
  if (rpcUrlEl) rpcUrlEl.value = config.rpcUrl || 'http://localhost:18081/json_rpc';
  document.getElementById('worker-input').value = config.worker || 'desktop-agent';
  const threadsInput = document.getElementById('threads-input');
  if (threadsInput) {
    threadsInput.max = String(cpuThreadMax);
    threadsInput.value = String(Math.min(cpuThreadMax, Math.max(1, config.threads || 4)));
  }

  const threadsValueEl = document.getElementById('threads-value');
  if (threadsValueEl) threadsValueEl.textContent = String(Math.min(cpuThreadMax, Math.max(1, config.threads || 4)));

  const threadsMaxEl = document.getElementById('threads-max');
  if (threadsMaxEl) threadsMaxEl.textContent = String(cpuThreadMax);

  document.getElementById('gpu-checkbox').checked = config.gpu || false;
  document.getElementById('autostart-checkbox').checked = config.autoStart || false;

  // Dashboard quick controls
  const algoSelect = document.getElementById('algo-select');
  if (algoSelect) algoSelect.value = (config.algorithm || 'cosmic_harmony');
}

function setupAiControls() {
  const afterburnerCheckbox = document.getElementById('afterburner-checkbox');
  const afterburnerStatus = document.getElementById('afterburner-status');
  if (afterburnerCheckbox) {
    afterburnerCheckbox.checked = config.aiAfterburner !== false;
    afterburnerCheckbox.addEventListener('change', async () => {
      config.aiAfterburner = afterburnerCheckbox.checked;
      await window.electronAPI.saveConfig(config);
      if (afterburnerStatus) {
        afterburnerStatus.textContent = config.aiAfterburner
          ? 'Enabled (takes effect on next miner start)'
          : 'Disabled (takes effect on next miner start)';
      }
    });
    if (afterburnerStatus) {
      afterburnerStatus.textContent = afterburnerCheckbox.checked
        ? 'Enabled'
        : 'Disabled';
    }
  }
}

function setupChatControls() {
  const endpointEl = document.getElementById('chat-endpoint');
  const modelEl = document.getElementById('chat-model');
  const apiKeyEl = document.getElementById('chat-api-key');
  const inputEl = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send-btn');
  const messagesEl = document.getElementById('chat-messages');
  const statusEl = document.getElementById('chat-status');

  if (endpointEl) endpointEl.value = config.chatEndpoint || 'https://openrouter.ai/api/v1/chat/completions';
  if (modelEl) modelEl.value = config.chatModel || 'allenai/olmo-3.1-32b-think:free';
  if (apiKeyEl) apiKeyEl.value = config.chatApiKey || '';

  const state = {
    messages: []
  };

  const render = () => {
    if (!messagesEl) return;
    if (state.messages.length === 0) {
      messagesEl.innerHTML = '<div style="color: rgba(255,255,255,0.55); font-size: 12px;">No messages yet.</div>';
      return;
    }
    messagesEl.innerHTML = state.messages.map(m => {
      const isUser = m.role === 'user';
      const bg = isUser ? 'rgba(147,51,234,0.18)' : 'rgba(0,0,0,0.35)';
      const border = isUser ? '1px solid rgba(147,51,234,0.35)' : '1px solid rgba(255,255,255,0.10)';
      const align = isUser ? 'flex-end' : 'flex-start';
      return `
        <div style="display:flex; justify-content:${align}; margin: 10px 0;">
          <div style="max-width: 85%; padding: 10px 12px; border-radius: 12px; background:${bg}; border:${border}; white-space: pre-wrap;">${escapeHtml(m.content || '')}</div>
        </div>
      `;
    }).join('');
    messagesEl.scrollTop = messagesEl.scrollHeight;
  };

  const send = async () => {
    const text = (inputEl && 'value' in inputEl ? inputEl.value : '').toString().trim();
    if (!text) return;

    const endpoint = (endpointEl && 'value' in endpointEl ? endpointEl.value : '').toString().trim();
    const model = (modelEl && 'value' in modelEl ? modelEl.value : '').toString().trim();
    const apiKey = (apiKeyEl && 'value' in apiKeyEl ? apiKeyEl.value : '').toString();
    config.chatEndpoint = endpoint || config.chatEndpoint;
    config.chatModel = model || config.chatModel;
    config.chatApiKey = apiKey || config.chatApiKey;
    await window.electronAPI.saveConfig(config);

    // Simple chat commands (local actions) so the agent can operate afterburner.
    // Examples:
    //  - /ab stats
    //  - /ab task neural_network 2.5 sacred
    //  - /ab start | /ab stop
    if (/^\/(ab|afterburner)\b/i.test(text)) {
      const parts = text.split(/\s+/).filter(Boolean);
      const sub = (parts[1] || '').toLowerCase();
      try {
        if (statusEl) statusEl.textContent = 'Running afterburner command...';
        const payload = { cmd: sub || 'help', args: parts.slice(2) };
        const result = await window.electronAPI.afterburnerCommand(payload);
        if (!result?.success) {
          state.messages.push({ role: 'assistant', content: `Afterburner error: ${result?.error || 'failed'}` });
        } else {
          state.messages.push({ role: 'assistant', content: result?.text || 'OK' });
        }
        if (statusEl) statusEl.textContent = 'OK';
        render();
        return;
      } catch (e) {
        if (statusEl) statusEl.textContent = `Error: ${e?.message || String(e)}`;
        return;
      }
    }

    state.messages.push({ role: 'user', content: text });
    if (inputEl) inputEl.value = '';
    render();

    if (statusEl) statusEl.textContent = 'Thinking...';
    const result = await window.electronAPI.aiChat({
      endpoint: config.chatEndpoint,
      model: config.chatModel,
      apiKey: config.chatApiKey,
      messages: state.messages
    });

    if (!result?.success) {
      if (statusEl) statusEl.textContent = `Error: ${result?.error || 'chat failed'}`;
      return;
    }
    state.messages.push(result.message);
    if (statusEl) statusEl.textContent = 'OK';
    render();
  };

  sendBtn?.addEventListener('click', send);
  inputEl?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Event listeners
function setupEventListeners() {
  window.electronAPI.onMinerStarted(() => {
    isRunning = true;
    updateControlButtons();
    updateStatusBadge('mining');
    addLogEntry('Mining started successfully', 'info');
  });
  
  window.electronAPI.onMinerStopped((data) => {
    isRunning = false;
    updateControlButtons();
    updateStatusBadge('stopped');
    addLogEntry(`Mining stopped (exit code: ${data.code})`, 'warning');
    
    // Reset stats
    updateStats({
      hashrate: 0,
      shares: 0,
      accepted: 0,
      rejected: 0,
      uptime: 0,
      consciousness_level: 'PHYSICAL',
      consciousness_xp: 0
    });
  });

  window.electronAPI.onMinerError((data) => {
    const msg = data?.message || 'Miner error';
    addLogEntry(`Miner error: ${msg}`, 'error');
  });

  window.electronAPI.onMinerOutput((data) => {
    const text = (data?.text || '').toString();
    const stream = data?.stream === 'stderr' ? 'stderr' : 'stdout';

    // Split into lines, strip control chars, keep it readable
    const lines = text
      .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '')
      .split(/\r?\n/)
      .map(l => l.trim())
      .filter(Boolean);

    for (const line of lines.slice(0, 10)) {
      addLogEntry(`[${stream}] ${line}`, 'info');
    }
  });

  window.electronAPI.onBlockFound((data) => {
    const height = data?.height;
    const msg = height != null
      ? `🎉 GRATULUJI! Našel jsi blok #${height}! 🎉`
      : '🎉 GRATULUJI! Našel jsi blok! 🎉';
    addLogEntry(msg, 'success');

    // Zobrazit hezky v AI Boost panelu
    const msgEl = document.getElementById('ab-blockfound-msg');
    const heightEl = document.getElementById('ab-blockfound-height');
    const timeEl = document.getElementById('ab-blockfound-time');
    
    if (msgEl) {
      msgEl.innerHTML = '<strong style="color: #10b981; font-size: 18px;">🎉 GRATULUJI! Našel jsi blok! 🎉</strong>';
      msgEl.style.animation = 'pulse 1s ease-in-out 3';
    }
    
    if (heightEl) {
      heightEl.innerHTML = height != null 
        ? `<strong>📊 Výška bloku: #${height}</strong>` 
        : '<strong>📊 Blok úspěšně přidán do sítě!</strong>';
    }
    
    if (timeEl) {
      timeEl.textContent = new Date().toLocaleString('cs-CZ');
    }
  });
  
  window.electronAPI.onStatsUpdate((stats) => {
    updateStats(stats);
  });
}

function updateControlButtons() {
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');
  
  startBtn.disabled = isRunning;
  stopBtn.disabled = !isRunning;
}

function updateStatusBadge(status) {
  const badge = document.getElementById('status-badge');
  
  if (status === 'mining') {
    badge.className = 'status-badge mining';
    badge.textContent = 'MINING';
  } else {
    badge.className = 'status-badge stopped';
    badge.textContent = 'STOPPED';
  }
}

// Stats update
function updateStats(stats) {
  // Hashrate
  const formatted = formatHashrate(stats.hashrate);
  document.getElementById('hashrate-value').textContent = formatted.value;
  const unitEl = document.getElementById('hashrate-unit');
  if (unitEl) unitEl.textContent = hashrateUnitMode === 'auto' ? formatted.unit : hashrateUnitMode;
  
  // Shares
  document.getElementById('shares-value').textContent = `${stats.accepted} / ${stats.shares}`;
  
  // Uptime
  const hours = Math.floor(stats.uptime / 3600);
  const minutes = Math.floor((stats.uptime % 3600) / 60);
  const seconds = stats.uptime % 60;
  document.getElementById('uptime-value').textContent = 
    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  
  // Consciousness level - DISABLED FOR TESTNET v2.9
  // TODO: Re-enable when consciousness system is ready
  /*
  document.getElementById('consciousness-value').textContent = stats.consciousness_level;
  
  // Consciousness XP and progress
  const levelThresholds = {
    'PHYSICAL': 1000,
    'MENTAL': 3000,
    'COSMIC': 10000,
    'ON_THE_STAR': 100000
  };
  
  const currentThreshold = levelThresholds[stats.consciousness_level] || 1000;
  const progress = Math.min((stats.consciousness_xp / currentThreshold) * 100, 100);
  
  document.getElementById('consciousness-xp').textContent = `XP: ${stats.consciousness_xp} / ${currentThreshold}`;
  
  const progressBar = document.getElementById('consciousness-progress');
  progressBar.style.width = `${progress}%`;
  progressBar.textContent = `${progress.toFixed(1)}%`;
  */
  
  // Log significant events (once per milestone)
  // NOTE: UI can load with stale stats from previous runs; don't emit milestones on first read.
  if (!milestoneInitialized) {
    lastAcceptedForMilestone = Number.isFinite(stats.accepted) ? stats.accepted : 0;
    lastMilestoneBucket = Math.floor(lastAcceptedForMilestone / 10);
    milestoneInitialized = true;
  } else {
    const acceptedNow = Number.isFinite(stats.accepted) ? stats.accepted : 0;

    // New session / reset (accepted counters dropped)
    if (acceptedNow < lastAcceptedForMilestone) {
      lastAcceptedForMilestone = acceptedNow;
      lastMilestoneBucket = Math.floor(acceptedNow / 10);
    } else if (acceptedNow > lastAcceptedForMilestone) {
      const milestoneBucket = Math.floor(acceptedNow / 10);
      if (milestoneBucket > lastMilestoneBucket) {
        lastMilestoneBucket = milestoneBucket;
        const milestoneShares = milestoneBucket * 10;
        if (milestoneShares > 0) {
          addLogEntry(`Milestone: ${milestoneShares} shares accepted!`, 'info');
        }
      }
      lastAcceptedForMilestone = acceptedNow;
    }
  }

  // AI Afterburner metrics - zjednodušené zobrazení
  const abStatusEl = document.getElementById('ab-status');
  const abTempEl = document.getElementById('ab-temp');
  const abTpsEl = document.getElementById('ab-tps');
  const abEffEl = document.getElementById('ab-eff');
  const abActiveEl = document.getElementById('ab-active');
  const abCfEl = document.getElementById('ab-cf');
  const abDetailsEl = document.getElementById('ab-details');
  const abBlockFoundMsgEl = document.getElementById('ab-blockfound-msg');
  const abBlockFoundTimeEl = document.getElementById('ab-blockfound-time');
  const abBlockFoundHeightEl = document.getElementById('ab-blockfound-height');

  // 📊 Stav
  if (abStatusEl) {
    const v = stats.afterburner_status || 'idle';
    if (v === 'running') {
      abStatusEl.innerHTML = '✅ <strong style="color: #10b981;">Běží</strong>';
    } else if (v === 'idle') {
      abStatusEl.innerHTML = '🟡 <strong style="color: #f59e0b;">Připraven</strong>';
    } else {
      abStatusEl.textContent = v;
    }
  }

  // 🌡️ Teplota
  if (abTempEl) {
    const v = stats.afterburner_temp_c;
    if (v != null && v !== '') {
      const t = Number(v);
      if (t > 75) {
        abTempEl.innerHTML = `<strong style="color: #ef4444;">${t}°C</strong> 🔥`;
      } else if (t > 60) {
        abTempEl.innerHTML = `<strong style="color: #f59e0b;">${t}°C</strong>`;
      } else {
        abTempEl.innerHTML = `<strong style="color: #10b981;">${t}°C</strong>`;
      }
    } else {
      abTempEl.textContent = '—';
    }
  }

  // ⚡ Rychlost
  if (abTpsEl) {
    const v = stats.afterburner_speed_10s;
    if (v != null && v !== '') {
      const speed = Number(v);
      if (speed > 0) {
        abTpsEl.innerHTML = `<strong style="color: #10b981;">${speed.toFixed(1)}</strong> <span style="font-size: 14px; opacity: 0.7;">ops/s</span>`;
      } else {
        abTpsEl.textContent = '0 ops/s';
      }
    } else {
      abTpsEl.textContent = '—';
    }
  }

  // ✓ Úspěšnost
  if (abEffEl) {
    const v = stats.afterburner_success_60s_pct;
    if (v != null && v !== '') {
      const pct = Number(v);
      if (pct >= 95) {
        abEffEl.innerHTML = `<strong style="color: #10b981;">${pct.toFixed(0)}%</strong> 🎯`;
      } else if (pct >= 80) {
        abEffEl.innerHTML = `<strong style="color: #f59e0b;">${pct.toFixed(0)}%</strong>`;
      } else {
        abEffEl.innerHTML = `<strong style="color: #ef4444;">${pct.toFixed(0)}%</strong>`;
      }
    } else {
      abEffEl.textContent = '—';
    }
  }

  // 🔄 Aktivních úloh
  if (abActiveEl) {
    const v = stats.afterburner_active_tasks;
    if (v != null && v !== '') {
      const n = Number(v);
      if (n > 0) {
        abActiveEl.innerHTML = `<strong style="color: #10b981;">${n}</strong> ⚙️`;
      } else {
        abActiveEl.textContent = '0';
      }
    } else {
      abActiveEl.textContent = '0';
    }
  }

  // 💯 Hotovo / Chyb
  if (abCfEl) {
    const c = stats.afterburner_completed_tasks;
    const f = stats.afterburner_failed_tasks;
    const okNum = Number(c || 0);
    const badNum = Number(f || 0);
    if (okNum === 0 && badNum === 0) {
      abCfEl.textContent = '—';
    } else {
      abCfEl.innerHTML = `<strong style="color: #10b981;">${okNum}</strong> / <strong style="color: ${badNum > 0 ? '#ef4444' : 'rgba(255,255,255,0.6)}'}">${badNum}</strong>`;
    }
  }

  if (abDetailsEl) {
    const fmtDuration = (sec) => {
      const n = Number(sec);
      if (!Number.isFinite(n) || n < 0) return '—';
      const s = Math.floor(n);
      const hh = String(Math.floor(s / 3600)).padStart(2, '0');
      const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
      const ss = String(s % 60).padStart(2, '0');
      return `${hh}:${mm}:${ss}`;
    };

    const uptime = stats.afterburner_uptime_sec;
    const lastTaskType = stats.afterburner_last_task_type;
    const lastTaskMs = stats.afterburner_last_task_ms;
    const throttle = stats.afterburner_throttle_events;
    const qDepth = stats.afterburner_queue_depth;
    const qByType = stats.afterburner_queue_by_type;
    const lastErrRaw = (stats.afterburner_last_error || '').toString().trim();
    const lastErr = lastErrRaw.length > 140 ? `${lastErrRaw.slice(0, 140)}…` : lastErrRaw;

    const s10 = stats.afterburner_speed_10s;
    const s60 = stats.afterburner_speed_60s;
    const s15 = stats.afterburner_speed_15m;
    const succ60 = stats.afterburner_success_60s_pct;
    const lat10 = stats.afterburner_latency_10s_ms;
    const lat60 = stats.afterburner_latency_60s_ms;
    const ok = stats.afterburner_completed_tasks;
    const bad = stats.afterburner_failed_tasks;

    const okN = (ok == null || ok === '' ? null : Number(ok));
    const badN = (bad == null || bad === '' ? null : Number(bad));
    const totN = (okN != null && badN != null) ? (okN + badN) : null;
    const lifePct = (totN != null && totN > 0) ? (100.0 * okN / totN) : null;

    let queueText = '—';
    if (qByType && typeof qByType === 'object') {
      const entries = Object.entries(qByType)
        .filter(([, v]) => typeof v === 'number' && Number.isFinite(v) && v > 0)
        .sort((a, b) => Number(b[1]) - Number(a[1]))
        .slice(0, 4)
        .map(([k, v]) => `${k}:${v}`);
      if (entries.length) queueText = entries.join('  ');
    }

    const lines = [];

    // Zjednodušený přehled
    lines.push(`⏱️ Běží: ${uptime == null || uptime === '' ? '—' : fmtDuration(uptime)}`);
    
    const speedLine = [];
    if (s10 != null && s10 !== '') speedLine.push(`10s: ${Number(s10).toFixed(1)}`);
    if (s60 != null && s60 !== '') speedLine.push(`60s: ${Number(s60).toFixed(1)}`);
    if (s15 != null && s15 !== '') speedLine.push(`15m: ${Number(s15).toFixed(1)}`);
    if (speedLine.length) lines.push(`⚡ Rychlost: ${speedLine.join(' | ')} ops/s`);
    
    if (ok != null || bad != null) {
      const okNum = Number(ok || 0);
      const badNum = Number(bad || 0);
      const total = okNum + badNum;
      const successPct = total > 0 ? ((okNum / total) * 100).toFixed(1) : '0';
      lines.push(`✓ Hotovo: ${okNum} | ❌ Chyby: ${badNum} | Úspěšnost: ${successPct}%`);
    }
    
    if (lat10 != null && lat10 !== '') {
      lines.push(`⏱️ Odezva: ${Number(lat10).toFixed(0)}ms (10s avg)`);
    }
    
    if (qDepth != null && qDepth !== '') {
      lines.push(`📄 Fronta: ${qDepth} úloh`);
    }
    
    if (lastErr) lines.push(`⚠️ Poslední chyba: ${lastErr}`);

    abDetailsEl.textContent = lines.length ? lines.join('\n') : 'Čekám na data...';
  }
}

// Stats polling
async function pollStats() {
  const stats = await window.electronAPI.getStats();
  
  isRunning = stats.isRunning;
  updateControlButtons();
  updateStatusBadge(stats.isRunning ? 'mining' : 'stopped');
  updateStats(stats);
  
  // Poll every 5 seconds
  setTimeout(pollStats, 5000);
}

// Log viewer
let _logQueue = [];
let _logFlushScheduled = false;

function addLogEntry(message, type = 'info') {
  const logViewer = document.getElementById('log-viewer');
  if (!logViewer) return;

  const timestamp = new Date().toLocaleTimeString();
  _logQueue.push({ timestamp, message, type });

  if (_logFlushScheduled) return;
  _logFlushScheduled = true;

  requestAnimationFrame(() => {
    _logFlushScheduled = false;
    const viewer = document.getElementById('log-viewer');
    if (!viewer) {
      _logQueue = [];
      return;
    }

    // Only auto-scroll if the user is already at the bottom.
    const atBottom = (viewer.scrollTop + viewer.clientHeight) >= (viewer.scrollHeight - 12);

    const frag = document.createDocumentFragment();
    for (const item of _logQueue) {
      const entry = document.createElement('div');
      entry.className = `log-entry ${item.type}`;
      entry.textContent = `[${item.timestamp}] ${item.message}`;
      frag.appendChild(entry);
    }
    _logQueue = [];

    viewer.appendChild(frag);

    // Keep only last 100 entries
    while (viewer.children.length > 100) {
      viewer.removeChild(viewer.firstChild);
    }

    if (atBottom) viewer.scrollTop = viewer.scrollHeight;
  });
}

// Wallet management
let generatedWallet = null;

function setupWalletControls() {
  const generateBtn = document.getElementById('generate-wallet-btn');
  const saveBtn = document.getElementById('save-wallet-btn');
  const cancelBtn = document.getElementById('cancel-wallet-btn');
  const copyAddressBtn = document.getElementById('copy-address-btn');
  const refreshWalletsBtn = document.getElementById('refresh-wallets-btn');
  const importBtn = document.getElementById('import-wallet-btn');

  // Wallet actions UI
  const activeWalletInput = document.getElementById('active-wallet-address');
  const setActiveWalletBtn = document.getElementById('set-active-wallet-btn');
  const refreshBalanceBtn = document.getElementById('refresh-balance-btn');
  const walletBalanceEl = document.getElementById('wallet-balance');
  const walletBalanceStatusEl = document.getElementById('wallet-balance-status');
  const generateQrBtn = document.getElementById('generate-qr-btn');
  const receiveQrImg = document.getElementById('receive-qr-img');
  const receiveQrPlaceholder = document.getElementById('receive-qr-placeholder');
  const receiveQrStatusEl = document.getElementById('receive-qr-status');
  const sendToEl = document.getElementById('send-to-address');
  const sendAmountEl = document.getElementById('send-amount');
  const sendPurposeEl = document.getElementById('send-purpose');
  const sendTxBtn = document.getElementById('send-tx-btn');
  const sendStatusEl = document.getElementById('send-status');

  const getRpcUrl = () => (config?.rpcUrl || 'http://localhost:18081/json_rpc');
  const getActiveAddress = () => {
    const v = activeWalletInput && 'value' in activeWalletInput ? activeWalletInput.value : '';
    return (v || config.wallet || '').toString().trim();
  };

  const syncActiveWallet = () => {
    if (activeWalletInput && 'value' in activeWalletInput) {
      activeWalletInput.value = (config.wallet || '').toString();
    }
  };

  // Generate wallet
  generateBtn?.addEventListener('click', async () => {
    const name = document.getElementById('new-wallet-name').value;
    const password = document.getElementById('new-wallet-password').value;
    const passwordConfirm = document.getElementById('new-wallet-password-confirm').value;

    if (!name) {
      alert('Please enter a wallet name');
      return;
    }

    if (!password || password.length < 8) {
      alert('Password must be at least 8 characters');
      return;
    }

    if (password !== passwordConfirm) {
      alert('Passwords do not match');
      return;
    }

    // Generate wallet
    const result = await window.electronAPI.generateWallet();
    
    if (result.success) {
      generatedWallet = result.wallet;
      
      // Show wallet display
      document.getElementById('wallet-generator').style.display = 'none';
      document.getElementById('wallet-display').style.display = 'block';
      
      // Fill in generated data
      document.getElementById('generated-address').value = generatedWallet.address;
      document.getElementById('generated-mnemonic').value = generatedWallet.mnemonic;
      
      addLogEntry(`New wallet generated: ${generatedWallet.address}`, 'info');
    } else {
      alert(`Wallet generation failed: ${result.error}`);
    }
  });

  // Copy address to clipboard
  copyAddressBtn?.addEventListener('click', () => {
    const address = document.getElementById('generated-address').value;
    navigator.clipboard.writeText(address);
    
      const copyAddressOriginalHtml = copyAddressBtn?.innerHTML;
      if (copyAddressBtn) {
        copyAddressBtn.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#i-check"></use></svg><span>Copied!</span>';
      }
    setTimeout(() => {
        if (copyAddressBtn) {
          copyAddressBtn.innerHTML = copyAddressOriginalHtml || '<span>Copy</span>';
        }
    }, 2000);
  });

  // Save wallet
  saveBtn?.addEventListener('click', async () => {
    const name = document.getElementById('new-wallet-name').value;
    const password = document.getElementById('new-wallet-password').value;

    const result = await window.electronAPI.saveWallet({
      wallet: generatedWallet,
      password,
      name
    });

    if (result.success) {
      alert('Wallet saved successfully!\n\nMake sure you have written down your recovery phrase!');
      
      // Reset form
      document.getElementById('wallet-generator').style.display = 'block';
      document.getElementById('wallet-display').style.display = 'none';
      document.getElementById('new-wallet-name').value = 'My Wallet';
      document.getElementById('new-wallet-password').value = '';
      document.getElementById('new-wallet-password-confirm').value = '';
      generatedWallet = null;
      
      // Reload wallets list
      loadWalletsList();
      addLogEntry('Wallet saved successfully', 'info');
    } else {
      alert(`Failed to save wallet: ${result.error}`);
    }
  });

  // Cancel wallet creation
  cancelBtn?.addEventListener('click', () => {
    if (confirm('Are you sure? The wallet will not be saved!')) {
      document.getElementById('wallet-generator').style.display = 'block';
      document.getElementById('wallet-display').style.display = 'none';
      generatedWallet = null;
    }
  });

  // Refresh wallets
  refreshWalletsBtn?.addEventListener('click', () => {
    loadWalletsList();
  });

  // Import wallet
  importBtn?.addEventListener('click', async () => {
    const mnemonic = document.getElementById('import-mnemonic').value.trim();
    const name = document.getElementById('import-wallet-name').value;
    const password = document.getElementById('import-wallet-password').value;

    if (!mnemonic || !name || !password) {
      alert('Please fill in all fields');
      return;
    }

    const result = await window.electronAPI.importWallet({ mnemonic, name, password });
    
    if (result.success) {
      alert('Wallet imported successfully!');
      document.getElementById('import-mnemonic').value = '';
      document.getElementById('import-wallet-name').value = '';
      document.getElementById('import-wallet-password').value = '';
      loadWalletsList();
    } else {
      alert(`Import failed: ${result.error}`);
    }
  });

  // Load wallets on wallet view switch
  loadWalletsList();

  // Seed wallet actions with current config
  syncActiveWallet();

  setActiveWalletBtn?.addEventListener('click', async () => {
    const address = getActiveAddress();
    if (!address) {
      alert('Enter a zion1... address');
      return;
    }

    const check = await window.electronAPI.validateAddress(address);
    if (check?.type === 'legacy') {
      alert('This is a legacy ZION... address. The chain only credits zion1... addresses.\n\nCreate/select a zion1... wallet and use that.');
      return;
    }
    if (!check?.valid) {
      alert('Invalid address. Expected zion1...');
      return;
    }

    config.wallet = address;
    await window.electronAPI.saveConfig(config);
    updateSettingsUI();
    addLogEntry(`Active wallet set: ${address}`, 'info');
    alert(`Active wallet set:\n\n${address}`);
  });

  refreshBalanceBtn?.addEventListener('click', async () => {
    const address = getActiveAddress();
    if (walletBalanceStatusEl) walletBalanceStatusEl.textContent = 'Loading...';

    const check = await window.electronAPI.validateAddress(address);
    if (!check?.valid) {
      if (walletBalanceStatusEl) walletBalanceStatusEl.textContent = 'Set a valid zion1... address first.';
      return;
    }

    const result = await window.electronAPI.walletGetBalance({
      rpcUrl: getRpcUrl(),
      address
    });

    if (!result?.success) {
      if (walletBalanceStatusEl) walletBalanceStatusEl.textContent = `Error: ${result?.error || 'balance fetch failed'}`;
      return;
    }

    if (walletBalanceEl) walletBalanceEl.textContent = String(result.balance ?? 0);
    if (walletBalanceStatusEl) walletBalanceStatusEl.textContent = `OK · ${new Date().toLocaleTimeString()}`;
  });

  generateQrBtn?.addEventListener('click', async () => {
    const address = getActiveAddress();
    if (receiveQrStatusEl) receiveQrStatusEl.textContent = 'Generating...';

    const check = await window.electronAPI.validateAddress(address);
    if (!check?.valid) {
      if (receiveQrStatusEl) receiveQrStatusEl.textContent = 'Set a valid zion1... address first.';
      return;
    }

    const result = await window.electronAPI.walletGenerateQr({ text: address });
    if (!result?.success) {
      if (receiveQrStatusEl) receiveQrStatusEl.textContent = `Error: ${result?.error || 'QR failed'}`;
      return;
    }

    if (receiveQrImg) {
      receiveQrImg.src = result.dataUrl;
      receiveQrImg.style.display = 'block';
    }
    if (receiveQrPlaceholder) receiveQrPlaceholder.style.display = 'none';
    if (receiveQrStatusEl) receiveQrStatusEl.textContent = 'OK';
  });

  sendTxBtn?.addEventListener('click', async () => {
    const from = getActiveAddress();
    const to = (sendToEl && 'value' in sendToEl ? sendToEl.value : '').toString().trim();
    const amount = (sendAmountEl && 'value' in sendAmountEl ? sendAmountEl.value : '').toString().trim();
    const purpose = (sendPurposeEl && 'value' in sendPurposeEl ? sendPurposeEl.value : '').toString();

    if (sendStatusEl) sendStatusEl.textContent = 'Sending...';

    const fromCheck = await window.electronAPI.validateAddress(from);
    const toCheck = await window.electronAPI.validateAddress(to);
    if (!fromCheck?.valid || !toCheck?.valid) {
      if (sendStatusEl) sendStatusEl.textContent = 'Both from/to must be valid zion1... addresses.';
      return;
    }

    const result = await window.electronAPI.walletSendTransaction({
      rpcUrl: getRpcUrl(),
      from,
      to,
      amount,
      purpose
    });

    if (!result?.success) {
      if (sendStatusEl) sendStatusEl.textContent = `Error: ${result?.error || 'send failed'}`;
      return;
    }

    if (sendStatusEl) sendStatusEl.textContent = `OK · ${result.status || 'pending'} · tx: ${result.txId || 'n/a'}`;
    if (sendToEl) sendToEl.value = '';
    if (sendAmountEl) sendAmountEl.value = '';
    if (sendPurposeEl) sendPurposeEl.value = '';
  });
}

async function loadWalletsList() {
  const result = await window.electronAPI.listWallets();
  const container = document.getElementById('wallets-list');

  const wallets = Array.isArray(result?.wallets) ? result.wallets : [];
  if (!result?.success || wallets.length === 0) {
    if (result?.success === false && result?.error) {
      addLogEntry(`Wallet list error: ${result.error}`, 'error');
    }
    container.innerHTML = '<p style="color: rgba(255,255,255,0.5); text-align: center; padding: 40px;">No wallets yet. Create one above!</p>';
    return;
  }

  // Build wallets list HTML
  const html = wallets.map(wallet => `
    <div style="padding: 20px; background: rgba(0,0,0,0.5); border: 1px solid rgba(147,51,234,0.2); border-radius: 12px; margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
        <div>
          <h3 style="color: var(--zion-gold); margin-bottom: 8px; font-size: 18px;">${wallet.name}</h3>
          <p style="color: rgba(255,255,255,0.7); font-family: monospace; font-size: 13px; word-break: break-all;">${wallet.address}</p>
        </div>
      </div>
      <div style="display: flex; gap: 8px; font-size: 12px; color: rgba(255,255,255,0.5);">
        <span>Created: ${new Date(wallet.createdAt).toLocaleDateString()}</span>
        <span>•</span>
        <span>Last used: ${wallet.lastUsed ? new Date(wallet.lastUsed).toLocaleDateString() : 'Never'}</span>
      </div>
      <div style="margin-top: 16px; display: flex; gap: 8px;">
        <button class="btn btn-primary" onclick="useWallet('${wallet.address}')" style="width: auto; padding: 10px 16px; font-size: 13px;">
           <svg class="icon" aria-hidden="true"><use href="#i-check"></use></svg>
           <span>Use for Mining</span>
        </button>
        <button class="btn" onclick="copyWalletAddress('${wallet.address}')" style="width: auto; padding: 10px 16px; font-size: 13px; background: rgba(147,51,234,0.2); border: 1px solid var(--zion-purple);">
           <svg class="icon" aria-hidden="true"><use href="#i-copy"></use></svg>
           <span>Copy Address</span>
        </button>
      </div>
    </div>
  `).join('');

  container.innerHTML = html;
}

// Global functions for wallet actions
window.useWallet = async (address) => {
  const check = await window.electronAPI.validateAddress(address);
  if (check?.type === 'legacy') {
    alert('This is a legacy ZION... address. The chain only credits zion1... addresses.\n\nCreate/select a zion1... wallet and use that.');
    return;
  }
  if (!check?.valid) {
    alert('Invalid address. Expected zion1...');
    return;
  }

  // Update config with wallet address
  const freshConfig = await window.electronAPI.getConfig();
  freshConfig.wallet = address;
  await window.electronAPI.saveConfig(freshConfig);

  // Keep renderer state in sync
  config.wallet = address;

  const activeWalletInput = document.getElementById('active-wallet-address');
  if (activeWalletInput && 'value' in activeWalletInput) {
    activeWalletInput.value = address;
  }

  alert(`Wallet set for mining!\n\nAddress: ${address}`);
  
  // Update settings UI if on that view
  updateSettingsUI();
};

window.copyWalletAddress = (address) => {
  navigator.clipboard.writeText(address);
  alert('Address copied to clipboard!');
};

console.log('Renderer script loaded');
