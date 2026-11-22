# Multi-stage / lightweight Debian Bookworm image with Python 3.11
FROM python:3.11-slim-bookworm

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

# Install system dependencies for X11 virtual display, noVNC, Openbox, OpenGL, and Qt6/WebEngine
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    openbox \
    novnc \
    websockify \
    libatomic1 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1 \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    libxext6 \
    libxrender1 \
    libx11-xcb1 \
    libdrm2 \
    libgbm1 \
    libxslt1.1 \
    libpulse0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libnss3 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxtst6 \
    libxrandr2 \
    libxcursor1 \
    libxi6 \
    libxinerama1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Configure noVNC to auto-connect and open full-screen directly at root URL
RUN ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html && \
    sed -i "s/UI.initSetting('autoconnect', false);/UI.initSetting('autoconnect', true);/" /usr/share/novnc/app/ui.js && \
    sed -i "s/UI.initSetting('resize', 'off');/UI.initSetting('resize', 'scale');/" /usr/share/novnc/app/ui.js

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and data assets
COPY . .

# Ensure start.sh has executable permissions
RUN chmod +x /app/start.sh

# Expose Render HTTP port
EXPOSE 10000

# Start noVNC virtual display and application
CMD ["/app/start.sh"]
