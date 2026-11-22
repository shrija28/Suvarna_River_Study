#!/bin/bash
set -e

# Render binds to the $PORT environment variable (defaults to 10000)
PORT=${PORT:-10000}
RESOLUTION=${RESOLUTION:-"1600x950x24"}

echo "=== Initializing Suvarna River Study on Render ==="
echo "Display Resolution: $RESOLUTION"
echo "Listening Port: $PORT"

# 1. Start Xvfb virtual framebuffer display
echo "Starting Xvfb server on display :99..."
Xvfb :99 -screen 0 $RESOLUTION -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2

# 2. Start Openbox window manager
echo "Starting Openbox window manager..."
openbox-session &
sleep 1

# 3. Start x11vnc server
echo "Starting x11vnc server on port 5900..."
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 -quiet &
sleep 1

# 4. Start Websockify / noVNC web server on $PORT
echo "Starting noVNC web interface on 0.0.0.0:$PORT..."
websockify --web /usr/share/novnc 0.0.0.0:$PORT localhost:5900 &
sleep 1

# 5. Launch the PySide6 Estuarine Mouth Dynamics Application
export DISPLAY=:99
export QT_QPA_PLATFORM=xcb
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

echo "Starting PySide6 Application..."
while true; do
    python main.py
    echo "Application process ended. Restarting in 2 seconds..."
    sleep 2
done
