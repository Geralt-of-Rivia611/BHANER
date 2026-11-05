from __future__ import annotations

import sys
import os
import json
import socket
import threading
import time
import webbrowser
import queue
import urllib.request
import urllib.parse
import subprocess
import re
import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# --- APP CONFIGURATION ---
APP_VERSION = "1.6.0"
GITHUB_REPO = "Geralt-of-Rivia611/BHANER"

if sys.platform == "win32":
    APP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "bhaner")
else:
    APP_DIR = os.path.join(os.path.expanduser("~"), ".bhaner")

os.makedirs(APP_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APP_DIR, "bhaner_config.json")
THEMES_DIR = os.path.join(APP_DIR, "themes")
FONTS_DIR = os.path.join(THEMES_DIR, "fonts")
SESSIONS_DIR = os.path.join(APP_DIR, "sessions")

os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

SESSION_FILENAME = os.path.join(
    SESSIONS_DIR, 
    f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

def log_session_event(action: str, content: str = "", extra: str = ""):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{action.upper()}]"
        if extra:
            log_line += f" ({extra})"
        if content:
            sanitized = content.replace("\r", "").replace("\n", " \\n ")
            log_line += f" -> {sanitized}"
        log_line += "\n"

        with open(SESSION_FILENAME, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

log_session_event("SESSION_START", f"bhaner v{APP_VERSION} initialized")

# Core Themes
BUILTIN_PRESETS = {
    "p1": {
        "id": "p1",
        "name": "P1: Flame (Orange Stage)",
        "font_family": "'Impact', 'Arial Black', sans-serif",
        "google_font_url": "",
        "font_file": "",
        "text_transform": "uppercase",
        "letter_spacing": "0px",
        "text_color": "#FFFFFF",
        "text_shadow": "-3px -3px 0 #5C1B03, 3px -3px 0 #5C1B03, -3px 3px 0 #5C1B03, 3px 3px 0 #5C1B03, -5px 0 0 #5C1B03, 5px 0 0 #5C1B03, 0 -5px 0 #5C1B03, 0 5px 0 #5C1B03, 0 8px 25px rgba(0,0,0,0.95)",
        "container_background": "transparent",
        "impact_zoom": {
            "scale": 1.18,
            "text_color": "#FF6200",
            "text_shadow": "-4px -4px 0 #FFF, 4px -4px 0 #FFF, -4px 4px 0 #FFF, 4px 4px 0 #FFF, 0 0 40px rgba(255,98,0,0.9)"
        }
    },
    "p2": {
        "id": "p2",
        "name": "P2: Ocean Punch (Cyan Swirl)",
        "font_family": "'Impact', 'Arial Black', sans-serif",
        "google_font_url": "",
        "font_file": "",
        "text_transform": "uppercase",
        "letter_spacing": "0px",
        "text_color": "#FF6200",
        "text_shadow": "-4px -4px 0 #000, 4px -4px 0 #000, -4px 4px 0 #000, 4px 4px 0 #000, -6px 0 0 #000, 6px 0 0 #000, 0 -6px 0 #000, 0 6px 0 #000, 0 0 35px rgba(255,98,0,0.95)",
        "container_background": "transparent",
        "impact_zoom": {
            "scale": 1.18,
            "text_color": "#FFFFFF",
            "text_shadow": "-4px -4px 0 #FF6200, 4px -4px 0 #FF6200, -4px 4px 0 #FF6200, 4px 4px 0 #FF6200, 0 0 40px #FFF"
        }
    },
    "p3": {
        "id": "p3",
        "name": "P3: Core Flare Shield (Hotspot)",
        "font_family": "'Impact', 'Arial Black', sans-serif",
        "google_font_url": "",
        "font_file": "",
        "text_transform": "uppercase",
        "letter_spacing": "0px",
        "text_color": "#FFFFFF",
        "text_shadow": "-5px -5px 0 #000, 5px -5px 0 #000, -5px 5px 0 #000, 5px 5px 0 #000, 0 0 30px rgba(255,98,0,0.8)",
        "container_background": "radial-gradient(ellipse at center, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 65%, transparent 100%)",
        "impact_zoom": {
            "scale": 1.18,
            "text_color": "#FF6200",
            "text_shadow": "-5px -5px 0 #000, 5px -5px 0 #000, -5px 5px 0 #000, 5px 5px 0 #000, 0 0 50px #FF6200"
        }
    },
    "p4": {
        "id": "p4",
        "name": "P4: Cyber Cyan Modern",
        "font_family": "'Segoe UI Black', 'Arial Black', sans-serif",
        "google_font_url": "",
        "font_file": "",
        "text_transform": "uppercase",
        "letter_spacing": "2px",
        "text_color": "#FFFFFF",
        "text_shadow": "-3px -3px 0 #032127, 3px -3px 0 #032127, -3px 3px 0 #032127, 3px 3px 0 #032127, 0 0 25px rgba(0,242,254,0.9)",
        "container_background": "transparent",
        "impact_zoom": {
            "scale": 1.18,
            "text_color": "#00F2FE",
            "text_shadow": "0 0 35px #00F2FE, -4px -4px 0 #000, 4px -4px 0 #000"
        }
    },
    "p5": {
        "id": "p5",
        "name": "P5: Minimalist White Lumen",
        "font_family": "'Arial Black', sans-serif",
        "google_font_url": "",
        "font_file": "",
        "text_transform": "uppercase",
        "letter_spacing": "0px",
        "text_color": "#FFFFFF",
        "text_shadow": "0 4px 20px rgba(0,0,0,0.95), 0 0 10px rgba(0,0,0,0.8)",
        "container_background": "transparent",
        "impact_zoom": {
            "scale": 1.18,
            "text_color": "#FFFFFF",
            "text_shadow": "0 0 40px rgba(255,255,255,0.9), 0 4px 20px #000"
        }
    }
}

def load_theme_files() -> dict[str, dict]:
    themes = {}
    if os.path.exists(THEMES_DIR):
        for item in sorted(os.listdir(THEMES_DIR)):
            if item.endswith(".json"):
                path = os.path.join(THEMES_DIR, item)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        tid = data.get("id", os.path.splitext(item)[0])
                        themes[tid] = data
                except Exception:
                    pass
    return themes

DISK_THEMES = load_theme_files()

def load_config() -> dict:
    default_cfg = {
        "favorite_mode": "p1",
        "active_custom_slot": "slot_a",
        "slots": {
            "slot_a": "festival_gold",
            "slot_b": "",
            "slot_c": ""
        },
        "clear_hotkey": "Shift_R",
        "active_bg_preset": "b1",
        "bg_presets": {
            "b1": "transparent",
            "b2": "",
            "b3": ""
        },
        "burst_mode": "single",
        "burst_bpm": 130
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg

def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

CONFIG = load_config()

def sanitize_color_input(raw: str) -> str:
    s = raw.strip()
    if not s:
        return ""
    nums = re.findall(r'[-+]?[0-9]*\.?[0-9]+', s)
    if len(nums) == 3 and not s.lower().startswith(('rgb', 'hsl', '#')):
        return f"rgb({nums[0]}, {nums[1]}, {nums[2]})"
    elif len(nums) == 4 and not s.lower().startswith(('rgba', 'hsl', '#')):
        return f"rgba({nums[0]}, {nums[1]}, {nums[2]}, {nums[3]})"
    if re.fullmatch(r'[0-9a-fA-F]{3,8}', s):
        if len(s) in (3, 4, 6, 8):
            return f"#{s}"
    return s

def get_current_background() -> str:
    active_bg = CONFIG.get("active_bg_preset", "b1")
    val = CONFIG.get("bg_presets", {}).get(active_bg, "")
    val = sanitize_color_input(val)
    if active_bg == "b1" or not val:
        return "transparent"
    return val

def resolve_theme(mode: str, custom_slot: str) -> dict:
    base_theme = {}
    if mode in BUILTIN_PRESETS:
        base_theme = dict(BUILTIN_PRESETS[mode])
    elif mode == "custom":
        assigned_id = CONFIG.get("slots", {}).get(custom_slot, "")
        if assigned_id in DISK_THEMES:
            base_theme = dict(DISK_THEMES[assigned_id])
        elif DISK_THEMES:
            base_theme = dict(next(iter(DISK_THEMES.values())))
        else:
            base_theme = dict(BUILTIN_PRESETS["p1"])
    else:
        base_theme = dict(BUILTIN_PRESETS["p1"])

    active_bg = CONFIG.get("active_bg_preset", "b1")
    if active_bg != "b1":
        base_theme["container_background"] = get_current_background()

    return base_theme

def find_free_port(preferred: int = 8000) -> int:
    for p in [preferred, 8080, 8888, 5000, 0]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', p))
                return s.getsockname()[1]
            except OSError:
                continue
    return preferred

ACTIVE_PORT = find_free_port(8000)

current_mode = CONFIG.get("favorite_mode", "p1")
current_custom_slot = CONFIG.get("active_custom_slot", "slot_a")

current_state = {
    "text": "",
    "zoom": False,
    "theme": resolve_theme(current_mode, current_custom_slot),
    "burst_mode": CONFIG.get("burst_mode", "single"),
    "burst_bpm": CONFIG.get("burst_bpm", 130)
}
state_lock = threading.Lock()
clients_queues = set()
clients_lock = threading.Lock()

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>bhaner - Stage Projection</title>
  <link id="google-font-link" rel="stylesheet" href="">
  <style id="dynamic-font-face"></style>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    html, body {{
      width: 100vw;
      height: 100vh;
      background: #000000;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: background 0.25s ease;
    }}

    #corner-brand {{
      position: absolute;
      top: 3.5vh;
      right: 4vw;
      width: 6.5vw;
      min-width: 60px;
      opacity: 0.85;
      filter: drop-shadow(0 0 10px rgba(92, 27, 3, 0.9));
      z-index: 10;
      pointer-events: none;
    }}

    #display-container {{
      width: 88vw;
      height: 72vh;
      margin-bottom: 8vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      position: relative;
    }}

    #projector-text {{
      word-wrap: break-word;
      line-height: 1.05;
      white-space: pre-wrap;
      max-width: 100%;
      transform-origin: center center;
      transition: transform 0.12s ease-out, color 0.15s ease, text-shadow 0.15s ease;
    }}

    #mic-perm-banner {{
      position: absolute;
      bottom: 15px;
      padding: 8px 16px;
      background: rgba(255, 98, 0, 0.25);
      border: 1px solid #FF6200;
      color: #FFF;
      font-family: sans-serif;
      font-size: 13px;
      border-radius: 6px;
      cursor: pointer;
      display: none;
      z-index: 999;
    }}

    /* CSS Keyframe Burst Patterns */
    @keyframes strobeAnim {{
      0%, 100% {{ transform: scale(1.0); }}
      50% {{ transform: scale(var(--burst-scale, 1.2)); }}
    }}

    @keyframes breatheAnim {{
      0%, 100% {{ transform: scale(0.96); filter: brightness(0.9); }}
      50% {{ transform: scale(var(--burst-scale, 1.2)); filter: brightness(1.25); }}
    }}

    @keyframes heartbeatAnim {{
      0%, 100% {{ transform: scale(1.0); }}
      15% {{ transform: scale(var(--burst-scale, 1.22)); }}
      30% {{ transform: scale(1.05); }}
      45% {{ transform: scale(calc(var(--burst-scale, 1.22) * 1.08)); }}
      60% {{ transform: scale(1.0); }}
    }}

    .anim-strobe {{
      animation: strobeAnim var(--burst-period, 0.46s) infinite ease-in-out;
    }}
    .anim-breathe {{
      animation: breatheAnim var(--burst-period, 1.84s) infinite ease-in-out;
    }}
    .anim-heartbeat {{
      animation: heartbeatAnim var(--burst-period, 0.92s) infinite cubic-bezier(0.215, 0.61, 0.355, 1);
    }}
  </style>
</head>
<body>
  <div id="corner-brand">
    <svg viewBox="0 0 100 70" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 65L48 20H32L6 65H22Z" fill="#FF6200"/>
      <path d="M48 65L74 20H58L32 65H48Z" fill="#FFFFFF"/>
      <path d="M74 65L100 20H84L58 65H74Z" fill="#FF6200"/>
    </svg>
  </div>

  <div id="display-container">
    <div id="projector-text"></div>
  </div>

  <div id="mic-perm-banner" onclick="initMic()">🎤 Click to Enable Live Venue Mic Pulse</div>

  <script>
    const textEl = document.getElementById('projector-text');
    const container = document.getElementById('display-container');
    const googleFontLink = document.getElementById('google-font-link');
    const dynamicFontFace = document.getElementById('dynamic-font-face');
    const micBanner = document.getElementById('mic-perm-banner');

    let activeTheme = {{}};
    let isZoomed = false;
    let burstMode = 'single';
    let burstBpm = 130;

    // Web Audio State
    let audioCtx = null;
    let analyser = null;
    let dataArray = null;
    let micStream = null;
    let micAnimationId = null;

    function applyTheme(theme) {{
      activeTheme = theme;

      if (theme.google_font_url && theme.google_font_url.trim()) {{
        googleFontLink.href = theme.google_font_url;
      }} else {{
        googleFontLink.removeAttribute('href');
      }}

      if (theme.font_file && theme.font_file.trim()) {{
        dynamicFontFace.innerHTML = `
          @font-face {{
            font-family: 'LocalCustomFont';
            src: url('/fonts/${{encodeURIComponent(theme.font_file)}}');
          }}
        `;
        textEl.style.fontFamily = `'LocalCustomFont', ${{theme.font_family || 'sans-serif'}}`;
      }} else {{
        dynamicFontFace.innerHTML = '';
        textEl.style.fontFamily = theme.font_family || 'Impact, sans-serif';
      }}

      textEl.style.textTransform = theme.text_transform || 'uppercase';
      textEl.style.letterSpacing = theme.letter_spacing || '0px';

      const bg = theme.container_background || 'transparent';
      document.body.style.background = (bg === 'transparent') ? '#000000' : bg;

      applyVisualState();
    }}

    function clearAnimations() {{
      textEl.classList.remove('anim-strobe', 'anim-breathe', 'anim-heartbeat');
      if (micAnimationId) {{
        cancelAnimationFrame(micAnimationId);
        micAnimationId = null;
      }}
    }}

    function applyVisualState() {{
      if (!activeTheme || !activeTheme.text_color) return;

      clearAnimations();

      if (!isZoomed) {{
        textEl.style.transform = 'scale(1.0)';
        textEl.style.color = activeTheme.text_color;
        textEl.style.textShadow = activeTheme.text_shadow;
        micBanner.style.display = 'none';
        return;
      }}

      // Zoom punch is Active: compute period from BPM
      const periodSec = 60 / Math.max(40, Math.min(240, burstBpm));
      const targetScale = (activeTheme.impact_zoom && activeTheme.impact_zoom.scale) ? activeTheme.impact_zoom.scale : 1.2;
      
      textEl.style.setProperty('--burst-scale', targetScale);
      textEl.style.color = (activeTheme.impact_zoom && activeTheme.impact_zoom.text_color) || activeTheme.text_color;
      textEl.style.textShadow = (activeTheme.impact_zoom && activeTheme.impact_zoom.text_shadow) || activeTheme.text_shadow;

      if (burstMode === 'strobe') {{
        textEl.style.setProperty('--burst-period', periodSec + 's');
        textEl.classList.add('anim-strobe');
      }} else if (burstMode === 'breathe') {{
        textEl.style.setProperty('--burst-period', (periodSec * 4) + 's');
        textEl.classList.add('anim-breathe');
      }} else if (burstMode === 'heartbeat') {{
        textEl.style.setProperty('--burst-period', (periodSec * 2) + 's');
        textEl.classList.add('anim-heartbeat');
      }} else if (burstMode === 'mic') {{
        if (!audioCtx) {{
          micBanner.style.display = 'block';
        }} else {{
          startMicPulse(targetScale);
        }}
      }} else {{
        // 'single' / default static punch
        textEl.style.transform = `scale(${{targetScale}})`;
      }}
    }}

    async function initMic() {{
      try {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        micStream = await navigator.mediaDevices.getUserMedia({{ audio: true, video: false }});
        const source = audioCtx.createMediaStreamSource(micStream);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        micBanner.style.display = 'none';
        applyVisualState();
      }} catch (err) {{
        alert("Microphone access unavailable or denied: " + err.message);
      }}
    }}

    function startMicPulse(maxScale) {{
      if (!analyser || !dataArray) return;

      function renderFrame() {{
        if (!isZoomed || burstMode !== 'mic') return;
        analyser.getByteFrequencyData(dataArray);

        // Sub-bass & low mids focus (bins 1 to 8: roughly 30Hz - 250Hz)
        let lowEnergy = 0;
        const bins = 8;
        for (let i = 1; i <= bins; i++) {{
          lowEnergy += dataArray[i];
        }}
        const avg = lowEnergy / bins; // 0 to 255
        const norm = Math.min(1.0, Math.max(0.0, (avg - 30) / 180)); // threshold floor
        const dynamicScale = 1.0 + norm * (maxScale - 1.0);

        textEl.style.transform = `scale(${{dynamicScale.toFixed(3)}})`;
        micAnimationId = requestAnimationFrame(renderFrame);
      }}
      renderFrame();
    }}

    function autoFitText() {{
      const text = textEl.innerText.trim();
      if (!text) {{
        textEl.style.fontSize = '12px';
        return;
      }}

      textEl.style.transform = 'scale(1.0)';

      let min = 14, max = 360, best = 14;
      const targetW = container.clientWidth;
      const targetH = container.clientHeight;

      while (min <= max) {{
        const mid = Math.floor((min + max) / 2);
        textEl.style.fontSize = mid + 'px';
        
        if (textEl.scrollWidth <= targetW && textEl.scrollHeight <= targetH) {{
          best = mid;
          min = mid + 1;
        }} else {{
          max = mid - 1;
        }}
      }}
      textEl.style.fontSize = best + 'px';
      applyVisualState();
    }}

    function handlePayload(data) {{
      if (data.burst_mode !== undefined) burstMode = data.burst_mode;
      if (data.burst_bpm !== undefined) burstBpm = data.burst_bpm;

      if (data.theme) {{
        applyTheme(data.theme);
      }}

      isZoomed = !!data.zoom;
      const currentText = textEl.innerText.trim();
      const incomingText = (data.text || '').trim();

      if (incomingText !== currentText) {{
        textEl.innerText = incomingText;
        autoFitText();
      }} else {{
        applyVisualState();
      }}
    }}

    const evtSource = new EventSource('/stream');
    evtSource.onmessage = (event) => {{
      try {{
        const payload = JSON.parse(event.data);
        handlePayload(payload);
      }} catch (err) {{}}
    }};

    window.addEventListener('resize', autoFitText);
  </script>
</body>
</html>
"""

class FastThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class RobustServerHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            content = HTML_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(content)
            self.wfile.flush()

        elif self.path.startswith('/fonts/'):
            filename = urllib.parse.unquote(self.path[len('/fonts/'):])
            font_path = os.path.join(FONTS_DIR, os.path.basename(filename))
            if os.path.isfile(font_path):
                ext = os.path.splitext(font_path)[1].lower()
                mime = 'font/otf' if ext == '.otf' else 'font/ttf'
                with open(font_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
            else:
                self.send_response(404)
                self.end_headers()

        elif self.path == '/stream':
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            q = queue.Queue()
            with state_lock:
                initial_msg = json.dumps(current_state)
            
            self.wfile.write(f"data: {initial_msg}\n\n".encode('utf-8'))
            self.wfile.flush()

            with clients_lock:
                clients_queues.add(q)

            try:
                while True:
                    try:
                        msg = q.get(timeout=10.0)
                        self.wfile.write(f"data: {msg}\n\n".encode('utf-8'))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with clients_lock:
                    clients_queues.discard(q)
        else:
            self.send_response(404)
            self.end_headers()

def broadcast_payload(payload: dict):
    with state_lock:
        for k, v in payload.items():
            current_state[k] = v

    msg = json.dumps(current_state)
    with clients_lock:
        for q in list(clients_queues):
            q.put(msg)

def run_server():
    server = FastThreadingHTTPServer(('127.0.0.1', ACTIVE_PORT), RobustServerHandler)
    server.serve_forever()

# --- OPERATOR GUI (DESKTOP CONTROLLER) ---
class OperatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"bhaner Controller v{APP_VERSION}")
        self.root.geometry("570x740")
        self.root.minsize(530, 680)

        self.last_pushed_text = ""
        self.is_zoomed = False

        self.preset_var = tk.StringVar(value=CONFIG.get("favorite_mode", "p1"))
        self.custom_slot_var = tk.StringVar(value=CONFIG.get("active_custom_slot", "slot_a"))
        self.bg_preset_var = tk.StringVar(value=CONFIG.get("active_bg_preset", "b1"))

        # --- 1. Visual Presets Frame ---
        preset_frame = ttk.LabelFrame(root, text=" Visual Presets (Quick-Switch: F1 - F6) ", padding=8)
        preset_frame.pack(fill="x", padx=15, pady=3)

        self.presets = [
            ("P1: Flame (Orange Stage)", "p1"),
            ("P2: Ocean Punch (Cyan Swirl)", "p2"),
            ("P3: Core Flare Shield", "p3"),
            ("P4: Cyber Cyan", "p4"),
            ("P5: Minimal White", "p5"),
            ("P6: Custom (3 User Slots)", "custom")
        ]

        preset_grid = ttk.Frame(preset_frame)
        preset_grid.pack(fill="x")

        for idx, (label, pid) in enumerate(self.presets):
            rb = ttk.Radiobutton(preset_grid, text=label, value=pid, variable=self.preset_var, command=self.on_preset_change)
            rb.grid(row=idx // 2, column=idx % 2, sticky="w", padx=6, pady=2)
            self.root.bind(f"<F{idx+1}>", lambda e, p=pid: self.set_preset(p))

        # Custom Options Sub-Panel
        self.custom_box = ttk.LabelFrame(preset_frame, text=" Custom Preset Configuration (Slot A / B / C) ", padding=6)
        self.custom_box.pack(fill="x", pady=3)

        slot_row = ttk.Frame(self.custom_box)
        slot_row.pack(fill="x", pady=2)

        ttk.Label(slot_row, text="Active Slot:").pack(side="left", padx=4)
        for s_code, s_label in [("slot_a", "Slot A"), ("slot_b", "Slot B"), ("slot_c", "Slot C")]:
            ttk.Radiobutton(slot_row, text=s_label, value=s_code, variable=self.custom_slot_var, command=self.on_slot_change).pack(side="left", padx=8)

        assign_row = ttk.Frame(self.custom_box)
        assign_row.pack(fill="x", pady=3)

        ttk.Label(assign_row, text="Theme:").pack(side="left", padx=4)
        self.theme_combo_var = tk.StringVar()
        self.theme_combobox = ttk.Combobox(assign_row, textvariable=self.theme_combo_var, state="readonly", width=16)
        self.theme_combobox.pack(side="left", padx=3)

        ttk.Button(assign_row, text="Assign", width=7, command=self.assign_theme_to_current_slot).pack(side="left", padx=2)
        ttk.Button(assign_row, text="Import Font", width=11, command=self.import_google_font_dialog).pack(side="left", padx=2)
        ttk.Button(assign_row, text="Reload", width=7, command=self.reload_themes).pack(side="left", padx=2)

        fav_frame = ttk.Frame(preset_frame)
        fav_frame.pack(fill="x", pady=2)
        self.fav_status_label = ttk.Label(fav_frame, text=self.get_fav_label(), font=("Segoe UI", 9, "bold"))
        self.fav_status_label.pack(side="left", padx=4)

        ttk.Button(fav_frame, text="Set as Default", command=self.save_as_favorite).pack(side="right", padx=4)

        # --- 2. Burst Patterns & Therapeutic Rave Engine ---
        burst_frame = ttk.LabelFrame(root, text=" Rave Burst Pattern (Double-Tap Punch) ", padding=8)
        burst_frame.pack(fill="x", padx=15, pady=3)

        burst_row = ttk.Frame(burst_frame)
        burst_row.pack(fill="x")

        ttk.Label(burst_row, text="Pattern:").pack(side="left", padx=4)

        self.burst_options = [
            ("Single Impact (Off)", "single"),
            ("BPM Strobe (High Rave)", "strobe"),
            ("Hypnotic Breathe (Therapeutic)", "breathe"),
            ("Shamanic Heartbeat (Grounding)", "heartbeat"),
            ("Live Mic / Audio Pulse", "mic")
        ]
        self.burst_var = tk.StringVar(value=CONFIG.get("burst_mode", "single"))
        self.burst_combo = ttk.Combobox(
            burst_row, 
            values=[opt[0] for opt in self.burst_options], 
            state="readonly", 
            width=26
        )
        # Match initial index
        init_idx = 0
        for i, opt in enumerate(self.burst_options):
            if opt[1] == self.burst_var.get():
                init_idx = i
                break
        self.burst_combo.current(init_idx)
        self.burst_combo.pack(side="left", padx=4)
        self.burst_combo.bind("<<ComboboxSelected>>", self.on_burst_selected)

        # Tempo / BPM Dial
        ttk.Label(burst_row, text="|  Tempo:").pack(side="left", padx=(10, 4))
        self.bpm_var = tk.IntVar(value=CONFIG.get("burst_bpm", 130))
        self.bpm_label = ttk.Label(burst_row, text=f"{self.bpm_var.get()} BPM", width=8)
        self.bpm_label.pack(side="right", padx=2)

        self.bpm_scale = ttk.Scale(
            burst_row, 
            from_=60, 
            to_=180, 
            variable=self.bpm_var, 
            orient="horizontal", 
            command=self.on_bpm_change
        )
        self.bpm_scale.pack(side="right", fill="x", expand=True, padx=4)

        # --- 3. Background Presets Frame (B1, B2, B3) ---
        bg_frame = ttk.LabelFrame(root, text=" Background Presets (Hex / RGB / RGBA) ", padding=8)
        bg_frame.pack(fill="x", padx=15, pady=3)

        bg_row = ttk.Frame(bg_frame)
        bg_row.pack(fill="x")

        ttk.Radiobutton(bg_row, text="B1: Transparent", value="b1", variable=self.bg_preset_var, command=self.on_bg_preset_change).pack(side="left", padx=3)

        ttk.Radiobutton(bg_row, text="B2:", value="b2", variable=self.bg_preset_var, command=self.on_bg_preset_change).pack(side="left", padx=(10, 2))
        self.b2_val_var = tk.StringVar(value=CONFIG.get("bg_presets", {}).get("b2", ""))
        self.b2_entry = ttk.Entry(bg_row, textvariable=self.b2_val_var, width=13)
        self.b2_entry.pack(side="left", padx=2)
        self.b2_val_var.trace_add("write", lambda *args: self.on_bg_text_changed("b2", self.b2_val_var.get()))

        ttk.Radiobutton(bg_row, text="B3:", value="b3", variable=self.bg_preset_var, command=self.on_bg_preset_change).pack(side="left", padx=(10, 2))
        self.b3_val_var = tk.StringVar(value=CONFIG.get("bg_presets", {}).get("b3", ""))
        self.b3_entry = ttk.Entry(bg_row, textvariable=self.b3_val_var, width=13)
        self.b3_entry.pack(side="left", padx=2)
        self.b3_val_var.trace_add("write", lambda *args: self.on_bg_text_changed("b3", self.b3_val_var.get()))

        # --- 4. Transmission Mode & Fast Clear ---
        mode_frame = ttk.LabelFrame(root, text=" Transmission Mode & Fast Clear ", padding=8)
        mode_frame.pack(fill="x", padx=15, pady=3)

        mode_row = ttk.Frame(mode_frame)
        mode_row.pack(fill="x")

        self.mode_var = tk.StringVar(value="live")
        ttk.Radiobutton(mode_row, text="Live Mode", value="live", variable=self.mode_var, command=self.on_mode_change).pack(side="left", padx=4)
        ttk.Radiobutton(mode_row, text="Batch Mode", value="batch", variable=self.mode_var, command=self.on_mode_change).pack(side="left", padx=8)

        ttk.Label(mode_row, text="|  Clear Hotkey:").pack(side="left", padx=(10, 4))

        self.current_bound_key = CONFIG.get("clear_hotkey", "Shift_R")
        self.is_recording_key = False

        self.bind_btn = ttk.Button(mode_row, text=self.format_key_name(self.current_bound_key), width=14, command=self.start_key_recording)
        self.bind_btn.pack(side="left", padx=2)

        self.bind_clear_hotkey(self.current_bound_key)

        # --- 5. Content Input ---
        input_frame = ttk.LabelFrame(root, text=" Screen Content ", padding=8)
        input_frame.pack(fill="both", expand=True, padx=15, pady=3)

        self.text_input = tk.Text(input_frame, wrap="word", font=("Segoe UI", 12), height=4)
        self.text_input.pack(fill="both", expand=True)

        self.text_input.bind("<<Modified>>", self.on_modified)
        self.text_input.bind("<Return>", self.on_return_pressed)

        # Control Buttons
        btn_frame = ttk.Frame(root, padding=8)
        btn_frame.pack(fill="x", padx=15)

        self.push_btn = ttk.Button(btn_frame, text="Push Content (Enter)", command=self.push_batch_content)
        self.push_btn.pack(side="left", padx=4)

        self.clear_btn = ttk.Button(btn_frame, text=f"Clear Screen ({self.format_key_name(self.current_bound_key)})", command=self.clear_all)
        self.clear_btn.pack(side="left", padx=4)

        ttk.Button(btn_frame, text="Re-open Window", command=self.open_browser).pack(side="right", padx=4)
        ttk.Button(btn_frame, text="Sessions", command=self.open_sessions_folder).pack(side="right", padx=4)

        self.update_theme_combobox()
        self.sync_active_slot_display()

        self.root.after(700, self.open_browser)

    # --- Burst Handlers ---
    def on_burst_selected(self, event=None):
        idx = self.burst_combo.current()
        mode_code = self.burst_options[idx][1]
        self.burst_var.set(mode_code)
        CONFIG["burst_mode"] = mode_code
        save_config(CONFIG)

        # Disable slider if mic is active
        if mode_code == "mic":
            self.bpm_scale.state(["disabled"])
            self.bpm_label.config(text="Live Mic")
        else:
            self.bpm_scale.state(["!disabled"])
            self.bpm_label.config(text=f"{int(self.bpm_var.get())} BPM")

        broadcast_payload({"burst_mode": mode_code, "burst_bpm": int(self.bpm_var.get())})
        log_session_event("BURST_MODE_CHANGE", extra=f"{mode_code} @ {int(self.bpm_var.get())} BPM")

    def on_bpm_change(self, val):
        bpm = int(float(val))
        self.bpm_label.config(text=f"{bpm} BPM")
        broadcast_payload({"burst_bpm": bpm})
        CONFIG["burst_bpm"] = bpm
        save_config(CONFIG)

    # --- Interactive Key Binding UI ---
    def format_key_name(self, raw_key: str) -> str:
        key_map = {
            "Shift_R": "Right Shift",
            "Shift_L": "Left Shift",
            "Control_R": "Right Ctrl",
            "Control_L": "Left Ctrl",
            "Escape": "Escape",
            "Delete": "Delete",
            "BackSpace": "Backspace"
        }
        return key_map.get(raw_key, raw_key)

    def start_key_recording(self):
        self.is_recording_key = True
        self.bind_btn.config(text="[Press Any Key]")
        self.root.bind("<KeyPress>", self.record_key_event)

    def record_key_event(self, event):
        if not self.is_recording_key:
            return
        self.is_recording_key = False
        self.root.unbind("<KeyPress>")

        captured_key = event.keysym
        self.bind_clear_hotkey(captured_key)

        CONFIG["clear_hotkey"] = captured_key
        save_config(CONFIG)

        friendly_name = self.format_key_name(captured_key)
        self.bind_btn.config(text=friendly_name)
        self.clear_btn.config(text=f"Clear Screen ({friendly_name})")
        log_session_event("HOTKEY_REBOUND", extra=f"Clear: {captured_key}")

    def bind_clear_hotkey(self, key_name: str):
        if not key_name:
            return
        if hasattr(self, "current_bound_key") and self.current_bound_key:
            try:
                self.root.unbind(f"<{self.current_bound_key}>")
            except Exception:
                pass

        try:
            self.root.bind(f"<{key_name}>", lambda e: self.clear_all())
            self.current_bound_key = key_name
        except Exception:
            self.root.bind("<Shift_R>", lambda e: self.clear_all())
            self.current_bound_key = "Shift_R"

    # --- Live Background Handlers ---
    def on_bg_text_changed(self, preset_key: str, raw_val: str):
        cleaned = sanitize_color_input(raw_val)
        CONFIG.setdefault("bg_presets", {})[preset_key] = cleaned
        save_config(CONFIG)
        if self.bg_preset_var.get() == preset_key:
            self.on_preset_change()

    def on_bg_preset_change(self):
        active_preset = self.bg_preset_var.get()
        CONFIG["active_bg_preset"] = active_preset
        save_config(CONFIG)
        self.on_preset_change()
        log_session_event("BG_PRESET_CHANGE", extra=f"Preset: {active_preset}")

    # --- Preset & Display Handlers ---
    def get_fav_label(self) -> str:
        mode = CONFIG.get("favorite_mode", "p1")
        if mode == "custom":
            slot = CONFIG.get("active_custom_slot", "slot_a")
            theme_id = CONFIG.get("slots", {}).get(slot, "Default")
            return f"[Default]: Custom ({slot.upper()}: {theme_id})"
        return f"[Default]: {BUILTIN_PRESETS.get(mode, {}).get('name', mode.upper())}"

    def update_theme_combobox(self):
        theme_names = [f"{tid}: {data.get('name', tid)}" for tid, data in DISK_THEMES.items()]
        self.theme_combobox['values'] = theme_names

    def sync_active_slot_display(self):
        current_slot = self.custom_slot_var.get()
        assigned_id = CONFIG.get("slots", {}).get(current_slot, "")
        for idx, tid in enumerate(DISK_THEMES.keys()):
            if tid == assigned_id:
                self.theme_combobox.current(idx)
                return
        if DISK_THEMES:
            self.theme_combobox.current(0)

    def set_preset(self, preset_id: str):
        self.preset_var.set(preset_id)
        self.on_preset_change()

    def on_preset_change(self):
        theme = resolve_theme(self.preset_var.get(), self.custom_slot_var.get())
        log_session_event("PRESET_CHANGE", extra=f"Active: {self.preset_var.get()} ({theme.get('name')})")
        broadcast_payload({"theme": theme})

    def on_slot_change(self):
        CONFIG["active_custom_slot"] = self.custom_slot_var.get()
        save_config(CONFIG)
        self.sync_active_slot_display()
        if self.preset_var.get() == "custom":
            self.on_preset_change()

    def assign_theme_to_current_slot(self):
        selected = self.theme_combo_var.get()
        if not selected:
            return
        tid = selected.split(":")[0].strip()
        slot = self.custom_slot_var.get()
        CONFIG.setdefault("slots", {})[slot] = tid
        save_config(CONFIG)
        self.preset_var.set("custom")
        self.on_preset_change()
        mb.showinfo("Slot Saved", f"Assigned '{tid}' to {slot.upper()}.\nSaved to preset memory.")

    def import_google_font_dialog(self):
        url = sd.askstring("Import Google Font", "Paste Google Font CSS URL:\n(e.g., https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap)")
        if not url or not url.strip():
            return
        url = url.strip()

        match = re.search(r'family=([^:&]+)', url)
        raw_name = match.group(1).replace('+', ' ') if match else "CustomFont"

        display_name = sd.askstring("Theme Name", f"Enter a label for this theme:", initialvalue=raw_name)
        if not display_name:
            display_name = raw_name

        slug = re.sub(r'[^a-zA-Z0-9_]', '', display_name.lower().replace(' ', '_'))
        theme_filename = f"{slug}.json"
        target_path = os.path.join(THEMES_DIR, theme_filename)

        new_theme = {
            "id": slug,
            "name": display_name,
            "google_font_url": url,
            "font_family": f"'{raw_name}', sans-serif",
            "font_file": "",
            "text_transform": "uppercase",
            "letter_spacing": "1px",
            "text_color": "#FFFFFF",
            "text_shadow": "-4px -4px 0 #000, 4px -4px 0 #000, 0 0 30px rgba(255,98,0,0.8)",
            "container_background": "transparent",
            "impact_zoom": {
                "scale": 1.2,
                "text_color": "#FF6200",
                "text_shadow": "-4px -4px 0 #FFF, 4px -4px 0 #FFF, 0 0 45px #FF6200"
            }
        }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(new_theme, f, indent=2)

        self.reload_themes()
        slot = self.custom_slot_var.get()
        CONFIG.setdefault("slots", {})[slot] = slug
        save_config(CONFIG)
        self.preset_var.set("custom")
        self.sync_active_slot_display()
        self.on_preset_change()

        log_session_event("FONT_IMPORTED", display_name, f"Assigned to {slot.upper()}")
        mb.showinfo("Font Imported", f"Theme '{display_name}' created and assigned to {slot.upper()}!")

    def reload_themes(self):
        global DISK_THEMES
        DISK_THEMES = load_theme_files()
        self.update_theme_combobox()
        self.sync_active_slot_display()
        if self.preset_var.get() == "custom":
            self.on_preset_change()

    def open_sessions_folder(self):
        if sys.platform == 'win32':
            os.startfile(SESSIONS_DIR)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', SESSIONS_DIR])
        else:
            subprocess.Popen(['xdg-open', SESSIONS_DIR])

    def save_as_favorite(self):
        CONFIG["favorite_mode"] = self.preset_var.get()
        CONFIG["active_custom_slot"] = self.custom_slot_var.get()
        save_config(CONFIG)
        self.fav_status_label.config(text=self.get_fav_label())
        log_session_event("SAVED_FAVORITE", extra=self.get_fav_label())

    def open_browser(self):
        webbrowser.open(f"http://127.0.0.1:{ACTIVE_PORT}")

    def on_mode_change(self):
        self.is_zoomed = False
        log_session_event("MODE_SWITCH", extra=self.mode_var.get().upper())
        if self.mode_var.get() == "live":
            self.sync_live_text()

    def on_modified(self, event=None):
        if self.text_input.edit_modified():
            self.text_input.edit_modified(False)
            if self.mode_var.get() == "live":
                self.sync_live_text()

    def sync_live_text(self):
        content = self.text_input.get("1.0", "end-1c").strip()
        broadcast_payload({"text": content, "zoom": False})
        if content != self.last_pushed_text:
            self.last_pushed_text = content
            log_session_event("LIVE_STREAM", content)

    def on_return_pressed(self, event):
        if self.mode_var.get() == "batch":
            self.push_batch_content()
            return "break"

    def push_batch_content(self):
        content = self.text_input.get("1.0", "end-1c").strip()
        if content and content == self.last_pushed_text:
            self.is_zoomed = not self.is_zoomed
            log_session_event("PUNCH_TOGGLE", content, f"Zoom: {self.is_zoomed} | Pattern: {self.burst_var.get()}")
        else:
            self.is_zoomed = False
            self.last_pushed_text = content
            mode = self.preset_var.get()
            log_session_event("PUSH", content, f"Preset: {mode}")

        broadcast_payload({
            "text": content, 
            "zoom": self.is_zoomed, 
            "burst_mode": self.burst_var.get(),
            "burst_bpm": int(self.bpm_var.get())
        })

    def clear_all(self):
        self.text_input.delete("1.0", tk.END)
        self.last_pushed_text = ""
        self.is_zoomed = False
        log_session_event("CLEAR_SCREEN")
        broadcast_payload({"text": "", "zoom": False})

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    root = tk.Tk()
    app_ui = OperatorApp(root)
    root.mainloop()