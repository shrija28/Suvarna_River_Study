"""
Launcher script for Suvarna Nadi - Estuarine Mouth Dynamics Web Application.
Launches the FastAPI server and automatically opens the browser.
"""

import os
import sys
import time
import webbrowser
import subprocess

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    web_app_dir = os.path.join(root_dir, "web_app")

    if not os.path.isdir(web_app_dir):
        print(f"Error: web_app directory not found at {web_app_dir}")
        sys.exit(1)

    # Change working directory to web_app
    os.chdir(web_app_dir)
    sys.path.insert(0, web_app_dir)

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 70)
    print("  SUVRNA NADI - ESTUARINE MOUTH DYNAMICS PREDICTION SYSTEM")
    print("  NITK Surathkal - Remote Sensing & Coastal GIS Platform")
    print("=" * 70)
    print(f"\n[+] Starting FastAPI server at: {url}")
    print(f"[+] Web Application Directory: {web_app_dir}")
    print("[+] Press Ctrl+C at any time to stop the server.\n")

    # Open browser after a slight delay
    def open_browser():
        time.sleep(1.5)
        print(f"[+] Opening browser at {url}...")
        webbrowser.open(url)

    import threading
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    try:
        import uvicorn
        uvicorn.run("main:app", host=host, port=port, reload=True)
    except ImportError:
        print("[!] Uvicorn not installed in current environment.")
        print("[!] Installing requirements from web_app/requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        import uvicorn
        uvicorn.run("main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
