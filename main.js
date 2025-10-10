// main.js
const { app, BrowserWindow, screen, ipcMain } = require('electron');
const net = require('net');
const fs = require('fs');

let win;
let socketServer;
const socketPath = '/tmp/optimus-electron-socket';

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  win = new BrowserWindow({
    width: 350,
    height: 350,
    x: width - 370,   // push to right edge
    y: 20,            // push down a little from top
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,    // Don't show in dock/taskbar
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // 🚀 MAKE IT TRULY SYSTEM-WIDE (above ALL apps including fullscreen)
  if (process.platform === 'darwin') {
    // Show on all macOS desktops/spaces
    win.setVisibleOnAllWorkspaces(true, { 
      visibleOnFullScreen: true 
    });
    
    // Set highest priority level - above fullscreen apps, games, presentations
    win.setAlwaysOnTop(true, 'screen-saver', 1);
    
    // Alternative levels you can try:
    // win.setAlwaysOnTop(true, 'pop-up-menu', 1);     // Above menus
    // win.setAlwaysOnTop(true, 'modal-panel', 1);     // Above modals
    // win.setAlwaysOnTop(true, 'status', 1);          // Status bar level
  }

  win.loadFile('index.html');
  
  // 🎯 Optional: Make window click-through in certain areas
  // win.setIgnoreMouseEvents(true, { forward: true });
  
  // Create socket server to receive commands
  startSocketServer();
  
  // 📍 Optional: Add window controls via IPC
  setupWindowControls();
}

function setupWindowControls() {
  // Handle window positioning from renderer process
  ipcMain.on('move-window', (event, x, y) => {
    if (win) {
      win.setPosition(x, y);
    }
  });
  
  // Handle window visibility toggle
  ipcMain.on('toggle-window', () => {
    if (win) {
      if (win.isVisible()) {
        win.hide();
      } else {
        win.show();
      }
    }
  });
  
  // Handle window opacity changes
  ipcMain.on('set-opacity', (event, opacity) => {
    if (win) {
      win.setOpacity(opacity);
    }
  });
}

function startSocketServer() {
  // Remove existing socket file if it exists
  if (fs.existsSync(socketPath)) {
    fs.unlinkSync(socketPath);
  }
  
  socketServer = net.createServer((socket) => {
    socket.on('data', (data) => {
      const command = data.toString().trim();
      handleCommand(command);
    });
  });
  
  socketServer.listen(socketPath, () => {
    console.log('Socket server listening on', socketPath);
  });
}

function handleCommand(command) {
  console.log('Received command:', command);
  
  // Parse commands with parameters
  const [cmd, ...params] = command.split(' ');
  
  switch(cmd) {
    case 'play':
      playAnimation();
      break;
    case 'pause':
      pauseAnimation();
      break;
    case 'hide':
      if (win) win.hide();
      break;
    case 'show':
      if (win) win.show();
      break;
    case 'move':
      if (params.length >= 2) {
        const [x, y] = params.map(Number);
        if (win) win.setPosition(x, y);
      }
      break;
    case 'opacity':
      if (params.length >= 1) {
        const opacity = parseFloat(params[0]);
        if (win && opacity >= 0 && opacity <= 1) {
          win.setOpacity(opacity);
        }
      }
      break;
    case 'reload':
      if (win) win.reload();
      break;
    case 'devtools':
      if (win) win.webContents.openDevTools();
      break;
    case 'stop':
      // Clean shutdown
      if (socketServer) {
        socketServer.close();
      }
      app.quit();
      break;
  }
}

function playAnimation() {
  if (win) {
    win.webContents.executeJavaScript(`
      // Send message to iframe to play animation
      const iframe = document.getElementById('optimus');
      if (iframe) {
        iframe.contentWindow.postMessage({action: 'play'}, '*');
      }
    `);
    console.log('▶️ Playing animation');
  }
}

function pauseAnimation() {
  if (win) {
    win.webContents.executeJavaScript(`
      // Send message to iframe to pause animation
      const iframe = document.getElementById('optimus');
      if (iframe) {
        iframe.contentWindow.postMessage({action: 'pause'}, '*');
      }
    `);
    console.log('⏸️ Pausing animation');
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  // Clean up socket file
  if (fs.existsSync(socketPath)) {
    fs.unlinkSync(socketPath);
  }
});

// 🎮 Optional: Global shortcuts for quick control
app.whenReady().then(() => {
  const { globalShortcut } = require('electron');
  
  // Cmd+Shift+P to toggle play/pause
  globalShortcut.register('CommandOrControl+Shift+P', () => {
    // Toggle animation state
    if (win) {
      win.webContents.executeJavaScript(`
        const iframe = document.getElementById('optimus');
        if (iframe) {
          // You could track state and toggle accordingly
          iframe.contentWindow.postMessage({action: 'toggle'}, '*');
        }
      `);
    }
  });
  
  // Cmd+Shift+H to toggle window visibility
  globalShortcut.register('CommandOrControl+Shift+H', () => {
    if (win) {
      if (win.isVisible()) {
        win.hide();
      } else {
        win.show();
      }
    }
  });
});

app.on('will-quit', () => {
  // Unregister all shortcuts
  const { globalShortcut } = require('electron');
  globalShortcut.unregisterAll();
});