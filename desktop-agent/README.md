<p align="center">
  <img src="../assets/logo/Z.gif" alt="ZION" width="120"/>
</p>

<h1 align="center">ZION Desktop Mining Agent v2.9</h1>

<p align="center">
  <strong>Professional desktop application for ZION TerraNova mining with consciousness evolution tracking.</strong>
</p>

## Features

✨ **Complete Mining Solution**
- One-click start/stop mining
- Real-time hashrate monitoring
- Share acceptance tracking
- System tray integration
- Auto-start on launch

🎮 **Consciousness Gamification**
- Live consciousness level tracking
- XP progress visualization
- Spiritual evolution milestones
- Visual progress indicators

📊 **Professional Dashboard**
- Real-time statistics
- Beautiful gradient UI
- Mining logs viewer
- Configuration management

⚙️ **Easy Configuration**
- Simple wallet setup
- Pool configuration
- CPU/GPU toggle
- Thread optimization

## Quick Start

### Development
```bash
cd desktop-agent
npm install
npm start
```

### Build Release
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## Configuration

On first launch, configure your settings:

1. **Wallet Address**: Your ZION wallet (ZION_...)
2. **Pool**: pool.zionterranova.com:3333 (default)
3. **Worker Name**: Identifier for this miner
4. **Threads**: CPU cores to use
5. **GPU**: Enable GPU mining (if available)

## System Requirements

- **OS**: Windows 10+, macOS 10.13+, Ubuntu 18.04+
- **RAM**: 4GB minimum
- **CPU**: Multi-core recommended
- **GPU**: NVIDIA/AMD (optional)
- **Python**: 3.10+ (for miner backend)

## Architecture

```
desktop-agent/
├── src/
│   ├── main.js         # Electron main process
│   ├── preload.js      # IPC security bridge
│   └── ui/
│       ├── index.html  # Main UI
│       └── renderer.js # UI logic
└── package.json        # Build config
```

## Features in Detail

### System Tray
- Minimize to tray
- Quick start/stop from tray menu
- Real-time hashrate in tooltip
- Status indicators

### Auto-start
- Launch on system startup
- Start mining automatically
- Background operation

### Logs
- Real-time log streaming
- Color-coded messages
- Open log file button
- Auto-scroll

### Stats Tracking
- Current hashrate (H/s)
- Accepted/rejected shares
- Mining uptime
- Consciousness level & XP

## Development

Built with:
- **Electron** 34.0.0 - Desktop framework
- **electron-builder** - Packaging
- **Native HTML/CSS/JS** - No heavy frameworks

## License

MIT - See LICENSE file

## Support

- Website: https://zionterranova.com
- Pool: pool.zionterranova.com:3333
- Docs: https://zionterranova.com/docs

---

**ZION TerraNova v2.9** - Where Technology Meets Spirit 🌟
