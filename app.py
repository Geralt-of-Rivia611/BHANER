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

# --- APP VERSION & REPO CONFIG ---
APP_VERSION = "1.0.0"
GITHUB_REPO = "Geralt-of-Rivia611/BHANER"  # e.g., "johndoe/bhaner"
CONFIG_FILE = "bhaner_config.json"

# --- AUTO-UPDATE LOGIC ---
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
            # If offline or repo not yet created, continue silently
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
            mb.showinfo("Update Notice", "Running from source code. Please pull latest git commits.")
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

# --- PRESET CONFIG STORAGE ---
def load_favorite_preset() -> str:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("favorite_preset", "p1")
    except Exception:
        pass
    return "p1"

def save_favorite_preset(preset_id: str):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"favorite_preset": preset_id}, f)
    except Exception:
        pass

current_state = {
    "text": "",
    "zoom": False,
    "preset": load_favorite_preset()
}
state_lock = threading.Lock()

clients_queues = set()
clients_lock = threading.Lock()

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

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>bhaner - Stage Projection</title>
  <style>
    :root {{
      --brand-orange: #FF6200;
      --brand-brown: #5C1B03;
      --brand-white: #FFFFFF;
      --ocean-cyan: #00F2FE;
    }}

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
      transition: background 0.3s ease;
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
      transition: opacity 0.3s ease;
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
      transition: background 0.25s ease;
    }}

    #projector-text {{
      word-wrap: break-word;
      line-height: 1.05;
      white-space: pre-wrap;
      max-width: 100%;
      transform-origin: center center;
      transition: transform 0.22s cubic-bezier(0.175, 0.885, 0.32, 1.275), color 0.2s ease, text-shadow 0.2s ease;
    }}

    /* PRESET 1: BRAND FLAME */
    body.preset-p1 #projector-text {{
      font-family: 'Impact', 'Arial Black', sans-serif;
      text-transform: uppercase;
      color: var(--brand-white);
      text-shadow:
        -3px -3px 0 var(--brand-brown), 3px -3px 0 var(--brand-brown),
        -3px  3px 0 var(--brand-brown), 3px  3px 0 var(--brand-brown),
        -5px  0px 0 var(--brand-brown), 5px  0px 0 var(--brand-brown),
        0px -5px 0 var(--brand-brown), 0px  5px 0 var(--brand-brown),
        0px  8px 25px rgba(0, 0, 0, 0.95);
    }}
    body.preset-p1 .impact-zoom {{
      transform: scale(1.18);
      color: var(--brand-orange) !important;
      text-shadow: -4px -4px 0 #FFF, 4px -4px 0 #FFF, -4px 4px 0 #FFF, 4px 4px 0 #FFF, 0 0 40px rgba(255, 98, 0, 0.9) !important;
    }}

    /* PRESET 2: OCEAN VORTEX PUNCH */
    body.preset-p2 #projector-text {{
      font-family: 'Impact', 'Arial Black', sans-serif;
      text-transform: uppercase;
      color: var(--brand-orange);
      text-shadow:
        -4px -4px 0 #000, 4px -4px 0 #000,
        -4px  4px 0 #000, 4px  4px 0 #000,
        -6px  0px 0 #000, 6px  0px 0 #000,
        0px -6px 0 #000, 0px  6px 0 #000,
        0 0 35px rgba(255, 98, 0, 0.95);
    }}
    body.preset-p2 .impact-zoom {{
      transform: scale(1.18);
      color: #FFFFFF !important;
      text-shadow: -4px -4px 0 var(--brand-orange), 4px -4px 0 var(--brand-orange), -4px 4px 0 var(--brand-orange), 4px 4px 0 var(--brand-orange), 0 0 40px #FFF !important;
    }}

    /* PRESET 3: CORE SHIELD */
    body.preset-p3 #display-container {{
      background: radial-gradient(ellipse at center, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 65%, transparent 100%);
    }}
    body.preset-p3 #projector-text {{
      font-family: 'Impact', 'Arial Black', sans-serif;
      text-transform: uppercase;
      color: #FFFFFF;
      text-shadow:
        -5px -5px 0 #000, 5px -5px 0 #000,
        -5px  5px 0 #000, 5px  5px 0 #000,
        0 0 30px rgba(255, 98, 0, 0.8);
    }}
    body.preset-p3 .impact-zoom {{
      transform: scale(1.18);
      color: var(--brand-orange) !important;
      text-shadow: -5px -5px 0 #000, 5px -5px 0 #000, -5px 5px 0 #000, 5px 5px 0 #000, 0 0 50px #FF6200 !important;
    }}

    /* PRESET 4: CYBER CYAN */
    body.preset-p4 #projector-text {{
      font-family: 'Segoe UI Black', 'Arial Black', sans-serif;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: #FFFFFF;
      text-shadow:
        -3px -3px 0 #032127, 3px -3px 0 #032127,
        -3px  3px 0 #032127, 3px  3px 0 #032127,
        0 0 25px rgba(0, 242, 254, 0.9);
    }}
    body.preset-p4 .impact-zoom {{
      transform: scale(1.18);
      color: var(--ocean-cyan) !important;
      text-shadow: 0 0 35px #00F2FE, -4px -4px 0 #000, 4px -4px 0 #000 !important;
    }}

    /* PRESET 5: MINIMALIST PURE WHITE */
    body.preset-p5 #projector-text {{
      font-family: 'Arial Black', sans-serif;
      text-transform: uppercase;
      color: #FFFFFF;
      text-shadow: 0 4px 20px rgba(0, 0, 0, 0.95), 0 0 10px rgba(0,0,0,0.8);
    }}
    body.preset-p5 .impact-zoom {{
      transform: scale(1.18);
      text-shadow: 0 0 40px rgba(255, 255, 255, 0.9), 0 4px 20px rgba(0, 0, 0, 1) !important;
    }}
  </style>
</head>
<body class="preset-p1">
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

    function autoFitText() {{
      const text = textEl.innerText.trim();
      if (!text) {{
        textEl.style.fontSize = '12px';
        return;
      }}

      textEl.classList.remove('impact-zoom');

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
    }}

    function applyUpdate(data) {{
      if (data.preset) {{
        document.body.className = 'preset-' + data.preset;
      }}

      const currentText = textEl.innerText.trim();
      const incomingText = (data.text || '').trim();

      if (incomingText !== currentText) {{
        textEl.innerText = incomingText;
        autoFitText();
      }}

      if (data.zoom) {{
        textEl.classList.add('impact-zoom');
      }} else {{
        textEl.classList.remove('impact-zoom');
      }}
    }}

    const evtSource = new EventSource('/stream');
    evtSource.onmessage = (event) => {{
      try {{
        const payload = JSON.parse(event.data);
        applyUpdate(payload);
      }} catch (err) {{
        applyUpdate({{ text: event.data, zoom: false, preset: 'p1' }});
      }}
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
        if "preset" in payload:
            current_state["preset"] = payload["preset"]

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
        self.root.geometry("520x520")
        self.root.minsize(460, 480)

        self.last_pushed_text = ""
        self.is_zoomed = False
        self.favorite_preset = load_favorite_preset()

        # Presets Toolbar
        preset_frame = ttk.LabelFrame(root, text=" Visual Presets (Quick-Switch: F1 - F5) ", padding=8)
        preset_frame.pack(fill="x", padx=15, pady=6)

        self.preset_var = tk.StringVar(value=self.favorite_preset)
        self.presets = [
            ("P1: Flame (Orange Stage)", "p1"),
            ("P2: Ocean Punch (Orange on Cyan)", "p2"),
            ("P3: Core Flare Shield", "p3"),
            ("P4: Cyber Cyan", "p4"),
            ("P5: Minimal White", "p5")
        ]

        preset_btn_grid = ttk.Frame(preset_frame)
        preset_btn_grid.pack(fill="x")

        for idx, (label, pid) in enumerate(self.presets):
            rb = ttk.Radiobutton(preset_btn_grid, text=label, value=pid, variable=self.preset_var, command=self.on_preset_change)
            rb.grid(row=idx // 2, column=idx % 2, sticky="w", padx=6, pady=2)
            self.root.bind(f"<F{idx+1}>", lambda e, p=pid: self.set_preset(p))

        fav_frame = ttk.Frame(preset_frame)
        fav_frame.pack(fill="x", pady=4)
        self.fav_status_label = ttk.Label(fav_frame, text=f"★ Default Startup: Preset {self.favorite_preset.upper()}", font=("Segoe UI", 9, "bold"))
        self.fav_status_label.pack(side="left", padx=5)

        ttk.Button(fav_frame, text="Set Current as Default ★", command=self.save_as_favorite).pack(side="right", padx=5)

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

        # Buttons
        btn_frame = ttk.Frame(root, padding=8)
        btn_frame.pack(fill="x", padx=15)

        self.push_btn = ttk.Button(btn_frame, text="Push Content (Enter)", command=self.push_batch_content)
        self.push_btn.pack(side="left", padx=4)

        ttk.Button(btn_frame, text="Clear Screen", command=self.clear_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Re-open Window", command=self.open_browser).pack(side="right", padx=4)

        self.root.after(700, self.open_browser)

        # --- Automatic Update Check on Window Launch ---
        check_for_updates(self.root)

    def set_preset(self, preset_id: str):
        self.preset_var.set(preset_id)
        self.on_preset_change()

    def on_preset_change(self):
        broadcast_payload({"preset": self.preset_var.get()})

    def save_as_favorite(self):
        chosen = self.preset_var.get()
        self.favorite_preset = chosen
        save_favorite_preset(chosen)
        self.fav_status_label.config(text=f"★ Default Startup: Preset {chosen.upper()}")

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