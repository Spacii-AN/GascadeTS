#!/usr/bin/env python3
"""
Web-based Cascade Tile Scanner
Simple web interface to show tile detection results
"""

import os
import re
import time
import json
import threading
import platform
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

def find_ee_log():
    """
    Auto-detect the EE.log file location across different platforms.
    Returns the path if found, None otherwise.
    """
    system = platform.system()
    possible_paths = []
    
    # Windows paths
    if system == 'Windows':
        localappdata = os.getenv('LOCALAPPDATA')
        if localappdata:
            possible_paths.append(os.path.join(localappdata, 'Warframe', 'EE.log'))
        # Also check common user profile location
        username = os.getenv('USERNAME')
        if username:
            possible_paths.append(os.path.join('C:', 'Users', username, 'AppData', 'Local', 'Warframe', 'EE.log'))
    
    # Linux paths (Steam/Proton)
    elif system == 'Linux':
        # Common Steam library locations
        home = os.path.expanduser('~')
        steam_paths = [
            os.path.join(home, '.steam', 'steam', 'steamapps', 'compatdata', '230410', 'pfx', 'drive_c', 'users', 'steamuser', 'AppData', 'Local', 'Warframe', 'EE.log'),
            os.path.join(home, '.local', 'share', 'Steam', 'steamapps', 'compatdata', '230410', 'pfx', 'drive_c', 'users', 'steamuser', 'AppData', 'Local', 'Warframe', 'EE.log'),
        ]
        
        # Check for Steam library folders
        steam_lib_paths = [
            os.path.join(home, '.steam', 'steam', 'steamapps'),
            os.path.join(home, '.local', 'share', 'Steam', 'steamapps'),
        ]
        
        # Look for SteamLibrary folders
        for steam_lib in steam_lib_paths:
            if os.path.isdir(steam_lib):
                parent = os.path.dirname(steam_lib)
                # Check parent directory for SteamLibrary folders
                if os.path.isdir(parent):
                    for item in os.listdir(parent):
                        if 'SteamLibrary' in item or 'steamapps' in item:
                            lib_path = os.path.join(parent, item) if 'SteamLibrary' in item else parent
                            compat_path = os.path.join(lib_path, 'steamapps', 'compatdata', '230410', 'pfx', 'drive_c', 'users', 'steamuser', 'AppData', 'Local', 'Warframe', 'EE.log')
                            if os.path.isfile(compat_path):
                                possible_paths.append(compat_path)
        
        possible_paths.extend(steam_paths)
    
    # macOS paths
    elif system == 'Darwin':
        home = os.path.expanduser('~')
        possible_paths.append(os.path.join(home, 'Library', 'Application Support', 'Warframe', 'EE.log'))
    
    # Check all possible paths
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    
    # If not found in default locations, try searching common directories
    print("🔍 EE.log not found in default locations, searching...")
    search_dirs = []
    
    if system == 'Windows':
        localappdata = os.getenv('LOCALAPPDATA')
        if localappdata:
            search_dirs.append(os.path.dirname(localappdata))  # Search in AppData parent
        search_dirs.append(os.path.join('C:', 'Users'))
    elif system == 'Linux':
        home = os.path.expanduser('~')
        search_dirs.append(os.path.join(home, '.steam'))
        search_dirs.append(os.path.join(home, '.local', 'share', 'Steam'))
        # Also search in common mount points
        if os.path.isdir('/mnt'):
            for item in os.listdir('/mnt'):
                mnt_path = os.path.join('/mnt', item)
                if os.path.isdir(mnt_path):
                    search_dirs.append(mnt_path)
    elif system == 'Darwin':
        home = os.path.expanduser('~')
        search_dirs.append(os.path.join(home, 'Library', 'Application Support'))
    
    # Search for EE.log in these directories (limit depth to avoid long searches)
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        try:
            for root, dirs, files in os.walk(search_dir):
                # Limit search depth to 10 levels to avoid very long searches
                depth = root[len(search_dir):].count(os.sep)
                if depth > 10:
                    dirs[:] = []  # Don't recurse deeper
                    continue
                
                if 'EE.log' in files:
                    found_path = os.path.join(root, 'EE.log')
                    # Verify it's in a Warframe directory
                    if 'Warframe' in found_path:
                        print(f"✅ Found EE.log at: {found_path}")
                        return found_path
        except (PermissionError, OSError):
            continue  # Skip directories we can't access
    
    return None

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Cascade Tile Scanner</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            padding: 20px;
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .status {
            text-align: center;
            font-size: 1.5em;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
        }
        .tiles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .tile {
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2em;
            transition: all 0.3s ease;
        }
        .tile.found {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        }
        .tile.not-found {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
        }
        .tile:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        .mission-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .refresh-info {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Cascade Tile Scanner</h1>
        
        <div class="status" id="status">
            <div class="loading"></div>
            <span id="status-text">Loading...</span>
        </div>
        
        <div class="mission-info">
            <h3>Mission Status</h3>
            <div id="mission-status">Awaiting mission...</div>
            <div id="attempts">Attempts: 0</div>
        </div>
        
        <div class="tiles">
            <div class="tile not-found" id="hangar">
                <div>🏢</div>
                <div>Hangar</div>
                <div id="hangar-status">Not Found</div>
            </div>
            <div class="tile not-found" id="park">
                <div>🌳</div>
                <div>Park</div>
                <div id="park-status">Not Found</div>
            </div>
            <div class="tile not-found" id="serenity">
                <div>🌸</div>
                <div>Serenity</div>
                <div id="serenity-status">Not Found</div>
            </div>
            <div class="tile not-found" id="lunaro">
                <div>⚽</div>
                <div>Lunaro</div>
                <div id="lunaro-status">Not Found</div>
            </div>
            <div class="tile not-found" id="ramp">
                <div>🏠</div>
                <div>Ramp</div>
                <div id="ramp-status">Not Found</div>
            </div>
        </div>
        
        <div class="refresh-info">
            Auto-refreshes every 0.5 seconds
        </div>
    </div>

    <script>
        function updateDisplay(data) {
            // Update status
            document.getElementById('status-text').textContent = data.status;
            document.getElementById('status').style.background = data.status_color === 'red' ? 
                'linear-gradient(45deg, #f44336, #d32f2f)' :
                data.status_color === 'green' ? 
                'linear-gradient(45deg, #4CAF50, #45a049)' :
                data.status_color === 'yellow' ? 
                'linear-gradient(45deg, #ff9800, #f57c00)' :
                'linear-gradient(45deg, #2196F3, #1976D2)';
            
            // Update mission info
            document.getElementById('mission-status').textContent = data.mission_status;
            document.getElementById('attempts').textContent = `Attempts: ${data.attempts}`;
            
            // Update tiles
            const tiles = ['hangar', 'park', 'serenity', 'lunaro', 'ramp'];
            tiles.forEach(tile => {
                const element = document.getElementById(tile);
                const statusElement = document.getElementById(tile + '-status');
                const found = data.tiles_found.includes(tile);
                
                element.className = `tile ${found ? 'found' : 'not-found'}`;
                statusElement.textContent = found ? 'Found!' : 'Not Found';
            });
        }
        
        function fetchData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDisplay(data))
                .catch(error => {
                    document.getElementById('status-text').textContent = 'Connection error';
                    console.error('Error:', error);
                });
        }
        
        // Initial load and refresh every 500ms for faster updates
        fetchData();
        setInterval(fetchData, 500);
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Get current status from the scanner
            status_data = {
                'status': scanner.get_status_text(),
                'status_color': scanner.get_status_color(),
                'mission_status': scanner.get_mission_status(),
                'attempts': scanner.get_attempts(),
                'tiles_found': scanner.get_tiles_found(),
                'timestamp': time.time()  # Add timestamp for cache busting
            }
            
            self.wfile.write(json.dumps(status_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

class WebScanner:
    def __init__(self):
        # Auto-detect EE.log location
        detected_path = find_ee_log()
        if detected_path:
            self.path = detected_path
            print(f"✅ Auto-detected EE.log at: {self.path}")
        else:
            # Fallback to a default path (will show error if not found)
            system = platform.system()
            if system == 'Windows':
                localappdata = os.getenv('LOCALAPPDATA', '')
                self.path = os.path.join(localappdata, 'Warframe', 'EE.log') if localappdata else 'C:\\Users\\YourUsername\\AppData\\Local\\Warframe\\EE.log'
            elif system == 'Linux':
                self.path = os.path.expanduser('~/.steam/steam/steamapps/compatdata/230410/pfx/drive_c/users/steamuser/AppData/Local/Warframe/EE.log')
            else:  # macOS
                self.path = os.path.expanduser('~/Library/Application Support/Warframe/EE.log')
            print(f"⚠️  Could not auto-detect EE.log, using default path: {self.path}")
            print("💡 Please ensure Warframe has been run at least once to generate EE.log")
        
        self.status_text = 'Awaiting Cascade...'
        self.status_color = 'red'
        self.mission_status = 'Awaiting mission...'
        self.attempts = 0
        self.tiles_found = []
        self.running = True
        
    def get_status_text(self):
        return self.status_text
        
    def get_status_color(self):
        return self.status_color
        
    def get_mission_status(self):
        return self.mission_status
        
    def get_attempts(self):
        return self.attempts
        
    def get_tiles_found(self):
        return self.tiles_found
        
    def update_status(self, text, color):
        self.status_text = text
        self.status_color = color
        
    def update_mission(self, status, attempts):
        self.mission_status = status
        self.attempts = attempts
        
    def update_tiles(self, tiles):
        self.tiles_found = tiles
        
    def follow(self, thefile, mission_active=False):
        """Follow a file like tail -f"""
        thefile.seek(0, 2)
        buffer = ''
        while self.running:
            line = thefile.readline()
            if not line:
                if mission_active:
                    time.sleep(0.01)  # 10ms during mission
                else:
                    time.sleep(0.1)  # 100ms when waiting
                continue
            buffer += line
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                yield line
                
    def track_tiles(self):
        """Main scanning logic"""
        if not os.path.isfile(self.path):
            print('❌ Log file not found at:', self.path)
            return
            
        print("🌐 Web Scanner started - Open http://localhost:8080 in your browser")
        print("🔍 Starting to monitor log file...")
        
        with open(self.path, encoding='utf8', errors='ignore') as logfile:
            searching = False
            attempts = 0
            hidden = False
            tile_matches = set()
            line_count = 0
            last_activity = time.time()
            mission_active = False
            mission_ended = False  # Flag to track if mission already ended
            
            print("🔄 Starting real-time log monitoring...")
            print("📝 Watching for new log entries...")
            
            loglines = self.follow(logfile, mission_active)
            
            for line in loglines:
                line_count += 1
                current_time = time.time()
                
                # Show activity every 30 seconds when not in mission, every 5 seconds during mission
                activity_interval = 5 if mission_active else 30
                if current_time - last_activity > activity_interval:
                    status = "🚀 FAST MONITORING" if mission_active else "📊 Monitoring"
                    print(f"{status}... (processed {line_count} lines)")
                    last_activity = current_time
                
                # Tile detection
                if re.search('\\[IntShuttleBayBackdrop\\]', line, re.IGNORECASE):
                    tile_matches.add('hangar')
                    print(f"🎯 DETECTED: Hangar tile")
                if re.search('\\[IntParkBackdrop\\]', line, re.IGNORECASE):
                    tile_matches.add('park')
                    print(f"🎯 DETECTED: Park tile")
                if re.search('\\[IntParkBBackdrop\\]', line, re.IGNORECASE):
                    tile_matches.add('serenity')
                    print(f"🎯 DETECTED: Serenity tile")
                if re.search('\\[IntLunaroCourtBackdrop\\]', line, re.IGNORECASE):
                    tile_matches.add('lunaro')
                    print(f"🎯 DETECTED: Lunaro tile")
                if re.search('\\[IntLivingQuartersBackdrop\\]', line, re.IGNORECASE):
                    tile_matches.add('ramp')
                    print(f"🎯 DETECTED: Ramp tile")
                
                # Mission detection
                if '/Lotus/Levels/Proc/Zariman/ZarimanDirectionalSurvival generating layout' in line:
                    if not mission_active:  # Only increment when starting a new mission
                        attempts += 1
                    searching = True
                    tile_matches.clear()
                    mission_active = True
                    mission_ended = False  # Reset mission ended flag
                    print(f'🎮 [Attempt {attempts}] Zariman mission started!')
                    print("🚀 SWITCHING TO FAST MONITORING MODE!")
                    self.update_mission("Mission Active", attempts)
                    self.update_status("Mission Active - Looking for tiles...", "blue")
                    loglines = self.follow(logfile, mission_active)
                    
                if not searching and ('/Lotus/Levels/Proc/TheNewWar/PartTwo/TNWDrifterCampMain' in line or '/Lotus/Levels/Proc/PlayerShip' in line):
                    if not mission_ended:  # Only show message once per mission
                        mission_ended = True  # Set flag to prevent multiple messages
                        print(f"🏁 Mission ended - Attempt {attempts} completed")
                    tile_matches.clear()
                    mission_active = False
                    self.update_mission("Mission Ended", attempts)
                    self.update_status("Awaiting Cascade...", "red")
                    loglines = self.follow(logfile, mission_active)
                
                # Update web interface with current tiles (immediate update)
                self.update_tiles(list(tile_matches))
                
                # Determine status based on tiles found
                if 'hangar' in tile_matches and ('lunaro' in tile_matches or 'ramp' in tile_matches) and ('park' in tile_matches or 'serenity' in tile_matches):
                    park_type = 'Park' if 'park' in tile_matches else 'Serenity'
                    living_type = 'Lunaro' if 'lunaro' in tile_matches else 'Ramp'
                    self.update_status(f'Tiles Found: (A) Hangar + {park_type} + {living_type}', 'cyan')
                elif 'hangar' in tile_matches and ('park' in tile_matches or 'serenity' in tile_matches):
                    park_type = 'Park' if 'park' in tile_matches else 'Serenity'
                    self.update_status(f'Tiles Found: (A) Hangar + {park_type}', 'cyan')
                elif 'hangar' in tile_matches and ('lunaro' in tile_matches or 'ramp' in tile_matches):
                    living_type = 'Lunaro' if 'lunaro' in tile_matches else 'Ramp'
                    self.update_status(f'Tiles Found: (B) Hangar + {living_type}', 'green')
                elif 'hangar' in tile_matches:
                    self.update_status('Tile Found: (B) Hangar', 'green')
                elif ('park' in tile_matches or 'serenity' in tile_matches) and ('lunaro' in tile_matches or 'ramp' in tile_matches):
                    park_type = 'Park' if 'park' in tile_matches else 'Serenity'
                    living_type = 'Lunaro' if 'lunaro' in tile_matches else 'Ramp'
                    self.update_status(f'Tiles Found: (C) {park_type} + {living_type}', 'yellow')
                elif 'park' in tile_matches or 'serenity' in tile_matches:
                    park_type = 'Park' if 'park' in tile_matches else 'Serenity'
                    self.update_status(f'Tile Found: (C) {park_type}', 'yellow')
                elif 'lunaro' in tile_matches or 'ramp' in tile_matches:
                    living_type = 'Lunaro' if 'lunaro' in tile_matches else 'Ramp'
                    self.update_status(f'Tile Found: (D) {living_type}', 'red')
                    
                if 'Level loader: LS_POST_CREATE -> LS_COMPLETE' in line and not tile_matches:
                    self.update_status('No tiles found!', 'red')
                    print("❌ No tiles found in this mission!")
                    
                if attempts >= 1 and ('Zariman Survival (Void Cascade): State Change: ENDLESS' in line or 'ZarimanSurvivalMission.lua: ModeState = 4' in line or 'ZarimanSurvivalMission.lua: Cleansing SurvivalLifeSupportPillarCorruptible' in line):
                    tile_matches.clear()
                    self.update_tiles([])

def main():
    global scanner
    scanner = WebScanner()
    
    # Start the web server (0.0.0.0 allows access from network devices)
    server = HTTPServer(('0.0.0.0', 9000), WebHandler)
    print("🌐 Web server starting on http://localhost:9000")
    print("🌐 Network access: http://<your-ip>:9000")
    print("💡 To find your IP: Run 'ip addr' or 'ifconfig' in terminal")
    
    # Start the scanner in a separate thread
    scanner_thread = threading.Thread(target=scanner.track_tiles, daemon=True)
    scanner_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web scanner...")
        scanner.running = False
        server.shutdown()

if __name__ == "__main__":
    main()
