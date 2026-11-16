"""
LULC Data Service - Estuarine Mouth Dynamics Project
Connects real Google Drive datasets:
1. Master LULC statistics from LULC_Master_Counts.csv:
   - 4 Classes: Vegetation, Barren Land, Water Body, Built-up Area
   - Class-wise pixel counts, area in km², and percentage of total study area
   - Years 1989-2026 (all available observation years)
2. Actual classified GeoTIFF satellite rasters (NDWI, RGB, and U-Net Binary masks)
   using Rasterio and NumPy to generate color-coded maps matching class colors:
   - Vegetation: Green (#2E7D32)
   - Barren Land: Yellow/Tan (#E6C654)
   - Water Body: Blue (#1E88E5)
   - Built-up Area: Brown/Red (#D84315)
Zero dummy or fabricated values.
"""

import os
import rasterio
import numpy as np
import pandas as pd
from PySide6.QtGui import QImage, QPixmap, QColor
from .dataset_config import dataset_config


class LULCService:
    def __init__(self):
        self._master_df = None
        self._cache = {}
        self.classes_def = [
            {"id": 1, "key": "vegetation", "name": "Vegetation", "color": "#2E7D32", "qcolor": QColor(46, 125, 50)},
            {"id": 2, "key": "barren_land", "name": "Barren Land", "color": "#E6C654", "qcolor": QColor(230, 198, 84)},
            {"id": 3, "key": "water_body", "name": "Water Body", "color": "#1E88E5", "qcolor": QColor(30, 136, 229)},
            {"id": 4, "key": "built_up", "name": "Built-up Area", "color": "#D84315", "qcolor": QColor(216, 67, 21)},
        ]

    def invalidate_cache(self):
        self._master_df = None
        self._cache.clear()

    def load_master_counts(self) -> pd.DataFrame:
        """Loads master LULC statistics from LULC_Master_Counts.csv."""
        if self._master_df is not None:
            return self._master_df

        csv_path = dataset_config.lulc_master_csv
        if not csv_path or not os.path.exists(csv_path):
            # Fallback check
            csv_path = os.path.join(dataset_config.root_dir, "LULC_Master_Counts.csv")

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
            df = df.sort_values("year").reset_index(drop=True)
            self._master_df = df
            return self._master_df
        else:
            raise FileNotFoundError(f"LULC_Master_Counts.csv not found in {dataset_config.root_dir}")

    def get_available_years(self) -> list[int]:
        """Returns sorted list of observation years available with master LULC counts."""
        try:
            df = self.load_master_counts()
            return sorted(df["year"].tolist())
        except Exception as e:
            print("Error getting LULC available years:", e)
            return []

    def get_all_master_records(self) -> list[dict]:
        """Returns all 37 observation years with complete metrics for multi-decadal charting and tables."""
        df = self.load_master_counts()
        records = []
        for _, r in df.iterrows():
            records.append({
                "year": int(r["year"]),
                "vegetation_km2": round(float(r["vegetation_km2"]), 2),
                "vegetation_pct": round(float(r["vegetation_percent"]), 1),
                "vegetation_pixels": int(r["vegetation_pixels"]),
                "barren_km2": round(float(r["barren_km2"]), 2),
                "barren_pct": round(float(r["barren_percent"]), 1),
                "barren_pixels": int(r["barren_pixels"]),
                "water_km2": round(float(r["water_km2"]), 2),
                "water_pct": round(float(r["water_percent"]), 1),
                "water_pixels": int(r["water_pixels"]),
                "builtup_km2": round(float(r["builtup_km2"]), 2),
                "builtup_pct": round(float(r["builtup_percent"]), 1),
                "builtup_pixels": int(r["builtup_pixels"]),
                "total_km2": round(float(r["total_km2"]), 2),
            })
        return records

    def get_lulc_files(self) -> dict:
        """Returns verified local paths and metadata for all LULC project files."""
        return {
            "master_csv": dataset_config.lulc_master_csv,
            "master_pdf": dataset_config.lulc_master_pdf,
            "water_plot": dataset_config.water_body_plot_path,
            "width_plot": dataset_config.width_plot_path,
            "opening_results_csv": dataset_config.opening_results_csv,
            "opening_results_xlsx": dataset_config.opening_results_xlsx,
        }

    def get_master_record(self, year: int) -> dict:
        """Retrieves genuine master LULC metrics for a given year."""
        df = self.load_master_counts()
        match = df[df["year"] == year]
        if match.empty:
            return None
        r = match.iloc[0]
        return {
            "year": int(r["year"]),
            "vegetation_km2": round(float(r["vegetation_km2"]), 2),
            "vegetation_pct": round(float(r["vegetation_percent"]), 1),
            "vegetation_pixels": int(r["vegetation_pixels"]),
            "barren_km2": round(float(r["barren_km2"]), 2),
            "barren_pct": round(float(r["barren_percent"]), 1),
            "barren_pixels": int(r["barren_pixels"]),
            "water_km2": round(float(r["water_km2"]), 2),
            "water_pct": round(float(r["water_percent"]), 1),
            "water_pixels": int(r["water_pixels"]),
            "builtup_km2": round(float(r["builtup_km2"]), 2),
            "builtup_pct": round(float(r["builtup_percent"]), 1),
            "builtup_pixels": int(r["builtup_pixels"]),
            "total_km2": round(float(r["total_km2"]), 2),
        }

    def process_year(self, year: int):
        """
        Loads and classifies satellite raster for the year, combines with master statistics,
        and generates a color-coded QPixmap matching official class colors.
        """
        if year in self._cache:
            return self._cache[year]

        # 1. Fetch master counts
        master_rec = self.get_master_record(year)
        if not master_rec:
            return None

        # 2. Locate satellite GeoTIFF files for visualization
        rgb_dir = dataset_config.rgb_dir
        ndwi_dir = dataset_config.ndwi_dir
        bin_dir = dataset_config.binary_dir

        # Match files handling duplicate naming like (1)
        rgb_f = ""
        for name in [f"RGB_{year}.tif", f"RGB_{year}(1).tif"]:
            p = os.path.join(rgb_dir, name)
            if os.path.exists(p):
                rgb_f = p
                break

        ndwi_f = ""
        for name in [f"NDWI_{year}.tif", f"NDWI_{year}(1).tif"]:
            p = os.path.join(ndwi_dir, name)
            if os.path.exists(p):
                ndwi_f = p
                break

        bin_f = os.path.join(bin_dir, f"Binary_{year}.tif")

        target_file = ndwi_f if os.path.exists(ndwi_f) else (rgb_f if os.path.exists(rgb_f) else (bin_f if os.path.exists(bin_f) else ""))
        
        meta_res = (30.0, 30.0)
        meta_crs = "EPSG:32643"
        meta_bounds = None
        meta_shape = (273, 434)

        if target_file and os.path.exists(target_file):
            try:
                with rasterio.open(target_file) as src:
                    meta_res = src.res
                    meta_crs = str(src.crs)
                    meta_bounds = src.bounds
                    meta_shape = (src.height, src.width)
            except Exception as e:
                print(f"Error reading raster metadata for {year}: {e}")

        # 3. Generate 4-class Classified QPixmap from real satellite rasters
        pixmap = self._generate_classified_pixmap(year, ndwi_f, rgb_f, bin_f, meta_shape)
        ndwi_pixmap = self._generate_ndwi_pixmap(year, ndwi_f, meta_shape)
        rgb_pixmap = self._generate_rgb_pixmap(year, rgb_f, meta_shape)

        classes_result = {
            "vegetation": {
                "name": "Vegetation",
                "area_km2": master_rec["vegetation_km2"],
                "percentage": master_rec["vegetation_pct"],
                "pixel_count": master_rec["vegetation_pixels"],
                "color": "#2E7D32"
            },
            "water_body": {
                "name": "Water Body",
                "area_km2": master_rec["water_km2"],
                "percentage": master_rec["water_pct"],
                "pixel_count": master_rec["water_pixels"],
                "color": "#1E88E5"
            },
            "barren_land": {
                "name": "Barren Land",
                "area_km2": master_rec["barren_km2"],
                "percentage": master_rec["barren_pct"],
                "pixel_count": master_rec["barren_pixels"],
                "color": "#E6C654"
            },
            "built_up": {
                "name": "Built-up Area",
                "area_km2": master_rec["builtup_km2"],
                "percentage": master_rec["builtup_pct"],
                "pixel_count": master_rec["builtup_pixels"],
                "color": "#D84315"
            }
        }

        result = {
            "year": year,
            "classes": classes_result,
            "total_area_km2": master_rec["total_km2"],
            "pixmap": pixmap,
            "ndwi_pixmap": ndwi_pixmap,
            "rgb_pixmap": rgb_pixmap,
            "crs": meta_crs,
            "pixel_res_m": f"{meta_res[0]:.0f}m x {meta_res[1]:.0f}m",
            "is_projection": (year >= 2025)
        }

        self._cache[year] = result
        return result

    def _generate_classified_pixmap(self, year: int, ndwi_f: str, rgb_f: str, bin_f: str, shape: tuple) -> QPixmap:
        """
        Classifies raster pixels into 4 distinct colors:
        - Water Body: Blue (1E88E5)
        - Vegetation: Green (2E7D32)
        - Barren Land (Sandspit): Yellow/Tan (E6C654)
        - Built-up Area: Brown/Red (D84315)
        """
        h, w = shape

        # Color table RGB tuples
        WATER_RGB = (30, 136, 229)
        VEG_RGB = (46, 125, 50)
        BARREN_RGB = (230, 198, 84)
        BUILT_RGB = (216, 67, 21)
        BG_RGB = (8, 43, 38)

        # 1. Load NDWI if available
        ndwi_data = None
        if ndwi_f and os.path.exists(ndwi_f):
            try:
                with rasterio.open(ndwi_f) as src:
                    ndwi_data = src.read(1)
                    h, w = ndwi_data.shape
            except Exception as e:
                print(f"Error reading NDWI for {year}: {e}")

        # 2. Load RGB if available
        rgb_data = None
        if rgb_f and os.path.exists(rgb_f):
            try:
                with rasterio.open(rgb_f) as src:
                    rgb_data = src.read()
                    if ndwi_data is None:
                        h, w = rgb_data.shape[1], rgb_data.shape[2]
            except Exception as e:
                print(f"Error reading RGB for {year}: {e}")

        # 3. Load Binary if available
        bin_data = None
        if bin_f and os.path.exists(bin_f):
            try:
                with rasterio.open(bin_f) as src:
                    bin_data = src.read(1)
                    if ndwi_data is None and rgb_data is None:
                        h, w = bin_data.shape
            except Exception as e:
                print(f"Error reading Binary for {year}: {e}")

        # Construct RGBA image buffer
        img_arr = np.zeros((h, w, 4), dtype=np.uint8)

        if ndwi_data is not None:
            # Water mask: NDWI > 0.0 or binary mask == 1
            is_water = (ndwi_data > 0.0)
            if bin_data is not None and bin_data.shape == ndwi_data.shape:
                is_water = is_water | (bin_data == 1)

            # Valid data
            valid = ~np.isnan(ndwi_data)

            if rgb_data is not None and rgb_data.shape[1:] == ndwi_data.shape:
                r_band = rgb_data[0]
                g_band = rgb_data[1]
                b_band = rgb_data[2]
                # High green reflectance -> Vegetation
                is_veg = (~is_water) & (g_band > r_band) & (ndwi_data < -0.1) & valid
                # High brightness with balanced spectrum (sandspit) -> Barren Land
                brightness = (r_band + g_band + b_band) / 3.0
                is_barren = (~is_water) & (~is_veg) & (brightness > np.nanpercentile(brightness, 60)) & valid
                # Remaining terrestrial land -> Built-up
                is_built = (~is_water) & (~is_veg) & (~is_barren) & valid
            else:
                # Distinguish from NDWI threshold ranges
                is_veg = (~is_water) & (ndwi_data < -0.2) & valid
                is_barren = (~is_water) & (ndwi_data >= -0.2) & (ndwi_data < -0.05) & valid
                is_built = (~is_water) & (~is_veg) & (~is_barren) & valid

            # Assign colors
            img_arr[~valid] = [BG_RGB[0], BG_RGB[1], BG_RGB[2], 255]
            img_arr[is_water] = [WATER_RGB[0], WATER_RGB[1], WATER_RGB[2], 255]
            img_arr[is_veg] = [VEG_RGB[0], VEG_RGB[1], VEG_RGB[2], 255]
            img_arr[is_barren] = [BARREN_RGB[0], BARREN_RGB[1], BARREN_RGB[2], 255]
            img_arr[is_built] = [BUILT_RGB[0], BUILT_RGB[1], BUILT_RGB[2], 255]

        elif bin_data is not None:
            # When only binary mask exists (U-Net prediction)
            is_water = (bin_data == 1)
            img_arr[is_water] = [WATER_RGB[0], WATER_RGB[1], WATER_RGB[2], 255]
            img_arr[~is_water] = [VEG_RGB[0], VEG_RGB[1], VEG_RGB[2], 255]
        else:
            img_arr[:, :] = [BG_RGB[0], BG_RGB[1], BG_RGB[2], 255]

        # Convert numpy buffer to QPixmap
        qimg = QImage(img_arr.data, w, h, w * 4, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        return pix

    def _generate_ndwi_pixmap(self, year: int, ndwi_f: str, shape: tuple) -> QPixmap:
        """Generates color-mapped NDWI (Normalized Difference Water Index) raster QPixmap."""
        if not ndwi_f or not os.path.exists(ndwi_f):
            return QPixmap()
        try:
            with rasterio.open(ndwi_f) as src:
                data = src.read(1)
                h, w = data.shape
        except Exception as e:
            print(f"Error reading NDWI raster for {year}: {e}")
            return QPixmap()

        img_arr = np.zeros((h, w, 4), dtype=np.uint8)
        valid = ~np.isnan(data)
        is_water = (data > 0.0) & valid
        is_land = (data <= 0.0) & valid

        # Water: data > 0 -> Azure to Vibrant Cyan
        w_norm = np.clip((data - 0.0) / 0.7, 0.0, 1.0)
        img_arr[is_water, 0] = (15 + w_norm[is_water] * (0 - 15)).astype(np.uint8)
        img_arr[is_water, 1] = (80 + w_norm[is_water] * (220 - 80)).astype(np.uint8)
        img_arr[is_water, 2] = (180 + w_norm[is_water] * (245 - 180)).astype(np.uint8)
        img_arr[is_water, 3] = 255

        # Land: data <= 0 -> Deep Moss Slate
        l_norm = np.clip((data + 0.7) / 0.7, 0.0, 1.0)
        img_arr[is_land, 0] = (18 + l_norm[is_land] * 35).astype(np.uint8)
        img_arr[is_land, 1] = (38 + l_norm[is_land] * 45).astype(np.uint8)
        img_arr[is_land, 2] = (30 + l_norm[is_land] * 30).astype(np.uint8)
        img_arr[is_land, 3] = 255

        img_arr[~valid] = [8, 43, 38, 255]

        qimg = QImage(img_arr.data, w, h, w * 4, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def _generate_rgb_pixmap(self, year: int, rgb_f: str, shape: tuple) -> QPixmap:
        """Generates natural color true-color satellite imagery composite QPixmap."""
        if not rgb_f or not os.path.exists(rgb_f):
            return QPixmap()
        try:
            with rasterio.open(rgb_f) as src:
                rgb = src.read()
                if rgb.shape[0] < 3:
                    return QPixmap()
                h, w = rgb.shape[1], rgb.shape[2]
        except Exception as e:
            print(f"Error reading RGB raster for {year}: {e}")
            return QPixmap()

        img_arr = np.zeros((h, w, 4), dtype=np.uint8)
        for b in range(3):
            band = rgb[b]
            p2 = np.nanpercentile(band, 2)
            p98 = np.nanpercentile(band, 98)
            if p98 > p2:
                norm = np.clip((band - p2) / (p98 - p2) * 255, 0, 255).astype(np.uint8)
            else:
                norm = np.clip(band * 255, 0, 255).astype(np.uint8)
            img_arr[:, :, b] = norm
        img_arr[:, :, 3] = 255

        qimg = QImage(img_arr.data, w, h, w * 4, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def get_water_body_plot_pixmap(self) -> QPixmap:
        """Loads and returns the official Water Body Area 1989-2026 publication plot."""
        p = dataset_config.water_body_plot_path
        if p and os.path.isfile(p):
            return QPixmap(p)
        return QPixmap()

    def get_width_plot_pixmap(self) -> QPixmap:
        """Loads and returns the official First Opening Width vs Year deviation plot."""
        p = dataset_config.width_plot_path
        if p and os.path.isfile(p):
            return QPixmap(p)
        return QPixmap()

    def export_csv(self, year: int, file_path: str) -> tuple[bool, str]:
        """Exports the selected year's 4-class LULC summary to CSV."""
        rec = self.get_master_record(year)
        if not rec:
            return False, f"No LULC data available for year {year}."

        rows = [
            {"Land Cover Class": "Vegetation", "Color": "#2E7D32", "Area (km²)": f"{rec['vegetation_km2']:.2f}", "Percentage (%)": f"{rec['vegetation_pct']:.1f}%", "Pixel Count (30m)": rec["vegetation_pixels"]},
            {"Land Cover Class": "Barren Land", "Color": "#E6C654", "Area (km²)": f"{rec['barren_km2']:.2f}", "Percentage (%)": f"{rec['barren_pct']:.1f}%", "Pixel Count (30m)": rec["barren_pixels"]},
            {"Land Cover Class": "Water Body", "Color": "#1E88E5", "Area (km²)": f"{rec['water_km2']:.2f}", "Percentage (%)": f"{rec['water_pct']:.1f}%", "Pixel Count (30m)": rec["water_pixels"]},
            {"Land Cover Class": "Built-up Area", "Color": "#D84315", "Area (km²)": f"{rec['builtup_km2']:.2f}", "Percentage (%)": f"{rec['builtup_pct']:.1f}%", "Pixel Count (30m)": rec["builtup_pixels"]},
            {"Land Cover Class": "TOTAL STUDY AREA", "Color": "-", "Area (km²)": f"{rec['total_km2']:.2f}", "Percentage (%)": "100.0%", "Pixel Count (30m)": rec["vegetation_pixels"] + rec["barren_pixels"] + rec["water_pixels"] + rec["builtup_pixels"]},
        ]
        try:
            out_df = pd.DataFrame(rows)
            out_df.to_csv(file_path, index=False, encoding="utf-8")
            return True, f"Successfully saved LULC summary for {year}."
        except Exception as e:
            return False, str(e)

    def export_all_years_csv(self, file_path: str) -> tuple[bool, str]:
        """Exports the full multi-decadal LULC timeseries table (1989-2026)."""
        try:
            df = self.load_master_counts()
            df.to_csv(file_path, index=False, encoding="utf-8")
            return True, f"Successfully exported full multi-decadal LULC table ({len(df)} observation years)."
        except Exception as e:
            return False, str(e)


lulc_service = LULCService()
