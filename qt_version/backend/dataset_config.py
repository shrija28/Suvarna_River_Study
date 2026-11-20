"""
Dataset Configuration & Discovery Engine - Estuarine Mouth Dynamics Project
Discovers, validates, and manages paths to actual project datasets in Google Drive:
Folder Structure:
SuvarnaProject_data/
├── average_rainfall/
│   ├── Suvarna_DeltaMouth_Rainfall_1989_2026.csv
│   ├── Suvarna_Delta_Monthly_Rainfall_1989_2026.csv
│   └── ...
├── weather_data/
│   ├── Suvarna_Daily_Weather_1989_1998.csv
│   ├── Suvarna_Daily_Weather_1999_2008.csv
│   ├── Suvarna_Daily_Weather_2009_2018.csv
│   ├── Suvarna_Daily_Weather_2019_2026_Aug.csv
│   ├── Suvarna_Delta_Temperature_Humidity_Corrected_1989_2026.csv
│   └── ...
├── river mouth images/
│   ├── image_RGB/      (RGB_1989.tif ... RGB_2026.tif)
│   ├── NDWI_images/    (NDWI_1989.tif ... NDWI_2026.tif)
│   └── Binary/         (Binary_2018.tif ... Binary_2026.tif + best_unet.keras)
├── LULC_Master_Counts.csv
└── Water_Body_Area_Bar_Plot_1989_2026.png
"""

import os
from PySide6.QtCore import QSettings

class DatasetConfig:
    def __init__(self):
        self._settings = QSettings("GeoTerra", "EstuarineMouthDynamics")
        self._root_dir = ""
        self.resolve_paths()

    def resolve_paths(self):
        """Resolves the active dataset root directory using priority discovery."""
        candidates = []

        # 1. User configured setting from QSettings
        saved_path = self._settings.value("dataset_root", "")
        if saved_path and os.path.isdir(str(saved_path)):
            candidates.append(str(saved_path))

        # 2. Environment variable
        env_path = os.environ.get("SUVARNA_DATA_DIR", "")
        if env_path and os.path.isdir(env_path):
            candidates.append(env_path)

        # 3. Workspace project folder
        ws_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "SuvarnaProject_data"))
        if os.path.isdir(ws_path):
            candidates.append(ws_path)

        # 4. Standard D:\ drive path
        d_path = r"D:\Suvarna_River_Study\SuvarnaProject_data"
        if os.path.isdir(d_path):
            candidates.append(d_path)

        # 5. Google Drive desktop typical mount points
        gdrive_candidates = [
            r"G:\My Drive\SuvarnaProject_data",
            r"G:\Other computers\My Laptop\SuvarnaProject_data",
            r"C:\Users\LENOVO\Google Drive\SuvarnaProject_data",
            r"C:\Users\LENOVO\GoogleDrive\SuvarnaProject_data"
        ]
        for gp in gdrive_candidates:
            if os.path.isdir(gp):
                candidates.append(gp)

        # 6. Fallback legacy data directory
        fallback_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        if os.path.isdir(fallback_data):
            candidates.append(fallback_data)

        # Select first existing directory with actual files
        for c in candidates:
            if os.path.isdir(c):
                self._root_dir = os.path.abspath(c)
                break

    @property
    def root_dir(self) -> str:
        return self._root_dir

    def set_root_dir(self, new_path: str) -> bool:
        """Sets and persists a custom dataset directory path."""
        if os.path.isdir(new_path):
            self._root_dir = os.path.abspath(new_path)
            self._settings.setValue("dataset_root", self._root_dir)
            return True
        return False

    @property
    def rainfall_dir(self) -> str:
        d = os.path.join(self._root_dir, "average_rainfall")
        if os.path.isdir(d):
            return d
        # Fallback to root or data folder if flat
        return self._root_dir

    @property
    def seasonal_rainfall_csv(self) -> str:
        candidates = [
            os.path.join(self.rainfall_dir, "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(self._root_dir, "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv")),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return ""

    @property
    def weather_dir(self) -> str:
        d = os.path.join(self._root_dir, "weather_data")
        if os.path.isdir(d):
            return d
        return self._root_dir

    @property
    def river_mouth_dir(self) -> str:
        d = os.path.join(self._root_dir, "river mouth images")
        if os.path.isdir(d):
            return d
        return self._root_dir

    @property
    def rgb_dir(self) -> str:
        d = os.path.join(self.river_mouth_dir, "image_RGB")
        if os.path.isdir(d):
            return d
        return self.river_mouth_dir

    @property
    def ndwi_dir(self) -> str:
        d = os.path.join(self.river_mouth_dir, "NDWI_images")
        if os.path.isdir(d):
            return d
        return self.river_mouth_dir

    @property
    def binary_dir(self) -> str:
        d = os.path.join(self.river_mouth_dir, "Binary")
        if os.path.isdir(d):
            return d
        return self.river_mouth_dir

    @property
    def first_opening_dir(self) -> str:
        d = os.path.join(self.river_mouth_dir, "First_Opening")
        if os.path.isdir(d):
            return d
        return self.river_mouth_dir

    @property
    def first_opening_csv(self) -> str:
        candidates = [
            os.path.join(self._root_dir, "Suvarna_First_Opening_Results.csv"),
            os.path.join(self.river_mouth_dir, "Suvarna_First_Opening_Results.csv"),
            os.path.join(self.river_mouth_dir, "Suvarna_First_Opening_Results_1990_onward.csv"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return ""

    @property
    def lulc_dir(self) -> str:
        d = os.path.join(self._root_dir, "LULC_images")
        if os.path.isdir(d):
            return d
        d2 = os.path.join(self.river_mouth_dir, "LULC_images")
        if os.path.isdir(d2):
            return d2
        return os.path.join(self._root_dir, "LULC_images")

    @property
    def lulc_master_csv(self) -> str:
        p = os.path.join(self._root_dir, "LULC_Master_Counts.csv")
        if os.path.isfile(p):
            return p
        return ""

    @property
    def lulc_master_pdf(self) -> str:
        p = os.path.join(self._root_dir, "LULC_Master_Counts.pdf")
        if os.path.isfile(p):
            return p
        return ""

    @property
    def water_body_plot_path(self) -> str:
        p = os.path.join(self._root_dir, "Water_Body_Area_Bar_Plot_1989_2026.png")
        if os.path.isfile(p):
            return p
        return ""

    @property
    def width_plot_path(self) -> str:
        p = os.path.join(self._root_dir, "Width_vs_Year.png")
        if os.path.isfile(p):
            return p
        return ""

    @property
    def opening_results_csv(self) -> str:
        p = os.path.join(self._root_dir, "Suvarna_First_Opening_Results.csv")
        if os.path.isfile(p):
            return p
        return ""

    @property
    def opening_results_xlsx(self) -> str:
        p = os.path.join(self._root_dir, "Suvarna_First_Opening_Results.xlsx")
        if os.path.isfile(p):
            return p
        return ""

    def get_status(self) -> dict:
        """Returns verification status and counts for all actual datasets."""
        status = {
            "root_found": bool(self._root_dir and os.path.isdir(self._root_dir)),
            "root_path": self._root_dir,
            "rainfall_found": False,
            "rainfall_files": 0,
            "weather_found": False,
            "weather_files": 0,
            "rgb_images_found": False,
            "rgb_count": 0,
            "ndwi_images_found": False,
            "ndwi_count": 0,
            "binary_masks_found": False,
            "binary_count": 0,
            "lulc_csv_found": False,
        }

        if not status["root_found"]:
            return status

        # Rainfall files
        if os.path.isdir(self.rainfall_dir):
            rf_files = [f for f in os.listdir(self.rainfall_dir) if f.endswith(('.csv', '.xlsx'))]
            status["rainfall_files"] = len(rf_files)
            status["rainfall_found"] = len(rf_files) > 0

        # Weather files
        if os.path.isdir(self.weather_dir):
            wf_files = [f for f in os.listdir(self.weather_dir) if f.endswith(('.csv', '.xlsx'))]
            status["weather_files"] = len(wf_files)
            status["weather_found"] = len(wf_files) > 0

        # RGB
        if os.path.isdir(self.rgb_dir):
            rgbs = [f for f in os.listdir(self.rgb_dir) if f.endswith('.tif')]
            status["rgb_count"] = len(rgbs)
            status["rgb_images_found"] = len(rgbs) > 0

        # NDWI
        if os.path.isdir(self.ndwi_dir):
            ndwis = [f for f in os.listdir(self.ndwi_dir) if f.endswith('.tif')]
            status["ndwi_count"] = len(ndwis)
            status["ndwi_images_found"] = len(ndwis) > 0

        # Binary
        if os.path.isdir(self.binary_dir):
            bins = [f for f in os.listdir(self.binary_dir) if f.endswith('.tif')]
            status["binary_count"] = len(bins)
            status["binary_masks_found"] = len(bins) > 0

        # LULC Master CSV
        status["lulc_csv_found"] = bool(self.lulc_master_csv and os.path.isfile(self.lulc_master_csv))

        return status


dataset_config = DatasetConfig()

