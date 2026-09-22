const { app, BrowserWindow, Tray, Menu, globalShortcut, ipcMain, clipboard } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let tray = null;
let backendProcess = null;
const BACKEND_PORT = 8000;

function startBackend() {
  const isDev = process.env.NODE_ENV === 'development';
  const backendDir = path.join(__dirname, '..', '..', 'backend');
  
  console.log('[Desktop] Starting embedded CyberShield FastAPI backend from:', backendDir);
  
  // Spawn Python FastAPI backend as a child process
  backendProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)], {
    cwd: backendDir,
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    shell: true,
  });

  backendProcess.stdout?.on('data', (data) => {
    console.log(`[Backend stdout]: ${data}`);
  });

  backendProcess.stderr?.on('data', (data) => {
    console.log(`[Backend stderr]: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`[Desktop] Backend process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 840,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#030712',
    title: 'CyberShield — Snapdragon AI Threat Detection',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    autoHideMenuBar: true,
  });

  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function setupTray() {
  try {
    tray = new Tray(path.join(__dirname, 'icon.png'));
  } catch (e) {
    // If icon missing, create without tray icon
    return;
  }
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open CyberShield Scanner',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createWindow();
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Quit CyberShield',
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);
  tray.setToolTip('CyberShield — On-Device Threat Detection');
  tray.setContextMenu(contextMenu);
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  setupTray();

  // Register global hotkey Ctrl+Shift+S to bring up quick scanner
  globalShortcut.register('CommandOrControl+Shift+S', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus();
      } else {
        mainWindow.show();
      }
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  if (backendProcess) {
    console.log('[Desktop] Stopping backend process...');
    backendProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
