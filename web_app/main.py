"""
FastAPI Server - Estuarine Mouth Dynamics Web Application
Path Deviation Prediction System
"""

import os
import sys
import io
import csv
from typing import Optional, Dict, Any

# Ensure web_app and project directories are in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
for _p in [_current_dir, _root_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from backend.dataset_config import dataset_config
    from backend.auth_service import auth_service
    from backend.weather_service import weather_service
    from backend.deviation_service import deviation_service
    from backend.lulc_service import lulc_service
    from backend.data_service import data_service
except ImportError:
    from web_app.backend.dataset_config import dataset_config
    from web_app.backend.auth_service import auth_service
    from web_app.backend.weather_service import weather_service
    from web_app.backend.deviation_service import deviation_service
    from web_app.backend.lulc_service import lulc_service
    from web_app.backend.data_service import data_service

app = FastAPI(
    title="Estuarine Mouth Dynamics - Path Deviation Prediction System",
    description="Geospatial Analysis, Remote Sensing & Machine Learning Web Platform",
    version="2.0.0",
)

# Enable CORS for external frontends (e.g., Netlify, Vercel, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount assets directory (logos, banners)
assets_dir = dataset_config.assets_dir
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Mount static web assets (vendor, js, css)
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    # Also mount subdirectories directly for relative path support
    for subdir in ("css", "js", "vendor"):
        sub_path = os.path.join(static_dir, subdir)
        if os.path.isdir(sub_path):
            app.mount(f"/{subdir}", StaticFiles(directory=sub_path), name=subdir)


# ----------------------------------------------------------------------------
# Pydantic Request Models
# ----------------------------------------------------------------------------
class LoginRequest(BaseModel):
    username_or_email: str
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    full_name: str
    role: str = "Researcher"


class ResetPasswordRequest(BaseModel):
    username_or_email: str
    new_password: str
    confirm_password: str


class ParameterRequest(BaseModel):
    base_year: int
    target_year: int
    aoi: Optional[Dict[str, float]] = None


class AOIRequest(BaseModel):
    north: float
    south: float
    east: float
    west: float


class LocationRequest(BaseModel):
    location_name: str
    lat: float
    lon: float


# ----------------------------------------------------------------------------
# Authentication Endpoints
# ----------------------------------------------------------------------------
@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    user_dict, token, err = auth_service.authenticate(req.username_or_email, req.password)
    if err or not user_dict:
        raise HTTPException(status_code=401, detail=err or "Invalid credentials")
    return {
        "success": True,
        "token": token,
        "user": user_dict,
    }


@app.post("/api/auth/register")
def api_register(req: RegisterRequest):
    ok, err = auth_service.register(
        username=req.username,
        email=req.email,
        password=req.password,
        confirm_password=req.confirm_password,
        full_name=req.full_name,
        role=req.role,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=err or "Registration failed")
    return {"success": True, "message": "Account created successfully. You can now sign in."}


@app.post("/api/auth/reset-password")
def api_reset_password(req: ResetPasswordRequest):
    ok, err = auth_service.reset_password(
        username_or_email=req.username_or_email,
        new_password=req.new_password,
        confirm_password=req.confirm_password,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=err or "Password reset failed")
    return {"success": True, "message": "Password updated successfully. Please sign in."}


@app.get("/api/auth/me")
def api_auth_me(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    user = auth_service.validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid token")
    return {"authenticated": True, "user": user}


@app.post("/api/auth/logout")
def api_logout(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    auth_service.logout_token(token)
    return {"success": True, "message": "Logged out successfully"}


# ----------------------------------------------------------------------------
# Configuration & Study Area State
# ----------------------------------------------------------------------------
@app.get("/api/config")
def get_config():
    return {
        "study_area": "Kodi Bengre, Udupi, Karnataka, India",
        "crs": "EPSG:32643",
        "center": [13.4380, 74.6980],
        "default_zoom": 13,
        "available_years": list(range(1989, 2027)),
        "min_year": 1989,
        "max_year": 2026,
    }


@app.get("/api/study-area/state")
def get_study_area_state():
    return data_service.get_state()


@app.post("/api/study-area/parameters")
def set_study_area_parameters(req: ParameterRequest):
    data_service.set_year_range(req.base_year, req.target_year)
    if req.aoi:
        data_service.set_aoi(
            north=req.aoi["north"],
            south=req.aoi["south"],
            east=req.aoi["east"],
            west=req.aoi["west"],
        )
    return {
        "success": True,
        "state": data_service.get_state(),
    }


@app.post("/api/study-area/aoi")
def set_aoi_coords(req: AOIRequest):
    data_service.set_aoi(north=req.north, south=req.south, east=req.east, west=req.west)
    return {
        "success": True,
        "aoi": data_service.get_aoi(),
    }


@app.delete("/api/study-area/aoi")
def clear_aoi_coords():
    data_service.clear_aoi()
    return {"success": True, "message": "AOI extent cleared"}


@app.post("/api/study-area/location")
def update_location(req: LocationRequest):
    data_service.set_location(req.location_name, req.lat, req.lon)
    return {
        "success": True,
        "location": data_service.get_location(),
    }


# ----------------------------------------------------------------------------
# River Mouth Gallery Endpoints
# ----------------------------------------------------------------------------
@app.get("/api/river-mouth/gallery")
def get_river_mouth_gallery(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
):
    items = data_service.get_gallery_items(start_year, end_year)
    return {
        "count": len(items),
        "items": items,
        "base_year": data_service.get_base_year(),
        "target_year": data_service.get_target_year(),
    }


@app.get("/api/river-mouth/image/{year}")
def get_river_mouth_image(year: int):
    path = data_service.get_river_mouth_image_path(year)
    if path and os.path.isfile(path):
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    raise HTTPException(status_code=404, detail=f"River mouth image not available for year {year}")


# ----------------------------------------------------------------------------
# Deviation Analysis Endpoints
# ----------------------------------------------------------------------------
@app.get("/api/deviation/calculate")
def get_deviation_analysis(
    base_year: int = 1989,
    target_year: int = 2000,
):
    result = deviation_service.calculate_deviation(base_year, target_year)
    if not result:
        raise HTTPException(status_code=400, detail="Could not calculate deviation for requested years")
    return result


@app.get("/api/deviation/export/csv")
def export_deviation_csv(
    base_year: int = 1989,
    target_year: int = 2000,
):
    dev = deviation_service.calculate_deviation(base_year, target_year)
    if not dev:
        raise HTTPException(status_code=400, detail="Could not generate deviation CSV")

    min_y = min(base_year, target_year)
    max_y = max(base_year, target_year)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Year", "Observation Type", "Latitude (WGS84)", "Longitude (WGS84)",
        "Displacement from Base (m)", "Azimuth Bearing (°)", "Compass Direction",
        "Estuary Water Area (km²)", "Mouth Width (m)", "Migration Rate (m/yr)"
    ])

    for row in dev["timeseries"]:
        if min_y <= row["year"] <= max_y:
            writer.writerow([
                row["year"],
                row["obs_type"],
                f"{row['mouth_lat']:.6f}",
                f"{row['mouth_lon']:.6f}",
                f"{row['displacement_m']:.2f}",
                f"{row['azimuth_deg']:.1f}",
                row["direction"],
                f"{row['water_area_km2']:.2f}",
                f"{row['opening_width_m']:.2f}" if row.get("opening_width_m") else "N/A",
                f"{row['rate_m_yr']:.2f}",
            ])

    output.seek(0)
    filename = f"Suvarna_Deviation_{base_year}_{target_year}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ----------------------------------------------------------------------------
# LULC Analysis Endpoints
# ----------------------------------------------------------------------------
@app.get("/api/lulc/master-records")
def get_lulc_master_records():
    recs = lulc_service.get_all_master_records()
    return {
        "count": len(recs),
        "records": recs,
    }


@app.get("/api/lulc/year/{year}")
def get_lulc_year(year: int):
    rec = lulc_service.get_master_record(year)
    if not rec:
        raise HTTPException(status_code=404, detail=f"LULC record not found for year {year}")
    return rec


@app.get("/api/lulc/image/{year}")
def get_lulc_image(year: int):
    p = lulc_service.get_lulc_image_path(year)
    if p and os.path.isfile(p):
        return FileResponse(p, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail=f"LULC image for year {year} not found")


@app.get("/api/lulc/export/csv")
def export_lulc_csv():
    p = dataset_config.lulc_master_csv
    if p and os.path.isfile(p):
        return FileResponse(p, media_type="text/csv", filename="LULC_Master_Counts.csv")
    raise HTTPException(status_code=404, detail="LULC Master CSV not found")


# ----------------------------------------------------------------------------
# Weather Endpoints
# ----------------------------------------------------------------------------
@app.get("/api/weather/annual")
def get_weather_annual(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
):
    recs = weather_service.get_annual_records(start_year, end_year)
    return {
        "count": len(recs),
        "records": recs,
    }


@app.get("/api/weather/monthly/{year}")
def get_weather_monthly(year: int):
    breakdown = weather_service.get_monthly_breakdown(year)
    if not breakdown:
        raise HTTPException(status_code=404, detail=f"Monthly breakdown not available for {year}")
    return {
        "year": year,
        "months": breakdown,
    }


@app.get("/api/weather/export/csv")
def export_weather_csv(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
):
    recs = weather_service.get_annual_records(start_year, end_year)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Year", "Avg Temperature (°C)", "Min Temperature (°C)", "Max Temperature (°C)",
        "Avg Relative Humidity (%)", "Annual Rainfall (mm)", "Monsoon Rainfall (mm)",
        "Pre-monsoon Rainfall (mm)", "Post-monsoon Rainfall (mm)", "Recorded Days", "Status"
    ])
    for r in recs:
        writer.writerow([
            r["year"],
            r["avg_temp"],
            r["avg_temp_min"],
            r["avg_temp_max"],
            r["avg_humidity"],
            r["annual_rainfall_mm"],
            r["monsoon_rainfall_mm"],
            r["pre_monsoon_rainfall_mm"],
            r["post_monsoon_rainfall_mm"],
            r["total_days"],
            r["status_note"],
        ])
    output.seek(0)
    filename = f"Suvarna_Weather_Dataset_{start_year or 1989}_{end_year or 2026}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ----------------------------------------------------------------------------
# Root Dashboard Page
# ----------------------------------------------------------------------------
@app.get("/")
def get_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "running", "message": "Estuarine Mouth Dynamics API Online"})


@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "app": "Estuarine Mouth Dynamics Web Platform"}
