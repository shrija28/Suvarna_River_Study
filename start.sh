#!/bin/bash
set -e

# Render binds to the $PORT environment variable (defaults to 10000)
PORT=${PORT:-10000}
RESOLUTION=${RESOLUTION:-"1600x950x24"}
export DISPLAY=:99
export QT_QPA_PLATFORM=xcb
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

echo "=== Initializing Suvarna River Study on Render ==="
echo "Display Resolution: $RESOLUTION"
echo "Listening Port: $PORT"

# 1. Start Xvfb virtual framebuffer display with full synthetic input (XTEST) and rendering extensions
echo "Starting Xvfb server on display :99..."
Xvfb :99 -screen 0 $RESOLUTION -ac +extension GLX +extension RANDR +extension RENDER +extension XTEST -noreset &
XVFB_PID=$!
sleep 2

# 2. Configure and start Openbox window manager with auto-focus on pointer hover
echo "Starting Openbox window manager..."
mkdir -p /root/.config/openbox
cat << 'EOF' > /root/.config/openbox/rc.xml
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <focus>
    <focusNew>yes</focusNew>
    <followMouse>yes</followMouse>
    <focusLast>yes</focusLast>
    <underMouse>yes</underMouse>
  </focus>
</openbox_config>
EOF
openbox --sm-disable &
sleep 1

# 3. Start x11vnc server with -always_inject to prevent dead clicks in Xvfb
echo "Starting x11vnc server on port 5900..."
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 -always_inject -noxdamage -xkb -repeat -cursor arrow -wait 10 -quiet &
sleep 1

# 4. Start Websockify / noVNC web server on $PORT
echo "Starting noVNC web interface on 0.0.0.0:$PORT..."
websockify --web /usr/share/novnc 0.0.0.0:$PORT localhost:5900 &
sleep 1

# 5. Launch the PySide6 Estuarine Mouth Dynamics Application
echo "Starting PySide6 Application..."
while true; do
    python main.py
    echo "Application process ended. Restarting in 2 seconds..."
    sleep 2
done
