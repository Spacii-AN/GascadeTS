# Cascade Tile Scanner

A cross-platform Warframe tile scanner for Zariman Survival (Void Cascade) missions with a beautiful web interface.

**Works on:** Windows, Linux, and macOS

**Made by:** Spacii-AN

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web scanner:**
   ```bash
   python3 web_scanner.py
   ```
   The scanner will automatically detect your Warframe `EE.log` file - no configuration needed!

3. **Open your browser:**
   - **On the same computer:** Go to `http://localhost:9000`
   - **On other devices:** Go to `http://<your-computer-ip>:9000`
   - The interface will auto-refresh every 0.5 seconds

**To find your computer's IP address:**
- **Linux/Mac:** Run `ip addr` or `ifconfig` in terminal
- **Windows:** Run `ipconfig` in command prompt
- Look for your local network IP (usually starts with 192.168.x.x or 10.x.x.x)

**Note:** If you can't access from other devices, you may need to allow port 9000 through your firewall:
- **Linux (ufw):** `sudo ufw allow 9000`
- **Linux (firewalld):** `sudo firewall-cmd --add-port=9000/tcp`
- **Windows:** Allow Python through Windows Firewall
- **Mac:** Check System Settings > Network > Firewall

## Features

- ✅ **Fast tile detection** - 10x faster monitoring during missions
- ✅ **Web interface** - Beautiful, real-time tile display in your browser
- ✅ **Terminal output** - Shows all results in terminal (Hyprland compatible)
- ✅ **Auto-detection** - Automatically detects mission start/end and EE.log file location
- ✅ **Attempt tracking** - Counts each mission attempt
- ✅ **All tile types** - Hangar, Park, Serenity, Lunaro, Ramp
- ✅ **Zero configuration** - Automatically finds your Warframe log file on Windows, Linux, and macOS

## Usage

1. Start the scanner before launching Warframe:
   ```bash
   python3 web_scanner.py
   ```

2. Open your browser to `http://localhost:9000` (or `http://<your-ip>:9000` from other devices)

3. Start a Zariman Survival mission

4. Watch the web interface for real-time tile detection

5. Use Ctrl+C to stop the scanner

## What You'll See

**In Terminal:**
```
✅ Auto-detected EE.log at: C:\Users\YourUsername\AppData\Local\Warframe\EE.log
🌐 Web Scanner started - Open http://localhost:9000 in your browser
🔍 Starting to monitor log file...
🔄 Starting real-time log monitoring...
🎮 [Attempt 1] Zariman mission started!
🚀 SWITCHING TO FAST MONITORING MODE!
🎯 DETECTED: Hangar tile
🎯 DETECTED: Park tile
```

**In Web Browser:**
- Real-time tile status with visual indicators
- Mission status and attempt counter
- Color-coded status updates
- Auto-refreshing every 0.5 seconds

## Platform Compatibility

✅ **Fully cross-platform!** The scanner works on:
- **Windows** - Native support
- **Linux** - Works with Steam Proton/Wine
- **macOS** - Native support

**Requirements:**
- Python 3.7 or higher
- Internet connection (for initial setup)
- Warframe installed and run at least once (to generate EE.log)

## Configuration

### EE.log Auto-Detection

The scanner **automatically detects** your Warframe log file location! No configuration needed in most cases.

**Auto-detection checks these locations:**

- **Windows:** `%LOCALAPPDATA%\Warframe\EE.log` (typically `C:\Users\YourUsername\AppData\Local\Warframe\EE.log`)
- **Linux (Steam Proton):** 
  - `~/.steam/steam/steamapps/compatdata/230410/pfx/drive_c/users/steamuser/AppData/Local/Warframe/EE.log`
  - `~/.local/share/Steam/steamapps/compatdata/230410/pfx/drive_c/users/steamuser/AppData/Local/Warframe/EE.log`
  - Searches for `SteamLibrary` folders in common mount points (e.g., `/mnt`)
- **macOS:** `~/Library/Application Support/Warframe/EE.log`

**If auto-detection fails:**

The scanner will search common directories for the `EE.log` file. If it still can't find it:
1. Make sure Warframe has been run at least once (to generate `EE.log`)
2. Check the terminal output - it will show the path it's trying to use
3. If needed, you can manually set the path in `web_scanner.py` by modifying the `find_ee_log()` function

## Files

- `web_scanner.py` - Main web-based scanner
- `requirements.txt` - Python dependencies
- `README.md` - This file

That's it! Clean and simple. 🎉
# GascadeTS
