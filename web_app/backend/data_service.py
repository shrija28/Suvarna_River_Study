"""
Centralized Data & Session State Service for Web Application
Estuarine Mouth Dynamics - Path Deviation Prediction System

Manages active temporal configuration, AOI spatial bounds,
and river-mouth gallery metadata.
"""

import os
from typing import Dict, List, Any, Optional

from .dataset_config import dataset_config
from .deviation_service import deviation_service
from .lulc_service import lulc_service


class SuvarnaDataService:
    def __init__(self):
        self._base_year = 1989
        self._target_year = 2000
        self._aoi: Optional[Dict[str, float]] = None
        self._location_name = "Kodi Bengre, Udupi, Karnataka, India"
        self._lat = 13.4380
        self._lon = 74.6980

    def set_year_range(self, base_year: int, target_year: int):
        try:
            b = max(1989, min(2026, int(base_year)))
            t = max(1989, min(2026, int(target_year)))
            if b > t:
                t = b
            self._base_year = b
            self._target_year = t
        except (ValueError, TypeError):
            pass

    def get_base_year(self) -> int:
        return self._base_year

    def get_target_year(self) -> int:
        return self._target_year

    def get_selected_years(self) -> List[int]:
        return list(range(self._base_year, self._target_year + 1))

    def set_aoi(self, north: float, south: float, east: float, west: float):
        self._aoi = {
            "north": float(north),
            "south": float(south),
            "east": float(east),
            "west": float(west),
        }

    def clear_aoi(self):
        self._aoi = None

    def get_aoi(self) -> Optional[Dict[str, float]]:
        return self._aoi

    def set_location(self, location_name: str, lat: float, lon: float):
        self._location_name = location_name
        self._lat = float(lat)
        self._lon = float(lon)

    def get_location(self) -> Dict[str, Any]:
        return {
            "location_name": self._location_name,
            "lat": self._lat,
            "lon": self._lon,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "base_year": self._base_year,
            "target_year": self._target_year,
            "selected_years": self.get_selected_years(),
            "aoi": self._aoi,
            "location": self.get_location(),
        }

    def get_gallery_items(self, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns gallery card metadata for the requested range (or currently selected years)."""
        if start_year is None:
            start_year = self._base_year
        if end_year is None:
            end_year = self._target_year

        gt = deviation_service._load_ground_truth()
        lulc_records = {r["year"]: r for r in lulc_service.load_master_counts()}

        items: List[Dict[str, Any]] = []
        for y in range(start_year, end_year + 1):
            if y < 1989 or y > 2026:
                continue

            info = gt.get(y, {})
            l_info = lulc_records.get(y, {})

            has_data = info.get("has_data", True) and (y != 1995)
            width_m = info.get("width_m") if has_data else None
            water_km2 = l_info.get("water_km2", info.get("water_area_km2", 12.5))

            # Check if actual PNG image exists
            img_file = self.get_river_mouth_image_path(y)
            has_img = img_file is not None and os.path.isfile(img_file)

            items.append({
                "year": y,
                "has_data": has_data,
                "has_image": has_img,
                "image_url": f"/api/river-mouth/image/{y}",
                "water_km2": water_km2,
                "width_m": width_m,
                "status": "Measured" if has_data else ("No Data (1995)" if y == 1995 else "Projection"),
                "is_projection": (y >= 2025),
            })

        return items

    def get_river_mouth_image_path(self, year: int) -> Optional[str]:
        """Resolves local filepath for a specific year's river mouth image."""
        candidates = [
            os.path.join(dataset_config.first_opening_dir, f"First_Opening_{year}.png"),
            os.path.join(dataset_config.data_dir, "river mouth images", "First_Opening", f"First_Opening_{year}.png"),
            os.path.join(dataset_config.project_root, "data", "river mouth images", "First_Opening", f"First_Opening_{year}.png"),
            os.path.join(dataset_config.root_dir, "river mouth images", "First_Opening", f"First_Opening_{year}.png"),
            os.path.join(dataset_config.project_root, "SuvarnaProject_data", "river mouth images", "First_Opening", f"First_Opening_{year}.png"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None


data_service = SuvarnaDataService()
