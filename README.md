# Cascade Tile Scanner

A cross-platform Warframe tile scanner for Zariman Survival (Void Cascade) missions with a beautiful web interface.

**Works on:** Windows, Linux, and macOS

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web scanner:**
   ```bash
   python3 web_scanner.py
   ```

3. **Open your browser:**
   - Go to: `http://localhost:9000`
   - The interface will auto-refresh every 0.5 seconds

## Features

- ✅ **Fast tile detection** - 10x faster monitoring during missions
- ✅ **Web interface** - Beautiful, real-time tile display in your browser
- ✅ **Terminal output** - Shows all results in terminal (Hyprland compatible)
- ✅ **Auto-detection** - Automatically detects mission start/end
- ✅ **Attempt tracking** - Counts each mission attempt
- ✅ **All tile types** - Hangar, Park, Serenity, Lunaro, Ramp

## Usage

1. Start the scanner before launching Warframe:
   ```bash
   python3 web_scanner.py
   ```

2. Open your browser to `http://localhost:9000`

3. Start a Zariman Survival mission

4. Watch the web interface for real-time tile detection

5. Use Ctrl+C to stop the scanner

## What You'll See

**In Terminal:**
```
🌐 Web Scanner started - Open http://localhost:9000 in your browser
🔍 Starting to monitor log file...
🎮 [Attempt 1] Zariman mission started!
🚀 SWITCHING TO FAST MONITORING MODE!
⚡ FAST DETECTION: Hangar found!
⚡ FAST DETECTION: Park found!
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

### Setting the EE.log File Path

The scanner needs to know where your Warframe log file is located. The path can vary depending on:
- Your operating system (Windows/Linux/Mac)
- Your Steam installation location
- Whether you're using Proton/Wine

**To update the log file path:**

1. Open `web_scanner.py` in a text editor
2. Find this line (around line 280):
   ```python
   self.path = '/mnt/2tb/SteamLibrary/steamapps/compatdata/230410/pfx/drive_c/users/steamuser/AppData/Local/Warframe/EE.log'
   ```
3. Replace it with your actual log file path

**Common locations:**
- **Linux (Steam Proton):** `/path/to/SteamLibrary/steamapps/compatdata/230410/pfx/drive_c/users/steamuser/AppData/Local/Warframe/EE.log`
- **Windows:** `C:\Users\YourUsername\AppData\Local\Warframe\EE.log`
- **Mac:** `~/Library/Application Support/Warframe/EE.log`

**To find your log file:**
1. Launch Warframe once
2. Search for `EE.log` on your system
3. Copy the full path and update it in `web_scanner.py`

## Files

- `web_scanner.py` - Main web-based scanner
- `requirements.txt` - Python dependencies
- `README.md` - This file

That's it! Clean and simple. 🎉
# GascadeTS
