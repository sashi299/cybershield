const { contextBridge, clipboard } = require('electron');

contextBridge.exposeInMainWorld('desktopAPI', {
  isDesktop: true,
  platform: process.platform,
  arch: process.arch,
  readClipboardText: () => clipboard.readText(),
});
