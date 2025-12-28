// ZION Desktop Mining Agent v2.9 - Preload Script
// IPC bridge between main process and renderer (security layer)

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // System info
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),

  // Config management
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),

  // Mining control
  startMining: (config) => ipcRenderer.invoke('start-mining', config),
  stopMining: () => ipcRenderer.invoke('stop-mining'),
  
  // Stats
  getStats: () => ipcRenderer.invoke('get-stats'),
  
  // Logs
  openLogs: () => ipcRenderer.invoke('open-logs'),

  // Wallet management
  generateWallet: () => ipcRenderer.invoke('generate-wallet'),
  saveWallet: (data) => ipcRenderer.invoke('save-wallet', data),
  listWallets: () => ipcRenderer.invoke('list-wallets'),
  importWallet: (data) => ipcRenderer.invoke('import-wallet', data),
  exportWallet: (data) => ipcRenderer.invoke('export-wallet', data),
  validateAddress: (address) => ipcRenderer.invoke('validate-address', address),

  // Wallet RPC
  walletGetBalance: (data) => ipcRenderer.invoke('wallet-get-balance', data),
  walletSendTransaction: (data) => ipcRenderer.invoke('wallet-send-transaction', data),
  walletGenerateQr: (data) => ipcRenderer.invoke('wallet-generate-qr', data),

  // AI / Chat
  aiChat: (data) => ipcRenderer.invoke('ai-chat', data),

  // AI Afterburner (commands)
  afterburnerCommand: (data) => ipcRenderer.invoke('afterburner-command', data),

  // Event listeners
  onMinerStarted: (callback) => {
    ipcRenderer.on('miner-started', (event, data) => callback(data));
  },
  onMinerStopped: (callback) => {
    ipcRenderer.on('miner-stopped', (event, data) => callback(data));
  },
  onMinerError: (callback) => {
    ipcRenderer.on('miner-error', (event, data) => callback(data));
  },
  onMinerOutput: (callback) => {
    ipcRenderer.on('miner-output', (event, data) => callback(data));
  },
  onBlockFound: (callback) => {
    ipcRenderer.on('block-found', (event, data) => callback(data));
  },
  onStatsUpdate: (callback) => {
    ipcRenderer.on('stats-update', (event, data) => callback(data));
  },

  // Cleanup listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

console.log('Preload script loaded - electronAPI available');
