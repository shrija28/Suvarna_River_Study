"""
LULC Data Service for Web Application
Estuarine Mouth Dynamics - Path Deviation Prediction System
Connects genuine multi-decadal Land Use and Land Cover (LULC) datasets (1989-2026).
"""

import os
import csv
from typing import Dict, List, Any, Optional

from .dataset_config import dataset_config


class LULCService:
    def __init__(self):
        self._cached_records: Optional[List[Dict[str, Any]]] = None
        self._cached_by_year: Optional[Dict[int, Dict[str, Any]]] = None

    def invalidate_cache(self):
        self._cached_records = None
        self._cached_by_year = None

    def load_master_counts(self) -> List[Dict[str, Any]]:
        """Loads and parses LULC_Master_Counts.csv."""
        if self._cached_records is not None:
            return self._cached_records

        csv_path = dataset_config.lulc_master_csv
        records: List[Dict[str, Any]] = []
        by_year: Dict[int, Dict[str, Any]] = {}

        if csv_path and os.path.isfile(csv_path):
            try:
                with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            y_str = row.get("year") or row.get("Year") or ""
                            if not y_str:
                                continue
                            y = int(float(y_str))

                            veg_km2 = round(float(row.get("vegetation_km2", 0.0) or 0.0), 2)
                            veg_pct = round(float(row.get("vegetation_percent", 0.0) or 0.0), 1)
                            veg_pix = int(float(row.get("vegetation_pixels", 0) or 0))

                            water_km2 = round(float(row.get("water_km2", 0.0) or 0.0), 2)
                            water_pct = round(float(row.get("water_percent", 0.0) or 0.0), 1)
                            water_pix = int(float(row.get("water_pixels", 0) or 0))

                            barren_km2 = round(float(row.get("barren_km2", 0.0) or 0.0), 2)
                            barren_pct = round(float(row.get("barren_percent", 0.0) or 0.0), 1)
                            barren_pix = int(float(row.get("barren_pixels", 0) or 0))

                            built_km2 = round(float(row.get("builtup_km2", 0.0) or 0.0), 2)
                            built_pct = round(float(row.get("builtup_percent", 0.0) or 0.0), 1)
                            built_pix = int(float(row.get("builtup_pixels", 0) or 0))

                            tot_km2 = round(float(row.get("total_km2", 0.0) or 0.0), 2)

                            item = {
                                "year": y,
                                "vegetation_km2": veg_km2,
                                "vegetation_pct": veg_pct,
                                "vegetation_pixels": veg_pix,
                                "barren_km2": barren_km2,
                                "barren_pct": barren_pct,
                                "barren_pixels": barren_pix,
                                "water_km2": water_km2,
                                "water_pct": water_pct,
                                "water_pixels": water_pix,
                                "builtup_km2": built_km2,
                                "builtup_pct": built_pct,
                                "builtup_pixels": built_pix,
                                "total_km2": tot_km2,
                                "classes": {
                                    "vegetation": {
                                        "name": "Vegetation",
                                        "area_km2": veg_km2,
                                        "percentage": veg_pct,
                                        "pixel_count": veg_pix,
                                        "color": "#2E7D32"
                                    },
                                    "water_body": {
                                        "name": "Water Body",
                                        "area_km2": water_km2,
                                        "percentage": water_pct,
                                        "pixel_count": water_pix,
                                        "color": "#1E88E5"
                                    },
                                    "barren_land": {
                                        "name": "Barren Land",
                                        "area_km2": barren_km2,
                                        "percentage": barren_pct,
                                        "pixel_count": barren_pix,
                                        "color": "#E6C654"
                                    },
                                    "built_up": {
                                        "name": "Built-up Area",
                                        "area_km2": built_km2,
                                        "percentage": built_pct,
                                        "pixel_count": built_pix,
                                        "color": "#D84315"
                                    }
                                }
                            }
                            records.append(item)
                            by_year[y] = item
                        except Exception as e:
                            continue
            except Exception as e:
                print(f"Error reading LULC master CSV: {e}")

        records.sort(key=lambda r: r["year"])
        self._cached_records = records
        self._cached_by_year = by_year
        return records

    def get_all_master_records(self) -> List[Dict[str, Any]]:
        return self.load_master_counts()

    def get_available_years(self) -> List[int]:
        recs = self.load_master_counts()
        return [r["year"] for r in recs]

    def get_master_record(self, year: int) -> Optional[Dict[str, Any]]:
        self.load_master_counts()
        if self._cached_by_year and year in self._cached_by_year:
            return self._cached_by_year[year]
        return None

    def get_lulc_image_path(self, year: int) -> Optional[str]:
        candidates = [
            os.path.join(dataset_config.lulc_dir, f"LULC_{year}.png"),
            os.path.join(dataset_config.root_dir, "LULC_images", f"LULC_{year}.png"),
            os.path.join(dataset_config.project_root, "SuvarnaProject_data", "LULC_images", f"LULC_{year}.png"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None


lulc_service = LULCService()
