---
title: Suvarna River Path Deviation Prediction System
emoji: 🌊
colorFrom: green
colorTo: blue
sdk: docker
app_port: 10000
pinned: false
---

# Suvarna River Path Deviation Prediction System (Web Edition)

A comprehensive geospatial web platform monitoring river mouth deviation, land use/land cover (LULC) changes, and meteorological trends for the Suvarna River basin in Udupi, Karnataka, India (1989–2026).

## Features
- **Interactive Geospatial Webmap**: High-resolution Leaflet map with satellite, terrain, and street layers, measurement tools, and river mouth coordinates.
- **River Mouth Gallery**: Multi-decade visual satellite archive of the estuary.
- **Deviation Analytics**: 1989–2026 path displacement, bearing, and timeseries displacement graphs.
- **LULC Analysis**: 4-class satellite land cover classification and proportional distribution.
- **Meteorological Trends**: User-selected year range filtering for precipitation, temperature, and humidity with dynamic charts.
- **Role-Based Authentication**: Secure SQLite PBKDF2 user session management.

## Running Locally

```bash
# 1. Install dependencies
pip install -r web_app/requirements.txt

# 2. Run the application
python run_web.py
# or:
uvicorn web_app.main:app --host 127.0.0.1 --port 8000 --reload
```
Access the application at `http://127.0.0.1:8000` (Default credentials: `admin` / `admin123`).
