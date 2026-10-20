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
import subprocess
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# --- APP CONFIGURATION ---
APP_VERSION = "1.1.0"
GITHUB_REPO = "Geralt-of-Rivia611/BHANER"
CONFIG_FILE = "bhaner_config.json"

# Base directory for executable or script
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

THEMES_DIR = os.path.join(BASE_DIR, "themes")
FONTS_DIR = os.path.join(THEMES_DIR, "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

# Default templates to generate if the folder is empty
DEFAULT_THEMES = {
    "01_flame.json": {
        "id": "p1_flame",
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
    "02_ocean_punch.json": {
        "id": "p2_ocean_punch",
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
    "03_core_shield.json": {
        "id": "p3_core_shield",
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
    "04_cyber_cyan.json": {
        "id": "p4_cyber_cyan",
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
    "05_minimal_white.json": {
        "id": "p5_minimal_white",
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

def ensure_default_themes():
    for filename, content in DEFAULT_THEMES.items():
        file_path = os.path.join(THEMES_DIR, filename)
        if not os.path.exists(file_path):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2)
            except Exception:
                pass

ensure_default_themes()

def load_all_themes() -> dict[str, dict]:
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
    if not themes:
        themes["p1_flame"] = DEFAULT_THEMES["01_flame.json"]
    return themes

AVAILABLE_THEMES = load_all_themes()

def load_favorite_theme() -> str:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                fav = data.get("favorite_theme")
                if fav in AVAILABLE_THEMES:
                    return fav
    except Exception:
        pass
    return next(iter(AVAILABLE_THEMES.keys()))

def save_favorite_theme(theme_id: str):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"favorite_theme": theme_id}, f)
    except Exception:
        pass

# --- AUTO-UPDATE PIPELINE ---
def check_for_updates(parent_window):
    def worker():
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "bhaner-updater"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
            
            latest_tag = data.get("tag_name", "").lstrip("v")
            if not latest_tag:
                return

            def parse_ver(v):
                return tuple(map(int, (v.split('.'))))

            if parse_ver(latest_tag) > parse_ver(APP_VERSION):
                exe_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        exe_url = asset["browser_download_url"]
                        break
                if exe_url:
                    parent_window.after(0, lambda: prompt_update(latest_tag, exe_url))
        except Exception:
            pass
    threading.Thread(target=worker, daemon=True).start()

def prompt_update(new_version, download_url):
    answer = mb.askyesno(
        "Update Available", 
        f"A new version of bhaner (v{new_version}) is available!\n\nWould you like to download and update now?"
    )
    if answer:
        threading.Thread(target=perform_update, args=(download_url,), daemon=True).start()

def perform_update(download_url):
    try:
        current_exe = sys.executable
        if not current_exe.endswith(".exe"):
            return
        new_exe = current_exe.replace(".exe", "_new.exe")
        urllib.request.urlretrieve(download_url, new_exe)

        updater_bat = os.path.join(os.path.dirname(current_exe), "update_bhaner.bat")
        with open(updater_bat, "w") as f:
            f.write(f"""@echo off
timeout /t 1 /nobreak >nul
del "{current_exe}"
move "{new_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
""")
        subprocess.Popen([updater_bat], shell=True)
        os._exit(0)
    except Exception as e:
        mb.showerror("Update Error", f"Failed to complete update:\n{e}")

# --- SERVER & PORT ---
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

current_theme_id = load_favorite_theme()
current_state = {
    "text": "",
    "zoom": False,
    "theme": AVAILABLE_THEMES[current_theme_id]
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
      width: 100%;
      height: 100%;
      background: #000000;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
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
      border-radius: 20px;
      transition: background 0.3s ease;
    }}

    #projector-text {{
      word-wrap: break-word;
      line-height: 1.05;
      white-space: pre-wrap;
      max-width: 100%;
      transform-origin: center center;
      transition: transform 0.22s cubic-bezier(0.175, 0.885, 0.32, 1.275), color 0.2s ease, text-shadow 0.2s ease;
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

  <script>
    const textEl = document.getElementById('projector-text');
    const container = document.getElementById('display-container');
    const googleFontLink = document.getElementById('google-font-link');
    const dynamicFontFace = document.getElementById('dynamic-font-face');

    let activeTheme = {{}};
    let isZoomed = false;

    function applyTheme(theme) {{
      activeTheme = theme;

      // Google Font URL
      if (theme.google_font_url && theme.google_font_url.trim()) {{
        googleFontLink.href = theme.google_font_url;
      }} else {{
        googleFontLink.removeAttribute('href');
      }}

      // Local Custom Font file served from /fonts/
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
      container.style.background = theme.container_background || 'transparent';

      applyVisualState();
    }}

    function applyVisualState() {{
      if (!activeTheme || !activeTheme.text_color) return;

      if (isZoomed && activeTheme.impact_zoom) {{
        textEl.style.transform = `scale(${{activeTheme.impact_zoom.scale || 1.18}})`;
        textEl.style.color = activeTheme.impact_zoom.text_color || activeTheme.text_color;
        textEl.style.textShadow = activeTheme.impact_zoom.text_shadow || activeTheme.text_shadow;
      }} else {{
        textEl.style.transform = 'scale(1.0)';
        textEl.style.color = activeTheme.text_color;
        textEl.style.textShadow = activeTheme.text_shadow;
      }}
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
            # Serve local custom font files from themes/fonts/
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
        if "text" in payload:
            current_state["text"] = payload["text"]
        if "zoom" in payload:
            current_state["zoom"] = payload["zoom"]
        if "theme" in payload:
            current_state["theme"] = payload["theme"]

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
        self.root.geometry("540x550")
        self.root.minsize(480, 500)

        self.last_pushed_text = ""
        self.is_zoomed = False
        self.current_theme_id = load_favorite_theme()

        # Theme Selector Toolbar
        theme_frame = ttk.LabelFrame(root, text=" Visual Theme & Custom Typography ", padding=8)
        theme_frame.pack(fill="x", padx=15, pady=6)

        sel_row = ttk.Frame(theme_frame)
        sel_row.pack(fill="x", pady=2)

        ttk.Label(sel_row, text="Active Theme:").pack(side="left", padx=4)

        self.theme_var = tk.StringVar(value=self.current_theme_id)
        self.theme_combobox = ttk.Combobox(sel_row, textvariable=self.theme_var, state="readonly", width=28)
        self.theme_combobox.pack(side="left", padx=4)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.on_theme_selected)

        ttk.Button(sel_row, text="Reload ⟳", width=9, command=self.reload_themes).pack(side="left", padx=3)
        ttk.Button(sel_row, text="Open Folder 📁", command=self.open_themes_folder).pack(side="left", padx=3)

        fav_row = ttk.Frame(theme_frame)
        fav_row.pack(fill="x", pady=4)

        self.fav_status_label = ttk.Label(fav_row, text=f"★ Startup Default: {AVAILABLE_THEMES[self.current_theme_id].get('name')}", font=("Segoe UI", 9, "bold"))
        self.fav_status_label.pack(side="left", padx=4)

        ttk.Button(fav_row, text="Set as Default ★", command=self.save_as_favorite).pack(side="right", padx=4)

        self.refresh_combobox_values()

        # Transmission Mode
        self.mode_var = tk.StringVar(value="live")
        mode_frame = ttk.LabelFrame(root, text=" Transmission Mode ", padding=8)
        mode_frame.pack(fill="x", padx=15, pady=4)

        ttk.Radiobutton(mode_frame, text="Live Mode (Keystrokes update in real time)", value="live", variable=self.mode_var, command=self.on_mode_change).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Batch Mode (Enter to push | 2nd Enter to punch)", value="batch", variable=self.mode_var, command=self.on_mode_change).pack(anchor="w", pady=2)

        # Content Input
        input_frame = ttk.LabelFrame(root, text=" Screen Content ", padding=8)
        input_frame.pack(fill="both", expand=True, padx=15, pady=4)

        self.text_input = tk.Text(input_frame, wrap="word", font=("Segoe UI", 12), height=4)
        self.text_input.pack(fill="both", expand=True)

        self.text_input.bind("<<Modified>>", self.on_modified)
        self.text_input.bind("<Return>", self.on_return_pressed)

        # Control Buttons
        btn_frame = ttk.Frame(root, padding=8)
        btn_frame.pack(fill="x", padx=15)

        self.push_btn = ttk.Button(btn_frame, text="Push Content (Enter)", command=self.push_batch_content)
        self.push_btn.pack(side="left", padx=4)

        ttk.Button(btn_frame, text="Clear Screen", command=self.clear_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Re-open Window", command=self.open_browser).pack(side="right", padx=4)

        self.root.after(700, self.open_browser)
        check_for_updates(self.root)

    def refresh_combobox_values(self):
        names = [f"{tid}: {data.get('name', tid)}" for tid, data in AVAILABLE_THEMES.items()]
        self.theme_combobox['values'] = names
        for idx, tid in enumerate(AVAILABLE_THEMES.keys()):
            if tid == self.current_theme_id:
                self.theme_combobox.current(idx)
                break

    def on_theme_selected(self, event=None):
        selected_text = self.theme_var.get()
        tid = selected_text.split(":")[0].strip()
        if tid in AVAILABLE_THEMES:
            self.current_theme_id = tid
            broadcast_payload({"theme": AVAILABLE_THEMES[tid]})

    def reload_themes(self):
        global AVAILABLE_THEMES
        AVAILABLE_THEMES = load_all_themes()
        self.refresh_combobox_values()
        if self.current_theme_id in AVAILABLE_THEMES:
            broadcast_payload({"theme": AVAILABLE_THEMES[self.current_theme_id]})
        mb.showinfo("Themes Reloaded", f"Loaded {len(AVAILABLE_THEMES)} theme presets successfully.")

    def open_themes_folder(self):
        if sys.platform == 'win32':
            os.startfile(THEMES_DIR)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', THEMES_DIR])
        else:
            subprocess.Popen(['xdg-open', THEMES_DIR])

    def save_as_favorite(self):
        save_favorite_theme(self.current_theme_id)
        name = AVAILABLE_THEMES[self.current_theme_id].get("name", self.current_theme_id)
        self.fav_status_label.config(text=f"★ Startup Default: {name}")

    def open_browser(self):
        webbrowser.open(f"http://127.0.0.1:{ACTIVE_PORT}")

    def on_mode_change(self):
        self.is_zoomed = False
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

    def on_return_pressed(self, event):
        if self.mode_var.get() == "batch":
            self.push_batch_content()
            return "break"

    def push_batch_content(self):
        content = self.text_input.get("1.0", "end-1c").strip()
        if content and content == self.last_pushed_text:
            self.is_zoomed = not self.is_zoomed
        else:
            self.is_zoomed = False
            self.last_pushed_text = content

        broadcast_payload({"text": content, "zoom": self.is_zoomed})

    def clear_all(self):
        self.text_input.delete("1.0", tk.END)
        self.last_pushed_text = ""
        self.is_zoomed = False
        broadcast_payload({"text": "", "zoom": False})

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    root = tk.Tk()
    app_ui = OperatorApp(root)
    root.mainloop()