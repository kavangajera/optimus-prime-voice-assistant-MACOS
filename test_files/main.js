const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

const HISTORY_FILE = path.resolve(__dirname, 'chat_history.json');
let tableWindow = null;

function createRightSideOverlay() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const overlayWidth = 360; // right-side narrow panel
  const overlayHeight = Math.min(400, Math.floor(height * 0.4));

  const win = new BrowserWindow({
    width: overlayWidth,
    height: overlayHeight,
    x: width - overlayWidth - 20, // 20px margin from right
    y: height - overlayHeight - 100, // Position above bottom, with 100px from bottom
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: true,
    hasShadow: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile(path.resolve(__dirname, 'index.html'));
  win.setAlwaysOnTop(true, 'screen-saver');
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  // Make the window interactive for input
  win.setIgnoreMouseEvents(false);

  // Ensure history file exists with initial content
  try {
    if (!fs.existsSync(HISTORY_FILE)) {
      const initialHistory = [
        {
          "role": "bot",
          "text": "How can I help you ?",
          "timestamp": new Date().toISOString()
        }
      ];
      fs.writeFileSync(HISTORY_FILE, JSON.stringify(initialHistory, null, 2));
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('Failed to ensure history file', e);
  }

  // Watch for changes using stat to detect modification time changes
  let lastMtime = null;
  
  function checkForUpdates() {
    try {
      const stats = fs.statSync(HISTORY_FILE);
      if (lastMtime && stats.mtime.getTime() !== lastMtime.getTime()) {
        // File was modified
        lastMtime = stats.mtime;
        if (!win.isDestroyed()) {
          win.webContents.send('log-updated');
        }
        
        // Check if the new message is a table response and open the table window
        try {
          const history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'));
          const lastMessage = history[history.length - 1];
          
          if (lastMessage && lastMessage.role === 'bot') {
            // Check if this looks like a JSON response for tabular data
            const isJsonResponse = lastMessage.text.trim().startsWith('[') || lastMessage.text.trim().startsWith('{');
            if (isJsonResponse) {
              // Create a temporary file with the JSON content
              const tempJsonPath = path.resolve(__dirname, 'temp.json');
              try {
                const parsedJson = JSON.parse(lastMessage.text);
                fs.writeFileSync(tempJsonPath, JSON.stringify(parsedJson, null, 2));
                
                // Open the table view window
                createTableViewWindow();
              } catch (e) {
                console.log('Message is not valid JSON, not opening table view');
              }
            }
          }
        } catch (e) {
          console.error('Error checking for JSON response:', e);
        }
      } else if (!lastMtime) {
        // Initial stats
        lastMtime = stats.mtime;
      }
    } catch (e) {
      // File might not exist yet
      if (e.code === 'ENOENT') {
        // Create the file with initial content if it doesn't exist
        const initialHistory = [
          {
            "role": "bot",
            "text": "How can I help you ?",
            "timestamp": new Date().toISOString()
          }
        ];
        fs.writeFileSync(HISTORY_FILE, JSON.stringify(initialHistory, null, 2));
        lastMtime = fs.statSync(HISTORY_FILE).mtime;
      }
    }
  }

  // Check for updates every 500ms
  setInterval(checkForUpdates, 500);
  
  return win;
}

function createTableViewWindow() {
  // Close existing table window if open
  if (tableWindow && !tableWindow.isDestroyed()) {
    tableWindow.close();
  }
  
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const tableWidth = 800;
  const tableHeight = 600;

  // Calculate center position
  const x = Math.floor((width - tableWidth) / 2);
  const y = Math.floor((height - tableHeight) / 2);

  tableWindow = new BrowserWindow({
    width: tableWidth,
    height: tableHeight,
    x: x, 
    y: y, 
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: true,
    hasShadow: true,
    resizable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  tableWindow.loadFile(path.resolve(__dirname, 'json_to_table.html'));
  
  // When the table window is closed, set the reference to null
  tableWindow.on('closed', () => {
    tableWindow = null;
  });

  return tableWindow;
}

// Handle IPC event to open table view
ipcMain.on('open-table-view', (event) => {
  createTableViewWindow();
});

app.whenReady().then(() => {
  createRightSideOverlay();
});

app.on('window-all-closed', () => {
  // Keep app running as overlay; quit on non-mac
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createRightSideOverlay();
});
