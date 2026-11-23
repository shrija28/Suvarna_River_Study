# Estuarine Mouth Dynamics - Path Deviation Prediction System (Web App)

This is the standalone web version of the **Estuarine Mouth Dynamics & Path Deviation Prediction System**, converted from the Python desktop application into a web platform powered by **FastAPI** on the backend and **Leaflet / HTML5 Canvas** on the frontend.

---

## 1. Quick Start: Local Run

### Easiest Way (Single Click / Single Command)

From the project root folder:
- **On Windows**: Double-click `run_web.bat` or run:
  ```cmd
  run_web.bat
  ```
- **Or using Python**:
  ```bash
  python run_web.py
  ```
*(This automatically resolves the virtual environment, starts the FastAPI server, and launches your web browser to `http://127.0.0.1:8000`)*

---

### Manual Terminal Run

1. **Navigate to the `web_app/` directory**:
   ```bash
   cd web_app
   ```

2. **Install Web Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: No desktop PyQt/PySide6 packages are required!)*

3. **Start the FastAPI Server**:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Access the Application**:
   Open your browser and navigate to:
   - **Interactive Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Alternative ReDoc API Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Default Login Accounts
- **Researcher Account**:
  - Username: `scientist`
  - Password: `scientist123`
- **System Administrator**:
  - Username: `admin`
  - Password: `admin123`
*(Or use the "Create Account" tab to register your own credentials)*

---

## 2. Architecture & File Structure

```
web_app/
├── backend/
│   ├── auth_service.py       # SQLite (auth.db) + PBKDF2 password derivation & token auth
│   ├── dataset_config.py     # Automatic discovery of data/, SuvarnaProject_data/, and assets/
│   ├── data_service.py       # Centralized session state (Base/Target years, AOI, gallery metadata)
│   ├── deviation_service.py  # Spatial displacement, azimuth bearing, migration velocity, timeseries
│   ├── lulc_service.py       # Multi-decadal 4-class LULC statistics (Vegetation, Water, Barren, Built-up)
│   └── weather_service.py    # Daily & seasonal rainfall, temperature, and humidity aggregations
├── static/
│   ├── index.html            # Single-Page Dashboard Shell (Branding, Sidebar, Views, Status bar)
│   ├── css/
│   │   └── style.css         # Dark Emerald GIS theme tokens (matching theme.py)
│   ├── js/
│   │   ├── app.js            # SPA view routing, REST fetch API client, HTML5 Canvas charts
│   │   └── script.js         # Leaflet Map Engine (QWebChannel replaced with standard fetch)
│   └── vendor/
│       ├── leaflet/          # Leaflet 1.9.4 map library
│       └── leaflet-draw/     # Leaflet Draw 1.0.4 AOI toolbar
├── config.json               # CRS and study area bounds configuration
├── main.py                   # FastAPI application, CORS middleware, API endpoints, static mounts
├── requirements.txt          # Pure web requirements
└── README.md                 # Deployment & usage guide
```

---

## 3. Deployment Guide

### Option A: Full-Stack Deployment to Render (Recommended)

1. Push your repository to GitHub or GitLab.
2. Log into [Render.com](https://render.com) and click **New + &rarr; Web Service**.
3. Connect your repository.
4. Configure the service settings:
   - **Name**: `estuarine-mouth-dynamics`
   - **Runtime**: `Python 3`
   - **Root Directory**: `web_app`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Render will build and deploy both the FastAPI REST backend and the Leaflet frontend in a single container.

---

### Option B: Decoupled Frontend Deployment to Netlify

If you wish to host the static frontend on Netlify while keeping the backend hosted on Render or a cloud VM:

1. In `web_app/static/js/app.js` and `web_app/static/js/script.js`, configure the API base URL to point to your live backend (e.g. `https://your-render-app.onrender.com`).
2. Log into [Netlify.com](https://netlify.com) and click **Add new site &rarr; Deploy manually** or connect your git repo.
3. Set the publish directory to `web_app/static`.
4. Deploy! Because CORS is already configured with `allow_origins=["*"]` on FastAPI, the frontend will communicate with the backend.

---

## 4. Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate username/password & issue session token |
| `POST` | `/api/auth/register` | Register new researcher account |
| `GET` | `/api/config` | Project CRS, bounds, and observation year bounds |
| `GET` | `/api/study-area/state` | Active base year, prediction year, and AOI coordinates |
| `POST` | `/api/study-area/parameters` | Set base year, target year, and AOI bounds |
| `POST` | `/api/study-area/aoi` | Capture drawn rectangle AOI bounds from Leaflet |
| `DELETE` | `/api/study-area/aoi` | Clear active AOI bounds |
| `GET` | `/api/river-mouth/gallery` | Multi-decadal satellite observation cards |
| `GET` | `/api/river-mouth/image/{year}` | Stream authentic First Opening PNG image |
| `GET` | `/api/deviation/calculate` | Euclidean displacement, azimuth bearing & migration rate |
| `GET` | `/api/deviation/export/csv` | Download deviation results as CSV |
| `GET` | `/api/lulc/master-records` | Complete 37-year 4-class LULC dataset |
| `GET` | `/api/lulc/export/csv` | Download LULC master counts CSV |
| `GET` | `/api/weather/annual` | 1989–2026 annual weather and seasonal rainfall |
| `GET` | `/api/weather/export/csv` | Download meteorological dataset as CSV |
