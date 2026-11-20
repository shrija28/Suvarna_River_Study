"""
Deviation Service - Suvarna River Study GIS Dashboard
Performs rigorous spatial calculations of estuarine river-mouth displacement,
migration direction (azimuth bearing & compass heading), and water-body area changes
across multi-decadal satellite rasters (1989-2026).
Coordinate Reference System: EPSG:32643 (UTM Zone 43N, Projected meters)
Geographic Output: EPSG:4326 (WGS 84, Latitude/Longitude)
"""

import os
import json
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform as warp_transform
import numpy as np
import pandas as pd
from PySide6.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF
from backend.dataset_config import dataset_config

# Primary raster search directories
RASTER_DIRS = [
    dataset_config.river_mouth_dir,
    dataset_config.ndwi_dir,
    dataset_config.rgb_dir,
    r"D:\Suvarna_River_Study\SuvarnaProject_data\river mouth images",
    r"D:\Suvarna_River_Study\data",
]

# Estuarine Mouth AOI in UTM Zone 43N (meters)
AOI_BOUNDS = (465285.0, 1484415.0, 470385.0, 1489425.0)


class DeviationService:
    def __init__(self):
        self.raster_dir = self._find_raster_dir()
        self._year_cache = {}
        self.aoi_left, self.aoi_bottom, self.aoi_right, self.aoi_top = AOI_BOUNDS
        self.fo_lookup = self._load_ground_truth()

    def _find_raster_dir(self):
        for d in RASTER_DIRS:
            if os.path.exists(d):
                return d
        return ""

    def load_mouth_width_shift_df(self) -> pd.DataFrame:
        """
        Loads the verified multi-decadal river mouth width and coordinate shift dataset (1989–2026).
        Returns a DataFrame with columns:
        [Index, Year, Mouth Width (m), Longitude, Latitude, East Shift (m), North Shift (m)]
        """
        paths = [
            os.path.join(dataset_config.root_dir, "SuvarnaProject_data", "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "data", "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
            r"D:\Suvarna_River_Study\SuvarnaProject_data\Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv",
            r"D:\Suvarna_River_Study\data\Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv",
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    df = pd.read_csv(p)
                    return df
                except Exception as e:
                    print(f"[DeviationService] Error loading mouth width & shift CSV from {p}: {e}")
        return pd.DataFrame()

    def _load_ground_truth(self):
        """
        Loads verified First-Opening mouth measurements from Google Drive / project datasets:
        - Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv (verified 38-year width & shifts)
        - First_Opening_1989_2026.csv (Mouth_Row, Mouth_Col, Latitude, Longitude, Opening_Width_m)
        - Suvarna_First_Opening_Results.csv (verified width calibrations)
        Standardizes all coordinates to UTM Zone 43N meters (EPSG:32643) and WGS84 degrees.
        """
        lookup = {}

        # 1. Base First Opening CSV for pixel row/col references
        fo_paths = [
            os.path.join(dataset_config.root_dir, "First_Opening_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "SuvarnaProject_data", "First_Opening_1989_2026.csv"),
            r"D:\Suvarna_River_Study\SuvarnaProject_data\First_Opening_1989_2026.csv",
            r"D:\Suvarna_River_Study\First_Opening_1989_2026.csv",
        ]
        for p in fo_paths:
            if os.path.exists(p):
                try:
                    df_fo = pd.read_csv(p)
                    lons = df_fo['Longitude'].tolist()
                    lats = df_fo['Latitude'].tolist()
                    utmx, utmy = warp_transform('EPSG:4326', 'EPSG:32643', lons, lats)
                    for i, (_, row) in enumerate(df_fo.iterrows()):
                        y = int(row['Year'])
                        lookup[y] = {
                            "utm_x": float(utmx[i]),
                            "utm_y": float(utmy[i]),
                            "lat": float(row['Latitude']),
                            "lon": float(row['Longitude']),
                            "width_m": float(row.get('Opening_Width_m', 0.0)),
                            "mouth_row": float(row.get('Mouth_Row', 0.0)),
                            "mouth_col": float(row.get('Mouth_Col', 0.0)),
                        }
                    break
                except Exception as e:
                    print(f"[DeviationService] Error loading base First_Opening CSV: {e}")

        # 2. Master verified Mouth Width & Coordinate Shift dataset (1989–2026)
        df_mw = self.load_mouth_width_shift_df()
        if not df_mw.empty:
            for _, row in df_mw.iterrows():
                y = int(row['Year'])
                if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
                    lookup[y] = {
                        "has_data": False,
                        "utm_x": 0.0,
                        "utm_y": 0.0,
                        "lat": 0.0,
                        "lon": 0.0,
                        "width_m": 0.0,
                        "east_shift_m": 0.0,
                        "north_shift_m": 0.0,
                        "mouth_row": 0.0,
                        "mouth_col": 0.0,
                    }
                    continue
                try:
                    lat_v = float(row['Latitude'])
                    lon_v = float(row['Longitude'])
                    utmx, utmy = warp_transform('EPSG:4326', 'EPSG:32643', [lon_v], [lat_v])
                    w_v = float(row['Mouth Width (m)']) if not pd.isna(row['Mouth Width (m)']) else 0.0
                    e_shift = float(row['East Shift (m)']) if not pd.isna(row['East Shift (m)']) else 0.0
                    n_shift = float(row['North Shift (m)']) if not pd.isna(row['North Shift (m)']) else 0.0

                    base_entry = lookup.get(y, {})
                    lookup[y] = {
                        "has_data": True,
                        "utm_x": float(utmx[0]),
                        "utm_y": float(utmy[0]),
                        "lat": lat_v,
                        "lon": lon_v,
                        "width_m": w_v,
                        "east_shift_m": e_shift,
                        "north_shift_m": n_shift,
                        "mouth_row": base_entry.get("mouth_row", 0.0),
                        "mouth_col": base_entry.get("mouth_col", 0.0),
                    }
                except Exception as e:
                    print(f"[DeviationService] Error parsing row for year {y}: {e}")

        # Explicitly ensure 1995 is flagged as No Data Available (Zero)
        lookup[1995] = {
            "has_data": False,
            "utm_x": 0.0,
            "utm_y": 0.0,
            "lat": 0.0,
            "lon": 0.0,
            "width_m": 0.0,
            "east_shift_m": 0.0,
            "north_shift_m": 0.0,
            "mouth_row": 0.0,
            "mouth_col": 0.0,
        }

        return lookup

    def get_available_years(self):
        """Returns sorted list of observation years available with satellite rasters."""
        years = set()
        search_dirs = [
            dataset_config.river_mouth_dir,
            dataset_config.ndwi_dir,
            dataset_config.rgb_dir,
            dataset_config.binary_dir,
            self.raster_dir,
            os.path.join(self.raster_dir, "Binary"),
            os.path.join(self.raster_dir, "NDWI_images"),
            os.path.join(self.raster_dir, "image_RGB"),
        ]
        for s_dir in search_dirs:
            if s_dir and os.path.exists(s_dir):
                for f in os.listdir(s_dir):
                    if f.endswith(".tif"):
                        for y in range(1980, 2035):
                            if f"_{y}." in f or f"_{y}(" in f:
                                years.add(y)
        return sorted(list(years))

    def get_year_mouth_data(self, year: int):
        """
        Loads georeferenced raster for the year, calculates water area in km^2,
        finds estuarine inlet mouth centroid coordinates in UTM meters,
        reprojects to WGS84, and builds colorized thumbnail QPixmap.
        """
        if year in self._year_cache:
            return self._year_cache[year]

        if not self.raster_dir:
            return None

        # Search across configured dataset directories
        bin_candidates = [
            os.path.join(dataset_config.binary_dir, f"Binary_{year}_Clean.tif"),
            os.path.join(dataset_config.binary_dir, f"Binary_{year}.tif"),
            os.path.join(self.raster_dir, "Binary", f"Binary_{year}_Clean.tif"),
            os.path.join(self.raster_dir, "Binary", f"Binary_{year}.tif"),
            os.path.join(self.raster_dir, f"Binary_{year}.tif"),
        ]
        ndwi_candidates = [
            os.path.join(dataset_config.ndwi_dir, f"NDWI_{year}.tif"),
            os.path.join(dataset_config.river_mouth_dir, f"NDWI_{year}.tif"),
            os.path.join(self.raster_dir, "NDWI_images", f"NDWI_{year}.tif"),
            os.path.join(self.raster_dir, f"NDWI_{year}.tif"),
        ]
        rgb_candidates = [
            os.path.join(dataset_config.rgb_dir, f"RGB_{year}.tif"),
            os.path.join(dataset_config.river_mouth_dir, f"RGB_{year}.tif"),
            os.path.join(self.raster_dir, "image_RGB", f"RGB_{year}.tif"),
            os.path.join(self.raster_dir, f"RGB_{year}.tif"),
        ]

        target_f = None
        for b in bin_candidates:
            if os.path.exists(b):
                target_f = b
                break
        if not target_f:
            for n in ndwi_candidates:
                if os.path.exists(n):
                    target_f = n
                    break
        if not target_f:
            for r in rgb_candidates:
                if os.path.exists(r):
                    target_f = r
                    break

        if not target_f or not os.path.exists(target_f):
            return None

        with rasterio.open(target_f) as src:
            res_m = src.res[0] if src.res[0] > 1.0 else 30.0
            
            # Check if raster coordinates are in degrees (EPSG:4326) or UTM (EPSG:32643)
            is_deg = (src.crs and src.crs.to_epsg() == 4326) or (src.bounds.right < 180.0)
            if is_deg:
                aoi_l, aoi_b, aoi_r, aoi_t = 74.68, 13.43, 74.72, 13.47
            else:
                aoi_l, aoi_b, aoi_r, aoi_t = self.aoi_left, self.aoi_bottom, self.aoi_right, self.aoi_top

            # Check if raster needs window crop to the common estuarine mouth AOI
            if src.bounds.left >= aoi_l - 100 and src.bounds.right <= aoi_r + 100:
                data = src.read(1)
                tform = src.transform
                w_shape = data.shape
            else:
                w_left = max(src.bounds.left, aoi_l)
                w_bottom = max(src.bounds.bottom, aoi_b)
                w_right = min(src.bounds.right, aoi_r)
                w_top = min(src.bounds.top, aoi_t)
                try:
                    if w_left < w_right and w_bottom < w_top:
                        win = from_bounds(w_left, w_bottom, w_right, w_top, src.transform)
                        data = src.read(1, window=win)
                        tform = src.window_transform(win)
                        w_shape = data.shape
                    else:
                        data = src.read(1)
                        tform = src.transform
                        w_shape = data.shape
                except Exception:
                    data = src.read(1)
                    tform = src.transform
                    w_shape = data.shape

            if "Binary" in target_f:
                water = (data == 1)
            else:
                valid = ~np.isnan(data) & (data != src.nodata if src.nodata is not None else True)
                water = valid & (data > 0.05)

            pixel_count = int(np.sum(water))
            area_km2 = float(pixel_count * (res_m * res_m) / 1e6)

            rows, cols = np.where(water)
            h, w = w_shape

            # Determine Mouth Coordinates from verified ground truth or raster
            has_data = True
            if year == 1995 or (year in self.fo_lookup and not self.fo_lookup[year].get("has_data", True)):
                # Year 1995: Strictly zero / no measurement data available
                mouth_x, mouth_y = 0.0, 0.0
                lon_wgs84, lat_wgs84 = 0.0, 0.0
                opening_width_m = 0.0
                has_data = False
            elif year in self.fo_lookup and self.fo_lookup[year].get("has_data", True):
                gt = self.fo_lookup[year]
                mouth_x = gt["utm_x"]
                mouth_y = gt["utm_y"]
                lon_wgs84 = gt["lon"]
                lat_wgs84 = gt["lat"]
                opening_width_m = gt["width_m"]
            else:
                opening_width_m = 0.0
                mouth_x, mouth_y = 466900.0, 1487100.0
                if len(rows) > 0:
                    xs, ys = rasterio.transform.xy(tform, rows, cols)
                    xs = np.array(xs)
                    ys = np.array(ys)
                    if is_deg:
                        utmx, utmy = warp_transform('EPSG:4326', 'EPSG:32643', xs.tolist(), ys.tolist())
                        xs = np.array(utmx)
                        ys = np.array(utmy)
                    inlet_mask = (xs >= 466200) & (xs <= 467800) & (ys >= 1486000) & (ys <= 1488500)
                    if np.sum(inlet_mask) > 10:
                        mouth_x = float(np.mean(xs[inlet_mask]))
                        mouth_y = float(np.mean(ys[inlet_mask]))
                    else:
                        mouth_x = float(np.mean(xs))
                        mouth_y = float(np.mean(ys))
                lons, lats = warp_transform('EPSG:32643', 'EPSG:4326', [mouth_x], [mouth_y])
                lon_wgs84 = float(lons[0])
                lat_wgs84 = float(lats[0])

            # Map coordinates to image pixels for the thumbnail overlay
            inv_t = ~tform
            if is_deg:
                px_col, px_row = inv_t * (lon_wgs84, lat_wgs84)
            else:
                px_col, px_row = inv_t * (mouth_x, mouth_y)
            pixel_mouth_x = int(np.clip(px_col, 0, w - 1))
            pixel_mouth_y = int(np.clip(px_row, 0, h - 1))

            # Render high-contrast estuarine channel QPixmap
            qimg = QImage(w, h, QImage.Format_ARGB32)
            qimg.fill(QColor(8, 43, 38, 255))  # Dark emerald background

            water_color = QColor(0, 191, 165, 240) if year < 2025 else QColor(30, 136, 229, 240)
            for r_idx in range(h):
                for c_idx in range(w):
                    if water[r_idx, c_idx]:
                        qimg.setPixelColor(c_idx, r_idx, water_color)

            # Paint bullseye target marker on the river mouth throat
            painter = QPainter(qimg)
            painter.setRenderHint(QPainter.Antialiasing)
            marker_color = QColor(233, 184, 102) if year < 2025 else QColor(200, 232, 137)
            painter.setPen(QPen(marker_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(pixel_mouth_x, pixel_mouth_y), 7, 7)
            painter.setBrush(QBrush(marker_color))
            painter.drawEllipse(QPointF(pixel_mouth_x, pixel_mouth_y), 2.5, 2.5)
            painter.end()

            pixmap = QPixmap.fromImage(qimg)

            data_obj = {
                "year": year,
                "water_area_km2": area_km2,
                "pixel_count": pixel_count,
                "mouth_utm_x": mouth_x,
                "mouth_utm_y": mouth_y,
                "pixel_mouth_x": pixel_mouth_x,
                "pixel_mouth_y": pixel_mouth_y,
                "mouth_lon": lon_wgs84,
                "mouth_lat": lat_wgs84,
                "is_projection": (year >= 2025),
                "obs_type": "AI Projection" if year >= 2025 else "Ground Truth",
                "opening_width_m": opening_width_m,
                "has_data": has_data,
                "pixmap": pixmap,
                "width": w,
                "height": h,
                "resolution_m": res_m,
                "crs": "EPSG:32643"
            }
            self._year_cache[year] = data_obj
            return data_obj

    def get_compass_direction(self, dx: float, dy: float):
        """Calculates azimuth bearing in degrees and 16-point cardinal direction."""
        angle_rad = np.arctan2(dx, dy)
        angle_deg = float(np.degrees(angle_rad) % 360.0)

        headings = [
            "North", "North-Northeast", "Northeast", "East-Northeast",
            "East", "East-Southeast", "Southeast", "South-Southeast",
            "South", "South-Southwest", "Southwest", "West-Southwest",
            "West", "West-Northwest", "Northwest", "North-Northwest"
        ]
        idx = int((angle_deg + 11.25) / 22.5) % 16
        return headings[idx], angle_deg

    def calculate_deviation(self, base_year: int, target_year: int):
        """
        Calculates river-mouth displacement, direction, water-body change,
        and full timeseries relative to the base year.
        """
        base_data = self.get_year_mouth_data(base_year)
        target_data = self.get_year_mouth_data(target_year)

        if not base_data or not target_data:
            return None

        dx = target_data["mouth_utm_x"] - base_data["mouth_utm_x"]
        dy = target_data["mouth_utm_y"] - base_data["mouth_utm_y"]
        dist_m = float(np.sqrt(dx**2 + dy**2))
        d_lat = target_data["mouth_lat"] - base_data["mouth_lat"]
        d_lon = target_data["mouth_lon"] - base_data["mouth_lon"]

        if dist_m < 1.0:
            dir_name = "Stationary / Baseline"
            dir_deg = 0.0
            dir_label = "No Significant Shift (< 1 m)"
        else:
            dir_name, dir_deg = self.get_compass_direction(dx, dy)
            dir_label = f"{dir_name} ({dir_deg:.0f}°)"

        area_change_km2 = target_data["water_area_km2"] - base_data["water_area_km2"]
        area_change_pct = (area_change_km2 / max(0.001, base_data["water_area_km2"])) * 100.0

        dt = abs(target_year - base_year)
        annual_rate_m_yr = (dist_m / dt) if dt > 0 else 0.0

        all_years = self.get_available_years()
        timeseries = []
        for y in all_years:
            yd = self.get_year_mouth_data(y)
            if not yd:
                continue
            has_data = yd.get("has_data", True) and (y != 1995)
            if not has_data:
                ydx = 0.0
                ydy = 0.0
                ydist = 0.0
                yd_lat = 0.0
                yd_lon = 0.0
                ydir = "No Data (0 m)"
                ydeg = 0.0
                yrate = 0.0
            else:
                ydx = yd["mouth_utm_x"] - base_data["mouth_utm_x"]
                ydy = yd["mouth_utm_y"] - base_data["mouth_utm_y"]
                ydist = float(np.sqrt(ydx**2 + ydy**2))
                yd_lat = yd["mouth_lat"] - base_data["mouth_lat"]
                yd_lon = yd["mouth_lon"] - base_data["mouth_lon"]
                ydir, ydeg = self.get_compass_direction(ydx, ydy) if ydist >= 1.0 else ("--", 0.0)
                ydt = abs(y - base_year)
                yrate = (ydist / ydt) if ydt > 0 else 0.0

            d_area = yd["water_area_km2"] - base_data["water_area_km2"]

            fo_info = self.fo_lookup.get(y, {})
            timeseries.append({
                "year": y,
                "is_projection": yd["is_projection"],
                "obs_type": yd["obs_type"],
                "mouth_utm_x": yd["mouth_utm_x"],
                "mouth_utm_y": yd["mouth_utm_y"],
                "mouth_lon": yd["mouth_lon"],
                "mouth_lat": yd["mouth_lat"],
                "has_data": has_data,
                "displacement_m": ydist,
                "difference_meters": ydist,
                "dx_m": ydx,
                "dy_m": ydy,
                "d_lat": yd_lat,
                "d_lon": yd_lon,
                "east_shift_m": fo_info.get("east_shift_m", 0.0),
                "north_shift_m": fo_info.get("north_shift_m", 0.0),
                "direction": ydir if (has_data and ydist >= 1.0) else ("No Data (0m)" if not has_data else "--"),
                "azimuth_deg": ydeg if (has_data and ydist >= 1.0) else 0.0,
                "water_area_km2": yd["water_area_km2"],
                "area_change_km2": d_area,
                "rate_m_yr": yrate,
                "opening_width_m": yd.get("opening_width_m", 0.0),
                "is_base": (y == base_year),
                "is_target": (y == target_year)
            })

        return {
            "base_year": base_year,
            "target_year": target_year,
            "base_data": base_data,
            "target_data": target_data,
            "displacement_m": dist_m,
            "difference_meters": dist_m,
            "dx_m": dx,
            "dy_m": dy,
            "d_lat": d_lat,
            "d_lon": d_lon,
            "direction_label": dir_label,
            "direction_name": dir_name,
            "azimuth_deg": dir_deg,
            "base_water_area_km2": base_data["water_area_km2"],
            "target_water_area_km2": target_data["water_area_km2"],
            "area_change_km2": area_change_km2,
            "area_change_pct": area_change_pct,
            "annual_rate_m_yr": annual_rate_m_yr,
            "time_interval_years": dt,
            "is_target_projection": target_data["is_projection"],
            "timeseries": timeseries
        }

    def export_csv(self, base_year: int, target_year: int, save_path: str):
        dev = self.calculate_deviation(base_year, target_year)
        if not dev:
            return False, "Could not compute deviation for export."

        min_y = min(base_year, target_year)
        max_y = max(base_year, target_year)

        rows = []
        for row in dev["timeseries"]:
            if min_y <= row["year"] <= max_y:
                rows.append({
                    "Year": row["year"],
                    "Observation Type": row["obs_type"],
                    "Latitude (WGS84)": f"{row['mouth_lat']:.6f}",
                    "Longitude (WGS84)": f"{row['mouth_lon']:.6f}",
                    "ΔLatitude (deg)": f"{row['d_lat']:+.6f}",
                    "ΔLongitude (deg)": f"{row['d_lon']:+.6f}",
                    "ΔEasting / ΔX (m)": f"{row['dx_m']:+.2f}",
                    "ΔNorthing / ΔY (m)": f"{row['dy_m']:+.2f}",
                    "Difference in Meters (m)": f"{row['displacement_m']:.2f}",
                    "Displacement Direction": row["direction"],
                    "Azimuth Bearing (deg)": f"{row['azimuth_deg']:.1f}",
                    "Water Body Area (km²)": f"{row['water_area_km2']:.2f}",
                    "Area Change from Base (km²)": f"{row['area_change_km2']:+.2f}",
                    "Migration Rate (m/yr)": f"{row['rate_m_yr']:.2f}",
                    "Opening Width (m)": f"{row.get('opening_width_m', 0.0):.1f}",
                    "River Mouth UTM Easting (m)": f"{row['mouth_utm_x']:.1f}",
                    "River Mouth UTM Northing (m)": f"{row['mouth_utm_y']:.1f}",
                    "CRS": "EPSG:32643",
                    "Baseline Reference Year": base_year
                })

        try:
            df = pd.DataFrame(rows)
            df.to_csv(save_path, index=False)
            return True, f"Successfully exported deviation table to:\n{save_path}"
        except Exception as e:
            return False, f"Failed to save CSV: {str(e)}"

    def export_geojson(self, base_year: int, target_year: int, save_path: str):
        dev = self.calculate_deviation(base_year, target_year)
        if not dev:
            return False, "Could not compute deviation for GeoJSON export."

        features = []
        b = dev["base_data"]
        t = dev["target_data"]

        # Feature 1: Base Year Mouth Point
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [b["mouth_lon"], b["mouth_lat"]]
            },
            "properties": {
                "role": "baseline_mouth",
                "year": base_year,
                "obs_type": b["obs_type"],
                "water_area_km2": b["water_area_km2"],
                "utm_easting_m": b["mouth_utm_x"],
                "utm_northing_m": b["mouth_utm_y"]
            }
        })

        # Feature 2: Target Year Mouth Point
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [t["mouth_lon"], t["mouth_lat"]]
            },
            "properties": {
                "role": "target_mouth",
                "year": target_year,
                "obs_type": t["obs_type"],
                "water_area_km2": t["water_area_km2"],
                "utm_easting_m": t["mouth_utm_x"],
                "utm_northing_m": t["mouth_utm_y"]
            }
        })

        # Feature 3: Displacement Vector LineString
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [b["mouth_lon"], b["mouth_lat"]],
                    [t["mouth_lon"], t["mouth_lat"]]
                ]
            },
            "properties": {
                "role": "displacement_vector",
                "base_year": base_year,
                "target_year": target_year,
                "displacement_m": dev["displacement_m"],
                "direction": dev["direction_label"],
                "azimuth_deg": dev["azimuth_deg"],
                "annual_rate_m_yr": dev["annual_rate_m_yr"],
                "water_area_change_km2": dev["area_change_km2"]
            }
        })

        # Feature 4..N: All other observation years within selected period
        min_y = min(base_year, target_year)
        max_y = max(base_year, target_year)
        for item in dev["timeseries"]:
            if min_y <= item["year"] <= max_y and item["year"] not in [base_year, target_year]:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [item["mouth_lon"], item["mouth_lat"]]
                    },
                    "properties": {
                        "role": "observation_mouth",
                        "year": item["year"],
                        "obs_type": item["obs_type"],
                        "displacement_from_base_m": item["displacement_m"],
                        "direction": item["direction"],
                        "water_area_km2": item["water_area_km2"]
                    }
                })

        geojson = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
            },
            "features": features
        }

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2)
            return True, f"Successfully exported GIS GeoJSON vector to:\n{save_path}"
        except Exception as e:
            return False, f"Failed to save GeoJSON: {str(e)}"

    def export_report(self, base_year: int, target_year: int, save_path: str):
        dev = self.calculate_deviation(base_year, target_year)
        if not dev:
            return False, "Could not compute deviation for report export."

        report = f"""# Suvarna River Estuary - River-Mouth Deviation & Morphodynamic Analysis Report

## 1. Study Parameters
- **Study Location**: Kodi Bengre, Udupi, Karnataka, India
- **Base Year**: {base_year} ({dev['base_data']['obs_type']})
- **Target Year**: {target_year} ({dev['target_data']['obs_type']})
- **Time Interval**: {dev['time_interval_years']} years
- **Projected Coordinate Reference System**: EPSG:32643 (WGS 84 / UTM Zone 43N)
- **Spatial Pixel Resolution**: 30.0 metres (Landsat Multi-Spectral / Deep Learning U-Net)

## 2. Key Geomorphological Measurements
- **Measured River-Mouth Displacement**: {dev['displacement_m']:.2f} metres
- **Displacement Vector Direction**: {dev['direction_label']}
- **Easting Shift (ΔX)**: {dev['dx_m']:+.2f} metres
- **Northing Shift (ΔY)**: {dev['dy_m']:+.2f} metres
- **Average Annual Migration Rate**: {dev['annual_rate_m_yr']:.2f} m/year
- **Base Year Estuarine Water Area**: {dev['base_water_area_km2']:.2f} km²
- **Target Year Estuarine Water Area**: {dev['target_water_area_km2']:.2f} km²
- **Net Water-Body Area Change**: {dev['area_change_km2']:+.2f} km² ({dev['area_change_pct']:+.1f}%)

## 3. Spatial Coordinates
- **Base Year ({base_year}) Mouth**:
  - UTM Zone 43N: {dev['base_data']['mouth_utm_x']:.1f} m E, {dev['base_data']['mouth_utm_y']:.1f} m N
  - Geographic Coordinates: {dev['base_data']['mouth_lat']:.6f}°N, {dev['base_data']['mouth_lon']:.6f}°E
- **Target Year ({target_year}) Mouth**:
  - UTM Zone 43N: {dev['target_data']['mouth_utm_x']:.1f} m E, {dev['target_data']['mouth_utm_y']:.1f} m N
  - Geographic Coordinates: {dev['target_data']['mouth_lat']:.6f}°N, {dev['target_data']['mouth_lon']:.6f}°E

## 4. Methodology Documentation
1. Multi-spectral Landsat surface reflectance and calibrated water indices (NDWI > 0.05 / U-Net binary masks) were clipped to the fixed estuarine mouth AOI.
2. Coordinates were projected in UTM Zone 43N (`EPSG:32643`), preserving true Euclidean distances in metres without projection distortion.
3. The river-mouth inlet throat centroid was tracked between the Kodi Bengre sandspit barrier and mainland tidal inlet.
4. Future projections (2025–2026) are labeled as AI Projections (U-Net Deep Learning) to clearly separate empirical observations from predictive modeling.
"""
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
            return True, f"Successfully exported scientific summary report to:\n{save_path}"
        except Exception as e:
            return False, f"Failed to save report: {str(e)}"


deviation_service = DeviationService()

