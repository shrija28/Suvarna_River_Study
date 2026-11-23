"""
Dataset Configuration & Discovery Engine for Web Application
Estuarine Mouth Dynamics - Path Deviation Prediction System
Discovers and manages paths to project datasets in data/, SuvarnaProject_data/, and assets/.
"""

import os

class DatasetConfig:
    def __init__(self):
        self._web_app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self._project_root = os.path.abspath(os.path.join(self._web_app_dir, ".."))
        self._root_dir = ""
        self._data_dir = ""
        self._assets_dir = ""
        self.resolve_paths()

    def resolve_paths(self):
        """Resolves the active dataset root and data directories."""
        # 1. Project assets directory
        assets_candidates = [
            os.path.join(self._project_root, "assets"),
            os.path.join(self._web_app_dir, "static", "assets"),
        ]
        for a in assets_candidates:
            if os.path.isdir(a):
                self._assets_dir = a
                break

        # 2. Main SuvarnaProject_data directory
        sp_candidates = [
            os.environ.get("SUVARNA_DATA_DIR", ""),
            os.path.join(self._project_root, "SuvarnaProject_data"),
            os.path.join(self._project_root, "data"),
            r"D:\Suvarna_River_Study\SuvarnaProject_data",
        ]
        for c in sp_candidates:
            if c and os.path.isdir(c):
                self._root_dir = os.path.abspath(c)
                break
        if not self._root_dir:
            self._root_dir = os.path.join(self._project_root, "data")

        # 3. Local data/ directory (for auth.db, weather, width and shift csv, etc.)
        data_candidates = [
            os.path.join(self._project_root, "data"),
            os.path.join(self._project_root, "SuvarnaProject_data"),
        ]
        for d in data_candidates:
            if os.path.isdir(d):
                self._data_dir = os.path.abspath(d)
                break
        if not self._data_dir:
            self._data_dir = self._root_dir

    @property
    def project_root(self) -> str:
        return self._project_root

    @property
    def root_dir(self) -> str:
        return self._root_dir

    @property
    def data_dir(self) -> str:
        return self._data_dir

    @property
    def assets_dir(self) -> str:
        return self._assets_dir

    @property
    def rainfall_dir(self) -> str:
        d = os.path.join(self._data_dir, "average_rainfall")
        if os.path.isdir(d):
            return d
        d2 = os.path.join(self._root_dir, "average_rainfall")
        if os.path.isdir(d2):
            return d2
        return self._data_dir

    @property
    def weather_dir(self) -> str:
        d = os.path.join(self._root_dir, "weather_data")
        if os.path.isdir(d):
            return d
        return self._data_dir

    @property
    def river_mouth_dir(self) -> str:
        d = os.path.join(self._data_dir, "river mouth images")
        if os.path.isdir(d):
            return d
        d2 = os.path.join(self._root_dir, "river mouth images")
        if os.path.isdir(d2):
            return d2
        return self._data_dir

    @property
    def first_opening_dir(self) -> str:
        d = os.path.join(self.river_mouth_dir, "First_Opening")
        if os.path.isdir(d):
            return d
        return self.river_mouth_dir

    @property
    def lulc_dir(self) -> str:
        d = os.path.join(self._root_dir, "LULC_images")
        if os.path.isdir(d):
            return d
        return self._root_dir

    @property
    def lulc_master_csv(self) -> str:
        candidates = [
            os.path.join(self._root_dir, "LULC_Master_Counts.csv"),
            os.path.join(self._data_dir, "LULC_Master_Counts.csv"),
            os.path.join(self._project_root, "SuvarnaProject_data", "LULC_Master_Counts.csv"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return ""

    @property
    def mouth_width_shift_csv(self) -> str:
        candidates = [
            os.path.join(self._data_dir, "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
            os.path.join(self._root_dir, "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
            os.path.join(self._project_root, "SuvarnaProject_data", "Suvarna_River_Mouth_Width_and_Shift_1989_2026.csv"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return ""


dataset_config = DatasetConfig()
