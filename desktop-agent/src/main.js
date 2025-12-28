// ZION Desktop Mining Agent v2.9 - Main Process
// Electron main process with system tray, auto-start, IPC

const { app, BrowserWindow, Tray, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const WalletGenerator = require('./wallet-generator');
const QRCode = require('qrcode');

// Keep cache clean on Windows without overriding userData paths.
// (We must NOT set userData to a different path; only set cache.)
app.disableHardwareAcceleration();

// Avoid multiple Electron instances fighting over the same cache directory.
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
}

function logApp(message, extra) {
  try {
    const USER_DATA_PATH = app.getPath('userData');
    const appLogPath = path.join(USER_DATA_PATH, 'desktop_agent.log');
    const line = `${new Date().toISOString()} ${message}${extra ? ` ${extra}` : ''}\n`;
    fs.appendFileSync(appLogPath, line);
  } catch {
    // ignore logging failures
  }
}

app.on('second-instance', () => {
  logApp('second-instance');
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    showWindow();
  } else {
    createWindow();
  }
});

const USER_DATA_PATH = app.getPath('userData');
const CACHE_PATH = path.join(USER_DATA_PATH, 'cache');

app.setPath('cache', CACHE_PATH);
app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');
app.commandLine.appendSwitch('disk-cache-dir', CACHE_PATH);
app.commandLine.appendSwitch('disable-http-cache');
app.commandLine.appendSwitch('disk-cache-size', '0');

let mainWindow;
let tray;
let trayMenu;
let minerProcess = null;
let minerStopping = false;
let minerStopPromise = null;
let afterburnerProc = null;
let afterburnerReady = false;
let afterburnerStdoutBuf = '';
let afterburnerQueue = [];
let afterburnerReqId = 1;
let minerStats = {
  hashrate: 0,
  shares: 0,
  accepted: 0,
  rejected: 0,
  uptime: 0,
  consciousness_level: 'PHYSICAL',
  consciousness_xp: 0
};

function resolveResourcePath(...parts) {
  // In dev: assets live under __dirname/assets
  // In packaged: assets may live inside app.asar OR be copied into Resources via electron-builder extraResources.
  const candidates = [
    path.join(__dirname, ...parts),
    path.join(process.resourcesPath, ...parts),
    path.join(process.resourcesPath, 'assets', ...parts),
    path.join(process.resourcesPath, 'app.asar', ...parts),
    path.join(process.resourcesPath, 'app.asar', 'src', ...parts)
  ];

  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) return p;
    } catch {
      // ignore
    }
  }

  // Fall back to the most common dev path.
  return path.join(__dirname, ...parts);
}

process.on('uncaughtException', (err) => {
  try {
    logApp('uncaughtException', err?.stack || err?.message || String(err));
  } catch {
    // ignore
  }
});

process.on('unhandledRejection', (reason) => {
  try {
    logApp('unhandledRejection', reason?.stack || reason?.message || String(reason));
  } catch {
    // ignore
  }
});

// App paths
const APP_ROOT = path.join(__dirname, '..');
const IS_PACKAGED = app.isPackaged;

// Miner path: platform-specific
// For packaged app: use resources folder
// For development: use the Python script in project root or resources
let MINER_PATH;
let MINER_IS_PYTHON = false;

if (process.platform === 'darwin') {
  // macOS: use Python script
  MINER_IS_PYTHON = true;
  MINER_PATH = IS_PACKAGED 
    ? path.join(process.resourcesPath, 'zion_native_miner_v2_9.py')
    : path.join(APP_ROOT, 'resources', 'zion_native_miner_v2_9.py');
} else if (process.platform === 'linux') {
  // Linux: use Python script (or native binary if available)
  MINER_IS_PYTHON = true;
  MINER_PATH = IS_PACKAGED 
    ? path.join(process.resourcesPath, 'zion_native_miner_v2_9.py')
    : path.join(APP_ROOT, 'resources', 'zion_native_miner_v2_9.py');
} else {
  // Windows: use .exe
  MINER_IS_PYTHON = false;
  MINER_PATH = IS_PACKAGED 
    ? path.join(process.resourcesPath, 'zion_native_miner_v2_9.exe')
    : path.join(APP_ROOT, 'resources', 'zion_native_miner_v2_9.exe');
}

const CONFIG_PATH = path.join(USER_DATA_PATH, 'miner_config.json');
const LOG_PATH = path.join(USER_DATA_PATH, 'miner.log');
const WALLETS_PATH = path.join(USER_DATA_PATH, 'wallets');
const STATS_PATH = path.join(USER_DATA_PATH, 'miner_stats.json');

// Afterburner service (Python JSON-lines RPC)
const AFTERBURNER_SCRIPT_PATH = IS_PACKAGED
  ? path.join(process.resourcesPath, 'afterburner_service.py')
  : path.join(APP_ROOT, 'resources', 'afterburner_service.py');

const MAX_MINER_LOG_BYTES = 50 * 1024 * 1024; // 50MB
const MAX_MINER_LOG_BACKUPS = 1;

function rotateFileIfLarge(filePath, maxBytes) {
  try {
    if (!fs.existsSync(filePath)) return;
    const st = fs.statSync(filePath);
    if (!st || typeof st.size !== 'number') return;
    if (st.size < maxBytes) return;

    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    const rotatedPath = `${filePath}.${ts}.bak`;
    fs.renameSync(filePath, rotatedPath);
  } catch (err) {
    // best-effort only
    console.warn('Log rotation failed:', err?.message || err);
  }
}

// Default configuration
const DEFAULT_CONFIG = {
  pool: {
    host: 'pool.zionterranova.com',
    port: 3333
  },
  // ZION chain JSON-RPC endpoint (Monero-like /json_rpc)
  rpcUrl: 'http://localhost:18081/json_rpc',
  // Mining algorithm (matches miner --algorithm)
  algorithm: 'cosmic_harmony',
  // AI Afterburner integration (controls env ZION_AI_AFTERBURNER)
  aiAfterburner: true,
  // Local chat (optional)
  // Cloud chat (OpenAI-compatible). Keep endpoint editable for future ZION AI Native.
  chatEndpoint: 'https://openrouter.ai/api/v1/chat/completions',
  // Free-tier via OpenRouter (model ids ending with :free)
  chatModel: 'allenai/olmo-3.1-32b-think:free',
  chatApiKey: '',
  wallet: '',
  worker: 'desktop-agent',
  threads: 4,
  gpu: false,
  autoStart: false,
  minimizeToTray: true,
  startMinimized: false
};

// Load or create config
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      return { ...DEFAULT_CONFIG, ...config };
    }
  } catch (err) {
    console.error('Failed to load config:', err);
  }
  return DEFAULT_CONFIG;
}

function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return true;
  } catch (err) {
    console.error('Failed to save config:', err);
    return false;
  }
}

// Ensure required directories exist
function ensureDirectories() {
  const dirs = [
    USER_DATA_PATH,
    CACHE_PATH,
    WALLETS_PATH
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log('Created directory:', dir);
    }
  });
}

function rotateFileIfTooLarge(filePath, maxBytes, maxBackups = 1) {
  try {
    if (!fs.existsSync(filePath)) return;
    const stat = fs.statSync(filePath);
    if (!stat.isFile()) return;
    if (stat.size <= maxBytes) return;

    for (let i = maxBackups; i >= 1; i -= 1) {
      const src = `${filePath}.${i}`;
      const dst = `${filePath}.${i + 1}`;
      if (fs.existsSync(src)) {
        try {
          if (i + 1 > maxBackups) {
            fs.unlinkSync(src);
          } else {
            if (fs.existsSync(dst)) fs.unlinkSync(dst);
            fs.renameSync(src, dst);
          }
        } catch {
          // ignore rotation failures
        }
      }
    }

    const backup = `${filePath}.1`;
    try {
      if (fs.existsSync(backup)) fs.unlinkSync(backup);
      fs.renameSync(filePath, backup);
    } catch {
      // If rename fails (e.g., file locked), best effort: truncate.
      try {
        fs.truncateSync(filePath, 0);
      } catch {
        // ignore
      }
    }
  } catch {
    // ignore
  }
}

function bytesToGiB(bytes) {
  const n = Number(bytes);
  if (!Number.isFinite(n) || n < 0) return 0;
  return n / (1024 ** 3);
}

function getMacVmStatAvailableBytes() {
  // Use vm_stat for a better approximation than os.freemem() on macOS.
  // We treat: free + speculative + inactive + purgeable as "available".
  // This is a heuristic to avoid RandomX FULL_MEM triggering heavy memory pressure.
  try {
    const out = execFileSync('vm_stat', { encoding: 'utf8' });
    const pageSizeMatch = out.match(/page size of\s+(\d+)\s+bytes/i);
    const pageSize = pageSizeMatch ? Number(pageSizeMatch[1]) : 4096;

    const getPages = (label) => {
      const re = new RegExp(`^\\s*${label}:\\s*(\\d+)\\.$`, 'mi');
      const m = out.match(re);
      return m ? Number(m[1]) : 0;
    };

    const pagesFree = getPages('Pages free');
    const pagesSpec = getPages('Pages speculative');
    const pagesInactive = getPages('Pages inactive');
    const pagesPurgeable = getPages('Pages purgeable');

    const pagesAvail = pagesFree + pagesSpec + pagesInactive + pagesPurgeable;
    const availBytes = Math.max(0, pagesAvail) * (Number.isFinite(pageSize) ? pageSize : 4096);
    return Number.isFinite(availBytes) ? availBytes : null;
  } catch {
    return null;
  }
}

function decideRandomxModeForMac(config) {
  const totalBytes = os.totalmem();
  const totalGiB = bytesToGiB(totalBytes);
  const threads = Number(config?.threads) || 1;

  const availBytes = getMacVmStatAvailableBytes();
  const availGiB = availBytes != null ? bytesToGiB(availBytes) : bytesToGiB(os.freemem());

  // RandomX FULL_MEM allocates ~2GiB dataset + overhead; macOS memory pressure can crater hashrate.
  // Keep it simple & safe for non-technical users:
  // - Prefer LIGHT mode on smaller machines, or when available memory is low.
  // - Prefer FULL_MEM when memory headroom seems comfortable.
  const forceLight = (totalGiB < 12) || (availGiB < 5) || (threads >= 8 && availGiB < 7);

  if (forceLight) {
    return {
      light: true,
      reason: `low memory headroom (available ~${availGiB.toFixed(1)} GiB of ${totalGiB.toFixed(1)} GiB)`
    };
  }

  return {
    light: false,
    reason: `memory OK (available ~${availGiB.toFixed(1)} GiB of ${totalGiB.toFixed(1)} GiB)`
  };
}

function migrateLegacyUserDataIfNeeded() {
  // Legacy bug created nested userData under: <userData>\cache\<appFolderName>\...
  const legacyRoot = path.join(USER_DATA_PATH, 'cache', path.basename(USER_DATA_PATH));
  const legacyConfig = path.join(legacyRoot, 'miner_config.json');
  const legacyLog = path.join(legacyRoot, 'miner.log');
  const legacyWallets = path.join(legacyRoot, 'wallets');

  try {
    if (!fs.existsSync(CONFIG_PATH) && fs.existsSync(legacyConfig)) {
      fs.copyFileSync(legacyConfig, CONFIG_PATH);
      console.log('Migrated legacy config to:', CONFIG_PATH);
    }

    if (!fs.existsSync(LOG_PATH) && fs.existsSync(legacyLog)) {
      fs.copyFileSync(legacyLog, LOG_PATH);
      console.log('Migrated legacy log to:', LOG_PATH);
    }

    if (!fs.existsSync(WALLETS_PATH) && fs.existsSync(legacyWallets)) {
      fs.mkdirSync(WALLETS_PATH, { recursive: true });
      for (const file of fs.readdirSync(legacyWallets)) {
        const from = path.join(legacyWallets, file);
        const to = path.join(WALLETS_PATH, file);
        if (!fs.existsSync(to)) {
          fs.copyFileSync(from, to);
        }
      }
      console.log('Migrated legacy wallets to:', WALLETS_PATH);
    }
  } catch (err) {
    console.warn('Legacy data migration failed:', err);
  }
}

// Create main window
function createWindow() {
  const config = loadConfig();

  // Window icon is meaningful on Windows/Linux; macOS uses the app bundle icon.
  const windowIconPath = resolveResourcePath('assets', 'icon.png');
  const windowIcon = (process.platform === 'win32' || process.platform === 'linux') ? windowIconPath : undefined;

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'ZION Miner v2.9',
    ...(windowIcon ? { icon: windowIcon } : {}),
    show: true, // Always show window on manual start; startMinimized only applies to auto-start
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load UI
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'ui', 'index.html'));
    // DevTools can be opened with F12 or Ctrl+Shift+I when needed
  }

  // Recover from renderer crashes / load failures instead of silently exiting.
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    logApp('did-fail-load', `${errorCode} ${errorDescription}`);
    console.error('LOAD FAILED:', errorCode, errorDescription);
    dialog.showErrorBox('Load Failed', `Failed to load UI: ${errorDescription}`);
  });

  mainWindow.webContents.on('crashed', (event, killed) => {
    logApp('crashed', `killed=${killed}`);
    console.error('RENDERER CRASHED!', { killed });
    dialog.showErrorBox('Renderer Crashed', 'The renderer process crashed. Check logs.');
  });

  mainWindow.webContents.on('render-process-gone', (event, details) => {
    logApp('render-process-gone', `${details?.reason || 'unknown'} ${details?.exitCode ?? ''}`);
    // Recreate the window after a short delay.
    setTimeout(() => {
      try {
        if (!mainWindow) createWindow();
        else mainWindow.reload();
      } catch (err) {
        logApp('renderer-recover-failed', err?.message || String(err));
      }
    }, 500);
  });

  // Window events
  mainWindow.on('close', (event) => {
    if (config.minimizeToTray && !app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Auto-start mining if configured
  if (config.autoStart && config.wallet) {
    setTimeout(() => startMining(config), 3000);
  }

  // Default ON: start Afterburner service on app launch (independent of miner).
  if (config.aiAfterburner !== false) {
    void ensureAfterburnerServiceRunning()
      .then(() => afterburnerSend({ cmd: 'start' }))
      .catch(() => {
        // best-effort; avoid noisy dialogs on launch
      });
  }
}

// Create system tray
function createTray() {
  // Use nativeImage for better compatibility
  const { nativeImage } = require('electron');
  
  // Prefer a dedicated tray icon; fall back to app icon.
  const trayIconCandidates = [
    resolveResourcePath('assets', 'tray-icon.png'),
    resolveResourcePath('tray-icon.png'),
    resolveResourcePath('assets', 'icon.png'),
    resolveResourcePath('icon.png')
  ];

  let trayIcon = nativeImage.createEmpty();
  for (const p of trayIconCandidates) {
    try {
      const img = nativeImage.createFromPath(p);
      if (img && !img.isEmpty()) {
        trayIcon = img;
        break;
      }
    } catch {
      // ignore
    }
  }

  // macOS menubar: template images render correctly on light/dark mode.
  if (process.platform === 'darwin' && trayIcon && !trayIcon.isEmpty()) {
    try {
      trayIcon.setTemplateImage(true);
    } catch {
      // ignore
    }
  }
  
  tray = new Tray(trayIcon);
  
  trayMenu = Menu.buildFromTemplate([
    {
      label: 'ZION Miner v2.9',
      enabled: false
    },
    { type: 'separator' },
    {
      label: 'Hashrate: 0 kH/s',
      id: 'hashrate',
      enabled: false
    },
    {
      label: 'Status: Stopped',
      id: 'status',
      enabled: false
    },
    { type: 'separator' },
    {
      label: 'Start Mining',
      id: 'start',
      click: () => {
        const config = loadConfig();
        if (config.wallet) {
          startMining(config);
        } else {
          showWindow();
          dialog.showMessageBox(mainWindow, {
            type: 'warning',
            title: 'Wallet Required',
            message: 'Please configure your ZION wallet address first.'
          });
        }
      }
    },
    {
      label: 'Stop Mining',
      id: 'stop',
      enabled: false,
      click: stopMining
    },
    { type: 'separator' },
    {
      label: 'Show Window',
      click: showWindow
    },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        stopMining();
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(trayMenu);
  tray.setToolTip('ZION Miner v2.9');
  
  tray.on('click', () => {
    showWindow();
  });
}

function showWindow() {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
  }
}

function updateTrayMenu(stats) {
  if (!tray || !trayMenu) return;
  const isRunning = minerProcess !== null;

  const hashrateHs = typeof stats.hashrate === 'number' ? stats.hashrate : 0;
  let trayValue = hashrateHs;
  let trayUnit = 'H/s';
  if (trayValue >= 1e9) {
    trayValue /= 1e9;
    trayUnit = 'GH/s';
  } else if (trayValue >= 1e6) {
    trayValue /= 1e6;
    trayUnit = 'MH/s';
  } else if (trayValue >= 1e3) {
    trayValue /= 1e3;
    trayUnit = 'kH/s';
  }
  trayMenu.getMenuItemById('hashrate').label = `Hashrate: ${trayValue.toFixed(2)} ${trayUnit}`;
  trayMenu.getMenuItemById('status').label = `Status: ${isRunning ? 'Mining' : 'Stopped'}`;
  trayMenu.getMenuItemById('start').enabled = !isRunning;
  trayMenu.getMenuItemById('stop').enabled = isRunning;

  tray.setContextMenu(trayMenu);
}

// Mining process management
function startMining(config) {
  if (minerProcess) {
    console.log('Miner already running');
    return { success: false, error: 'Miner is already running' };
  }

  if (!config.wallet || !config.wallet.toString().trim()) {
    dialog.showErrorBox('Wallet Missing', 'Set your ZION wallet address in Settings or Wallet tab before starting mining.');
    return { success: false, error: 'Wallet missing' };
  }

  // Enforce canonical chain-compatible addresses.
  const addr = config.wallet.toString().trim();
  const addrType = WalletGenerator.getAddressType(addr);
  if (addrType !== 'zion1') {
    const hint = addrType === 'legacy'
      ? 'You are using a legacy ZION... address. The chain only credits zion1... addresses.'
      : 'Invalid address format.';
    dialog.showErrorBox(
      'Invalid Wallet Address',
      `${hint}\n\nPlease create/select a zion1... wallet in the Wallet tab and use that for mining.`
    );
    return { success: false, error: 'Invalid wallet address' };
  }

  // Check if miner executable exists
  if (!fs.existsSync(MINER_PATH)) {
    dialog.showErrorBox('Miner Not Found', `Miner executable not found at: ${MINER_PATH}`);
    return { success: false, error: `Miner executable not found at: ${MINER_PATH}` };
  }

  const args = [
    '--pool', `${config.pool.host}:${config.pool.port}`,
    '--wallet', config.wallet,
    '--worker', config.worker,
    '--threads', config.threads.toString(),
    '--stats-interval', '5',
    '--stats-file', STATS_PATH
  ];

  if (config.algorithm) {
    args.push('--algorithm', String(config.algorithm));
  }

  args.push('--mode', config.gpu ? 'gpu' : 'cpu');

  console.log('Starting miner:', MINER_IS_PYTHON ? `python3 ${MINER_PATH}` : MINER_PATH, args.join(' '));

  // The miner loads native DLLs via relative paths like ai\\mining\\*.dll.
  // Ensure cwd points to a directory that contains the ai/ folder.
  const minerCwd = IS_PACKAGED ? process.resourcesPath : path.join(APP_ROOT, 'resources');

  // Spawn miner - use Python on macOS/Linux, executable on Windows
  let spawnCommand, spawnArgs;
  if (MINER_IS_PYTHON) {
    // macOS or Linux: use python3
    spawnCommand = 'python3';
    spawnArgs = [MINER_PATH, ...args];
  } else {
    // Windows: use .exe directly
    spawnCommand = MINER_PATH;
    spawnArgs = args;
  }

  const env = {
    ...process.env,
    ZION_AI_AFTERBURNER: config.aiAfterburner === false ? '0' : '1',
    // Prevent UnicodeEncodeError on Windows when PyInstaller app prints non-ASCII.
    PYTHONUTF8: '1',
    PYTHONIOENCODING: 'utf-8',
    // Make sure prints/logs aren't stuck in a buffer when stdout isn't a TTY.
    PYTHONUNBUFFERED: '1',
    // Add mining folder to PYTHONPATH so miner can find local modules
    PYTHONPATH: minerCwd + (process.env.PYTHONPATH ? path.delimiter + process.env.PYTHONPATH : '')
  };

  // "Na klik" RandomX: automatically choose FULL_MEM vs LIGHT on macOS.
  // We always set both env vars to override any inherited shell settings.
  const algo = String(config.algorithm || '').toLowerCase();
  let randomxAutoMessage = null;
  if (process.platform === 'darwin' && algo === 'randomx') {
    const decision = decideRandomxModeForMac(config);
    if (decision.light) {
      env.ZION_RANDOMX_LIGHT = '1';
      env.ZION_RANDOMX_FULL_MEM = '0';
      randomxAutoMessage = `RandomX auto: LIGHT mode (cache-only) selected — ${decision.reason}`;
    } else {
      env.ZION_RANDOMX_LIGHT = '0';
      env.ZION_RANDOMX_FULL_MEM = '1';
      randomxAutoMessage = `RandomX auto: FULL_MEM mode selected — ${decision.reason}`;
    }

    // Show users a friendly explanation in the UI log.
    try {
      sendToRenderer('miner-output', { stream: 'stdout', text: `${randomxAutoMessage}\n` });
    } catch {
      // ignore
    }
  }

  minerProcess = spawn(spawnCommand, spawnArgs, {
    cwd: minerCwd,
    env
  });

  // Start Afterburner service (best-effort, non-blocking) when enabled.
  if (config.aiAfterburner !== false) {
    void ensureAfterburnerServiceRunning()
      .then(() => afterburnerSend({ cmd: 'start' }))
      .catch((err) => {
        try {
          sendToRenderer('miner-output', {
            stream: 'stderr',
            text: `[afterburner] failed to start: ${err?.message || String(err)}\n`
          });
        } catch {
          // ignore
        }
      });
  }

  minerProcess.on('error', (err) => {
    console.error('Failed to start miner process:', err);
    minerProcess = null;
    sendToRenderer('miner-error', { message: err.message });
    sendToRenderer('miner-stopped', { code: -1 });
    updateTrayMenu(minerStats);
  });

  // Log output
  // Prevent log files from growing without bound (esp. if miner is too chatty).
  rotateFileIfTooLarge(LOG_PATH, MAX_MINER_LOG_BYTES, MAX_MINER_LOG_BACKUPS);
  const logStream = fs.createWriteStream(LOG_PATH, { flags: 'a' });

  try {
    logStream.write(
      `\n===== MINER START ${new Date().toISOString()} algorithm=${config.algorithm || ''} mode=${config.gpu ? 'gpu' : 'cpu'} =====\n`
    );
    if (randomxAutoMessage) {
      logStream.write(`[INFO] ${randomxAutoMessage}\n`);
    }
  } catch {
    // ignore
  }

  const shouldSkipFileLogLine = (text) => {
    // Prevent massive log growth from ultra-frequent debug spam.
    if (/^\s*DEBUG:\s*Using C\+\+ library for hash\s*$/i.test(String(text).trim())) return true;
    return false;
  };

  const maybeEmitBlockFound = (text) => {
    // Miner prints: "KWIIIIK KEPORKAK NASEL BLOK <height> !!!"
    const m = text.match(/KEPORKAK\s+NASEL\s+BLOK\s+(\d+)/i);
    if (m) {
      sendToRenderer('block-found', { height: parseInt(m[1], 10) });
      return;
    }
    if (/block_found/i.test(text) || /BLOCK\s+FOUND/i.test(text)) {
      sendToRenderer('block-found', {});
    }
  };
  
  minerProcess.stdout.on('data', (data) => {
    rotateFileIfTooLarge(LOG_PATH, MAX_MINER_LOG_BYTES, MAX_MINER_LOG_BACKUPS);
    const output = data.toString();
    if (!shouldSkipFileLogLine(output)) {
      logStream.write(`[STDOUT] ${output}`);
    }
    sendToRenderer('miner-output', { stream: 'stdout', text: output });
    maybeEmitBlockFound(output);
    parseMinerOutput(output);
  });

  minerProcess.stderr.on('data', (data) => {
    const output = data.toString();
    if (!shouldSkipFileLogLine(output)) {
      logStream.write(`[STDERR] ${output}`);
    }
    console.log('Miner:', output);
    sendToRenderer('miner-output', { stream: 'stderr', text: output });
    maybeEmitBlockFound(output);
  });

  minerProcess.on('close', (code) => {
    logStream.end();
    console.log(`Miner process exited with code ${code}`);
    minerProcess = null;
    
    minerStats = { ...minerStats, hashrate: 0 };
    updateTrayMenu(minerStats);
    sendToRenderer('miner-stopped', { code });
  });

  sendToRenderer('miner-started', {});
  updateTrayMenu(minerStats);

  return { success: true };
}

function ensureAfterburnerServiceRunning() {
  return new Promise((resolve, reject) => {
    try {
      if (afterburnerProc && afterburnerReady) return resolve(true);

      if (!fs.existsSync(AFTERBURNER_SCRIPT_PATH)) {
        return reject(new Error(`Afterburner service not found at: ${AFTERBURNER_SCRIPT_PATH}`));
      }

      if (afterburnerProc) {
        // Process exists but not ready yet.
        const t = setTimeout(() => reject(new Error('Afterburner service startup timed out')), 4000);
        const check = () => {
          if (afterburnerReady) {
            clearTimeout(t);
            resolve(true);
          } else {
            setTimeout(check, 100);
          }
        };
        check();
        return;
      }

      afterburnerReady = false;
      afterburnerStdoutBuf = '';
      afterburnerQueue = [];

      const cwd = IS_PACKAGED ? process.resourcesPath : path.join(APP_ROOT, '..');
      const cmd = process.platform === 'darwin' ? 'python3' : 'python';
      afterburnerProc = spawn(cmd, [AFTERBURNER_SCRIPT_PATH], {
        cwd,
        env: {
          ...process.env,
          PYTHONUTF8: '1',
          PYTHONIOENCODING: 'utf-8',
          PYTHONUNBUFFERED: '1'
        }
      });

      afterburnerProc.on('error', (err) => {
        afterburnerProc = null;
        afterburnerReady = false;
        reject(err);
      });

      const failAllPending = (error) => {
        const q = afterburnerQueue.slice();
        afterburnerQueue = [];
        for (const item of q) {
          try {
            item.reject(error);
          } catch {
            // ignore
          }
        }
      };

      afterburnerProc.on('close', (code) => {
        const err = new Error(`Afterburner service exited (code ${code})`);
        afterburnerProc = null;
        afterburnerReady = false;
        failAllPending(err);
      });

      afterburnerProc.stderr.on('data', (d) => {
        const text = d.toString();
        try {
          sendToRenderer('miner-output', { stream: 'stderr', text: `[afterburner] ${text}` });
        } catch {
          // ignore
        }
      });

      afterburnerProc.stdout.on('data', (d) => {
        afterburnerStdoutBuf += d.toString();
        while (true) {
          const idx = afterburnerStdoutBuf.indexOf('\n');
          if (idx < 0) break;
          const line = afterburnerStdoutBuf.slice(0, idx).trim();
          afterburnerStdoutBuf = afterburnerStdoutBuf.slice(idx + 1);
          if (!line) continue;

          let msg;
          try {
            msg = JSON.parse(line);
          } catch {
            continue;
          }

          if (!afterburnerReady && msg?.ok === true && msg?.status === 'ready') {
            afterburnerReady = true;
            resolve(true);
            continue;
          }

          const pending = afterburnerQueue.shift();
          if (pending) pending.resolve(msg);
        }
      });

      // Wait briefly for ready line.
      const t = setTimeout(() => {
        if (!afterburnerReady) reject(new Error('Afterburner service startup timed out'));
      }, 4000);
      const check = () => {
        if (afterburnerReady) {
          clearTimeout(t);
          resolve(true);
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    } catch (err) {
      reject(err);
    }
  });
}

function afterburnerSend(payload) {
  return new Promise(async (resolve, reject) => {
    try {
      await ensureAfterburnerServiceRunning();
      if (!afterburnerProc || !afterburnerProc.stdin?.writable) {
        return reject(new Error('Afterburner service not running'));
      }

      const id = afterburnerReqId++;
      const req = { id, ...payload };
      afterburnerQueue.push({ resolve, reject });
      afterburnerProc.stdin.write(`${JSON.stringify(req)}\n`);
    } catch (err) {
      reject(err);
    }
  });
}

async function stopAfterburnerService() {
  try {
    if (!afterburnerProc) return;
    try {
      await afterburnerSend({ cmd: 'stop' });
    } catch {
      // ignore
    }
    try {
      afterburnerProc.kill('SIGTERM');
    } catch {
      // ignore
    }
  } finally {
    afterburnerProc = null;
    afterburnerReady = false;
    afterburnerStdoutBuf = '';
    afterburnerQueue = [];
  }
}

function tryUpdateStatsFromFile() {
  try {
    if (!fs.existsSync(STATS_PATH)) return false;
    const raw = fs.readFileSync(STATS_PATH, 'utf8');
    if (!raw) return false;
    const payload = JSON.parse(raw);

    // Map miner stats-file payload to desktop agent stats
    const toNum = (v) => {
      if (typeof v === 'number' && Number.isFinite(v)) return v;
      if (typeof v === 'string' && v.trim() !== '') {
        const n = Number(v);
        if (Number.isFinite(n)) return n;
      }
      return null;
    };

    // Prefer total hashrate; fall back to alternate keys.
    const hr = toNum(payload.hashrate);
    const hrWindow = toNum(payload.hashrate_window_hs);
    const hrCpu = toNum(payload.hashrate_cpu);
    const hrGpu = toNum(payload.hashrate_gpu);
    if (hr != null) minerStats.hashrate = hr;
    else if (hrWindow != null) minerStats.hashrate = hrWindow;
    else if (hrCpu != null || hrGpu != null) minerStats.hashrate = (hrCpu || 0) + (hrGpu || 0);

    if (typeof payload.shares_sent === 'number') minerStats.shares = payload.shares_sent;
    if (typeof payload.shares_accepted === 'number') minerStats.accepted = payload.shares_accepted;
    if (typeof payload.shares_rejected === 'number') minerStats.rejected = payload.shares_rejected;
    if (typeof payload.uptime_sec === 'number') minerStats.uptime = Math.floor(payload.uptime_sec);

    return true;
  } catch (err) {
    // Ignore stats parsing issues; keep UI responsive
    return false;
  }
}

async function stopMiningAsync() {
  if (!minerProcess) {
    return { success: true, alreadyStopped: true };
  }

  if (minerStopping && minerStopPromise) {
    return minerStopPromise;
  }

  minerStopping = true;
  const proc = minerProcess;

  minerStopPromise = new Promise((resolve) => {
    let finished = false;

    const finish = (result) => {
      if (finished) return;
      finished = true;
      minerStopping = false;
      minerStopPromise = null;
      resolve(result);
    };

    const killTimer = setTimeout(() => {
      try {
        proc.kill('SIGKILL');
      } catch {
        // ignore
      }
    }, 5000);

    proc.once('close', (code) => {
      clearTimeout(killTimer);
      finish({ success: true, code });
    });

    try {
      proc.kill('SIGTERM');
    } catch (err) {
      clearTimeout(killTimer);
      finish({ success: false, error: err?.message || String(err) });
    }
  });

  return minerStopPromise;
}

function stopMining() {
  void stopMiningAsync();
}

function parseMinerOutput(output) {
  // Parse hashrate: "Hashrate: 123.45 H/s"
  const hashrateMatch = output.match(/Hashrate:\s*([\d.]+)\s*H\/s/i);
  if (hashrateMatch) {
    minerStats.hashrate = parseFloat(hashrateMatch[1]);
  }

  // Parse shares: "Share accepted (123/125)"
  const shareMatch = output.match(/Share\s+accepted\s+\((\d+)\/(\d+)\)/i);
  if (shareMatch) {
    minerStats.accepted = parseInt(shareMatch[1]);
    minerStats.shares = parseInt(shareMatch[2]);
  }

  // Parse consciousness: "Level: MENTAL (XP: 1250)"
  const consciousnessMatch = output.match(/Level:\s*(\w+)\s+\(XP:\s*(\d+)\)/i);
  if (consciousnessMatch) {
    minerStats.consciousness_level = consciousnessMatch[1];
    minerStats.consciousness_xp = parseInt(consciousnessMatch[2]);
  }

  updateTrayMenu(minerStats);
  sendToRenderer('stats-update', minerStats);
}

function sendToRenderer(channel, data) {
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send(channel, data);
  }
}

// IPC handlers
ipcMain.handle('get-config', () => {
  return loadConfig();
});

ipcMain.handle('save-config', (event, config) => {
  const ok = saveConfig(config);
  // Apply Afterburner enable/disable immediately (no need to restart miner).
  try {
    if (config?.aiAfterburner === false) {
      void stopAfterburnerService();
    } else {
      void ensureAfterburnerServiceRunning().then(() => afterburnerSend({ cmd: 'start' }));
    }
  } catch {
    // ignore
  }
  return ok;
});

ipcMain.handle('get-system-info', () => {
  const cpuCount = Array.isArray(os.cpus?.()) ? os.cpus().length : 1;
  return {
    cpuCount: Math.max(1, cpuCount)
  };
});

ipcMain.handle('start-mining', (event, config) => {
  saveConfig(config);
  return startMining(config);
});

ipcMain.handle('stop-mining', async () => {
  const result = await stopMiningAsync();
  return result.success ? { success: true } : { success: false, error: result.error };
});

ipcMain.handle('get-stats', () => {
  return {
    ...minerStats,
    isRunning: minerProcess !== null
  };
});

ipcMain.handle('open-logs', () => {
  const { shell } = require('electron');
  shell.openPath(LOG_PATH);
  return { success: true };
});

// Wallet IPC handlers
ipcMain.handle('generate-wallet', () => {
  try {
    // Ensure wallets directory exists
    if (!fs.existsSync(WALLETS_PATH)) {
      fs.mkdirSync(WALLETS_PATH, { recursive: true });
    }

    // Generate new wallet
    const wallet = WalletGenerator.generateWallet();
    
    console.log('Generated wallet:', wallet.address);
    return { success: true, wallet };
  } catch (error) {
    console.error('Wallet generation failed:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('save-wallet', (event, { wallet, password, name }) => {
  try {
    // Encrypt private key
    const encrypted = WalletGenerator.encryptPrivateKey(wallet.privateKey, password);
    
    // Wallet data to save
    const walletData = {
      version: '2.9.0',
      name: name || 'My Wallet',
      address: wallet.address,
      publicKey: wallet.publicKey,
      encryptedPrivateKey: encrypted,
      mnemonic: wallet.mnemonic, // WARNING: In production, encrypt this too!
      createdAt: wallet.createdAt,
      lastUsed: new Date().toISOString()
    };
    
    // Save to file
    const filename = `${wallet.address.substring(0, 15)}.json`;
    const filePath = path.join(WALLETS_PATH, filename);
    fs.writeFileSync(filePath, JSON.stringify(walletData, null, 2));
    
    console.log('Wallet saved:', filePath);
    return { success: true, filePath };
  } catch (error) {
    console.error('Wallet save failed:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('list-wallets', () => {
  try {
    if (!fs.existsSync(WALLETS_PATH)) {
      return { success: true, wallets: [] };
    }
    
    const files = fs.readdirSync(WALLETS_PATH).filter(f => f.endsWith('.json'));
    const wallets = [];
    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(WALLETS_PATH, file), 'utf8'));
        if (!data?.address) continue;
        wallets.push({
          name: data.name,
          address: data.address,
          createdAt: data.createdAt,
          lastUsed: data.lastUsed
        });
      } catch (err) {
        console.warn('Skipping invalid wallet file:', file, err?.message || err);
      }
    }
    
    return { success: true, wallets };
  } catch (error) {
    console.error('List wallets failed:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('import-wallet', (event, { mnemonic, password, name }) => {
  try {
    // TODO: Implement mnemonic -> keypair derivation (BIP39/BIP32)
    // For now, just validate format
    const words = mnemonic.trim().split(/\s+/);
    if (words.length !== 12) {
      throw new Error('Invalid mnemonic: must be 12 words');
    }
    
    return { success: false, error: 'Mnemonic import not yet implemented' };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('export-wallet', (event, { address, password }) => {
  try {
    // Find wallet file
    const files = fs.readdirSync(WALLETS_PATH);
    const walletFile = files.find(f => f.startsWith(address.substring(0, 15)));
    
    if (!walletFile) {
      throw new Error('Wallet not found');
    }
    
    const walletData = JSON.parse(
      fs.readFileSync(path.join(WALLETS_PATH, walletFile), 'utf8')
    );
    
    // Decrypt private key
    const privateKey = WalletGenerator.decryptPrivateKey(
      walletData.encryptedPrivateKey,
      password
    );
    
    return {
      success: true,
      wallet: {
        address: walletData.address,
        publicKey: walletData.publicKey,
        privateKey,
        mnemonic: walletData.mnemonic
      }
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('validate-address', (event, address) => {
  const type = WalletGenerator.getAddressType(address);
  return {
    success: true,
    // valid == chain-compatible
    valid: type === 'zion1',
    type
  };
});

async function zionRpcCall(rpcUrl, method, params) {
  const url = (rpcUrl || '').toString().trim();
  if (!url) {
    throw new Error('RPC URL is missing');
  }

  const body = {
    jsonrpc: '2.0',
    id: 'zion-desktop-agent',
    method,
    params
  };

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`RPC HTTP ${res.status}${text ? `: ${text}` : ''}`);
  }

  const json = await res.json();
  if (json?.error) {
    const msg = json.error?.message || JSON.stringify(json.error);
    throw new Error(msg);
  }
  return json?.result;
}

ipcMain.handle('wallet-get-balance', async (event, { rpcUrl, address }) => {
  try {
    const addr = (address || '').toString().trim();
    const type = WalletGenerator.getAddressType(addr);
    if (type !== 'zion1') {
      return { success: false, error: 'Address must be a zion1... address' };
    }

    const result = await zionRpcCall(rpcUrl, 'getbalance', { address: addr });
    if (result?.error) return { success: false, error: result.error };
    return { success: true, balance: result?.balance ?? 0, address: result?.address ?? addr };
  } catch (error) {
    return { success: false, error: error?.message || String(error) };
  }
});

ipcMain.handle('wallet-send-transaction', async (event, { rpcUrl, from, to, amount, purpose }) => {
  try {
    const fromAddr = (from || '').toString().trim();
    const toAddr = (to || '').toString().trim();
    const fromType = WalletGenerator.getAddressType(fromAddr);
    const toType = WalletGenerator.getAddressType(toAddr);
    if (fromType !== 'zion1' || toType !== 'zion1') {
      return { success: false, error: 'Both from/to addresses must be zion1... addresses' };
    }

    const amt = Number(amount);
    if (!Number.isFinite(amt) || amt <= 0) {
      return { success: false, error: 'Amount must be a positive number' };
    }

    const result = await zionRpcCall(rpcUrl, 'sendtransaction', {
      from: fromAddr,
      to: toAddr,
      amount: amt,
      purpose: (purpose || '').toString()
    });

    if (result?.error) return { success: false, error: result.error };
    return { success: true, txId: result?.tx_id, status: result?.status };
  } catch (error) {
    return { success: false, error: error?.message || String(error) };
  }
});

ipcMain.handle('wallet-generate-qr', async (event, { text }) => {
  try {
    const value = (text || '').toString();
    if (!value.trim()) {
      return { success: false, error: 'QR text is empty' };
    }
    const dataUrl = await QRCode.toDataURL(value, {
      errorCorrectionLevel: 'M',
      margin: 1,
      scale: 6
    });
    return { success: true, dataUrl };
  } catch (error) {
    return { success: false, error: error?.message || String(error) };
  }
});

ipcMain.handle('ai-chat', async (event, { endpoint, model, messages, apiKey }) => {
  try {
    const url = (endpoint || '').toString().trim();
    const m = (model || '').toString().trim();
    const msgs = Array.isArray(messages) ? messages : [];
    if (!url) return { success: false, error: 'Chat endpoint is missing' };
    if (!m) return { success: false, error: 'Chat model is missing' };
    if (msgs.length === 0) return { success: false, error: 'No messages provided' };

    const isOllamaLike = /\/api\/chat\b/i.test(url);
    const isOpenAIResponses = /\/v1\/responses\b/i.test(url);
    const headers = { 'content-type': 'application/json' };
    const key = (apiKey || '').toString().trim();
    if (!isOllamaLike && key) {
      headers.authorization = `Bearer ${key}`;
    }

    // Ollama-style (local) vs OpenAI-compatible (cloud)
    // Support both Chat Completions (/v1/chat/completions) and Responses (/v1/responses).
    const body = (() => {
      if (isOllamaLike) return { model: m, messages: msgs, stream: false };
      if (isOpenAIResponses) {
        const input = msgs.map((mm) => ({
          role: mm?.role || 'user',
          content: [{ type: 'text', text: String(mm?.content ?? '') }]
        }));
        return { model: m, input };
      }
      return { model: m, messages: msgs, stream: false };
    })();

    const controller = new AbortController();
    const timeoutMs = 45_000;
    const t = setTimeout(() => controller.abort(), timeoutMs);

    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: controller.signal
    }).finally(() => clearTimeout(t));

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      let detail = text || res.statusText;
      try {
        const j = JSON.parse(text);
        detail = j?.error?.message || detail;
      } catch {
        // ignore
      }
      return { success: false, error: `HTTP ${res.status}: ${detail}` };
    }

    const json = await res.json();

    // Ollama: { message: { content } }
    // OpenAI-compatible: { choices: [{ message: { content } }] }
    // OpenAI Responses: { output_text: "..." }
    const content =
      json?.message?.content ??
      json?.choices?.[0]?.message?.content ??
      json?.choices?.[0]?.delta?.content ??
      json?.output_text ??
      json?.output?.[0]?.content?.[0]?.text;

    if (!content) return { success: false, error: 'Invalid chat response' };
    return { success: true, message: { role: 'assistant', content: String(content) } };
  } catch (error) {
    const msg = error?.name === 'AbortError'
      ? 'Chat request timed out'
      : (error?.message || String(error));
    return { success: false, error: msg };
  }
});

ipcMain.handle('afterburner-command', async (event, data) => {
  try {
    const cmd = String(data?.cmd || '').trim().toLowerCase();
    const args = Array.isArray(data?.args) ? data.args.map((x) => String(x)) : [];

    const helpText =
      'Afterburner commands:\n' +
      '  /ab start\n' +
      '  /ab stop\n' +
      '  /ab stats\n' +
      '  /ab task <type> [compute=1.0] [priority=5] [sacred]\n' +
      '  /ab cool\n';

    if (!cmd || cmd === 'help') return { success: true, text: helpText };

    if (cmd === 'start') {
      const r = await afterburnerSend({ cmd: 'start' });
      if (!r?.ok) return { success: false, error: r?.error || 'start failed' };
      return { success: true, text: 'Afterburner started.' };
    }

    if (cmd === 'stop') {
      await stopAfterburnerService();
      return { success: true, text: 'Afterburner stopped.' };
    }

    if (cmd === 'cool') {
      const r = await afterburnerSend({ cmd: 'cool' });
      if (!r?.ok) return { success: false, error: r?.error || 'cool failed' };
      return { success: true, text: 'Emergency cooling activated.' };
    }

    if (cmd === 'stats') {
      const r = await afterburnerSend({ cmd: 'stats' });
      if (!r?.ok) return { success: false, error: r?.error || 'stats failed' };
      const st = r?.stats || {};
      const pm = st?.performance_metrics || {};
      const temp = pm?.afterburner_temperature;
      const tps = pm?.tasks_per_second;
      const eff = pm?.compute_efficiency;
      return {
        success: true,
        text:
          `Afterburner: ${st?.status || 'unknown'}\n` +
          `Active tasks: ${st?.active_tasks ?? '—'}\n` +
          `Completed: ${st?.completed_tasks ?? '—'} / Failed: ${st?.failed_tasks ?? '—'}\n` +
          `Temp: ${temp != null ? Number(temp).toFixed(1) : '—'} °C\n` +
          `Tasks/sec: ${tps != null ? Number(tps).toFixed(2) : '—'}\n` +
          `Efficiency: ${eff != null ? Number(eff).toFixed(1) : '—'}%`
      };
    }

    if (cmd === 'task') {
      const taskType = (args[0] || 'generic').trim() || 'generic';
      const computeReq = args[1] != null && args[1] !== '' ? Number(args[1]) : 1.0;
      const priority = args[2] != null && args[2] !== '' ? Number(args[2]) : 5;
      const sacred = args.some((a) => /^sacred$/i.test(a)) || /^sacred$/i.test(args[3] || '');
      const r = await afterburnerSend({
        cmd: 'task',
        task_type: taskType,
        compute_req: Number.isFinite(computeReq) ? computeReq : 1.0,
        priority: Number.isFinite(priority) ? priority : 5,
        sacred
      });
      if (!r?.ok) return { success: false, error: r?.error || 'task failed' };
      return { success: true, text: `Task queued: ${taskType} (id=${r?.task_id ?? '—'})` };
    }

    return { success: false, error: 'Unknown afterburner command. Try /ab help.' };
  } catch (err) {
    return { success: false, error: err?.message || String(err) };
  }
});

// App lifecycle
app.whenReady().then(() => {
  console.log('ZION Desktop Agent v2.9 started');
  console.log('Config path:', CONFIG_PATH);
  console.log('Miner path:', MINER_PATH);
  console.log('Log path:', LOG_PATH);
  console.log('Cache path:', CACHE_PATH);
  
  // Ensure all required directories exist
  ensureDirectories();
  migrateLegacyUserDataIfNeeded();
  
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Tray app: do not quit on Windows/Linux when window closes/crashes.
  // Users can quit from tray.
  if (process.platform === 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
  stopMining();
  void stopAfterburnerService();
});

// Stats update interval
setInterval(() => {
  if (minerProcess) {
    const updated = tryUpdateStatsFromFile();
    if (!updated) minerStats.uptime += 5;
  }

  // Best-effort: merge Afterburner metrics into minerStats (even if miner is stopped).
  if (afterburnerProc && afterburnerReady) {
    void afterburnerSend({ cmd: 'stats' })
      .then((r) => {
        if (!r?.ok) return;
        const st = r?.stats || {};
        const pm = st?.performance_metrics || {};
        const temp = pm?.afterburner_temperature;
        const tps = pm?.tasks_per_second;
        const eff = pm?.compute_efficiency;
        const speed10 = pm?.speed_10s;
        const speed60 = pm?.speed_60s;
        const speed15 = pm?.speed_15m;
        const succ60 = pm?.success_rate_60s;
        const lat10 = pm?.latency_avg_10s_ms;
        const lat60 = pm?.latency_avg_60s_ms;
        const sacredRatio = pm?.sacred_enhancement_ratio;
        minerStats.afterburner_temp_c = temp != null ? Number(temp).toFixed(1) : '';
        minerStats.afterburner_tasks_per_sec = tps != null ? Number(tps).toFixed(2) : '';
        minerStats.afterburner_efficiency_pct = eff != null ? Number(eff) : '';
        minerStats.afterburner_speed_10s = speed10 != null ? Number(speed10).toFixed(2) : '';
        minerStats.afterburner_speed_60s = speed60 != null ? Number(speed60).toFixed(2) : '';
        minerStats.afterburner_speed_15m = speed15 != null ? Number(speed15).toFixed(2) : '';
        minerStats.afterburner_success_60s_pct = succ60 != null ? Number(succ60) : '';
        minerStats.afterburner_latency_10s_ms = lat10 != null ? Number(lat10) : '';
        minerStats.afterburner_latency_60s_ms = lat60 != null ? Number(lat60) : '';
        minerStats.afterburner_status = st?.status || '';
        minerStats.afterburner_compute_mode = st?.compute_mode || '';
        minerStats.afterburner_sacred = typeof st?.sacred_enhancement === 'boolean' ? st.sacred_enhancement : '';
        minerStats.afterburner_active_tasks = typeof st?.active_tasks === 'number' ? st.active_tasks : '';
        minerStats.afterburner_completed_tasks = typeof st?.completed_tasks === 'number' ? st.completed_tasks : '';
        minerStats.afterburner_failed_tasks = typeof st?.failed_tasks === 'number' ? st.failed_tasks : '';
        minerStats.afterburner_utilization_pct = typeof st?.compute_utilization === 'number' ? st.compute_utilization : '';
        minerStats.afterburner_available_compute = typeof st?.available_compute === 'number' ? Number(st.available_compute).toFixed(2) : '';
        minerStats.afterburner_total_compute = typeof st?.total_compute === 'number' ? Number(st.total_compute).toFixed(2) : '';
        minerStats.afterburner_sacred_ratio = sacredRatio != null ? Number(sacredRatio).toFixed(2) : '';

        // Extended details
        minerStats.afterburner_uptime_sec = typeof st?.uptime_sec === 'number' ? st.uptime_sec : '';
        minerStats.afterburner_last_error = typeof st?.last_error === 'string' ? st.last_error : '';
        minerStats.afterburner_throttle_events = typeof st?.throttle_events === 'number' ? st.throttle_events : '';
        minerStats.afterburner_queue_depth = typeof st?.queue_depth === 'number' ? st.queue_depth : '';
        minerStats.afterburner_queue_by_type = st?.queue_by_type && typeof st.queue_by_type === 'object' ? st.queue_by_type : '';
        minerStats.afterburner_last_task_type = typeof st?.last_task_type === 'string' ? st.last_task_type : '';
        minerStats.afterburner_last_task_ms = typeof st?.last_task_duration_ms === 'number' ? st.last_task_duration_ms : '';
        minerStats.afterburner_avg_task_ms = typeof st?.avg_task_duration_ms === 'number' ? st.avg_task_duration_ms : '';
        sendToRenderer('stats-update', minerStats);
      })
      .catch(() => {
        // ignore
      });
  } else {
    // Still refresh UI for miner stats.
    sendToRenderer('stats-update', minerStats);
  }
}, 5000);
