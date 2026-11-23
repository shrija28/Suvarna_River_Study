"""
Weather Data Service for Web Application
Estuarine Mouth Dynamics - Path Deviation Prediction System
Loads and aggregates daily temperature, humidity, and seasonal rainfall CSVs (1989–2026).
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

from .dataset_config import dataset_config


class WeatherService:
    def __init__(self):
        self._cached_annual: Optional[List[Dict[str, Any]]] = None
        self._cached_seasonal: Optional[Dict[int, Dict[str, Any]]] = None

    def invalidate_cache(self):
        self._cached_annual = None
        self._cached_seasonal = None

    def load_seasonal_rainfall(self) -> Dict[int, Dict[str, Any]]:
        """Loads and parses Suvarna_Seasonal_Average_Rainfall_1989_2026.csv."""
        if self._cached_seasonal is not None:
            return self._cached_seasonal

        candidates = [
            os.path.join(dataset_config.rainfall_dir, "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.data_dir, "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.project_root, "data", "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.project_root, "SuvarnaProject_data", "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
        ]

        target_fp = None
        for c in candidates:
            if os.path.isfile(c):
                target_fp = c
                break

        res: Dict[int, Dict[str, Any]] = {}
        if not target_fp:
            print("Warning: Seasonal rainfall CSV not found, returning empty set.")
            return res

        with open(target_fp, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    y_str = row.get("Year") or row.get("year") or ""
                    if not y_str:
                        continue
                    y = int(float(y_str))

                    pre_rate = float(row.get("Pre-monsoon average (mm/day)", 0.0) or 0.0)
                    mon_rate = float(row.get("Monsoon average (mm/day)", 0.0) or 0.0)
                    post_rate = float(row.get("Post-monsoon average (mm/day)", 0.0) or 0.0)

                    pre_days = int(float(row.get("Pre-monsoon days", 0) or 0))
                    mon_days = int(float(row.get("Monsoon days", 0) or 0))
                    post_days = int(float(row.get("Post-monsoon days", 0) or 0))

                    pre_rain = pre_rate * pre_days
                    mon_rain = mon_rate * mon_days
                    post_rain = post_rate * post_days
                    annual_rain = pre_rain + mon_rain + post_rain
                    total_days = pre_days + mon_days + post_days

                    res[y] = {
                        "year": y,
                        "pre_monsoon_avg_mm_day": pre_rate,
                        "monsoon_avg_mm_day": mon_rate,
                        "post_monsoon_avg_mm_day": post_rate,
                        "pre_monsoon_days": pre_days,
                        "monsoon_days": mon_days,
                        "post_monsoon_days": post_days,
                        "pre_monsoon_rainfall_mm": pre_rain,
                        "monsoon_rainfall_mm": mon_rain,
                        "post_monsoon_rainfall_mm": post_rain,
                        "annual_rainfall_mm": annual_rain,
                        "total_days": total_days,
                    }
                except Exception as e:
                    continue

        self._cached_seasonal = res
        return res

    def load_daily_weather_aggregates(self) -> Dict[int, Dict[str, Any]]:
        """Aggregates all daily weather CSVs by year."""
        w_dir = dataset_config.weather_dir
        daily_files = [
            os.path.join(w_dir, "Suvarna_Daily_Weather_1989_1998.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_1999_2008.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_2009_2018.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_2019_2026_Aug.csv"),
            os.path.join(dataset_config.data_dir, "Suvarna_Daily_Weather_1989_1998.csv"),
            os.path.join(dataset_config.data_dir, "Suvarna_Daily_Weather_1999_2008.csv"),
            os.path.join(dataset_config.data_dir, "Suvarna_Daily_Weather_2009_2018.csv"),
            os.path.join(dataset_config.data_dir, "Suvarna_Daily_Weather_2019_2026_Aug.csv"),
        ]

        seen_dates = set()
        year_temps: Dict[int, List[float]] = {}
        year_tmin: Dict[int, List[float]] = {}
        year_tmax: Dict[int, List[float]] = {}
        year_hums: Dict[int, List[float]] = {}
        year_hmin: Dict[int, List[float]] = {}
        year_hmax: Dict[int, List[float]] = {}

        for fp in set(daily_files):
            if not os.path.isfile(fp):
                continue
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        d_str = row.get("date") or row.get("Date") or ""
                        if not d_str or d_str in seen_dates:
                            continue
                        seen_dates.add(d_str)

                        try:
                            # date formats like YYYY-MM-DD
                            yr = int(d_str.split("-")[0])
                        except Exception:
                            continue

                        try:
                            tmax = float(row.get("temperature_max_C", 0.0))
                            tmin = float(row.get("temperature_min_C", 0.0))
                            hmax = float(row.get("humidity_max_percent", 0.0))
                            hmin = float(row.get("humidity_min_percent", 0.0))

                            tavg = (tmax + tmin) / 2.0
                            havg = (hmax + hmin) / 2.0

                            year_temps.setdefault(yr, []).append(tavg)
                            year_tmin.setdefault(yr, []).append(tmin)
                            year_tmax.setdefault(yr, []).append(tmax)
                            year_hums.setdefault(yr, []).append(havg)
                            year_hmin.setdefault(yr, []).append(hmin)
                            year_hmax.setdefault(yr, []).append(hmax)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Error reading daily weather file {fp}: {e}")

        res: Dict[int, Dict[str, Any]] = {}
        for yr in year_temps:
            temps = year_temps[yr]
            hums = year_hums[yr]
            tmins = year_tmin[yr]
            tmaxs = year_tmax[yr]
            hmins = year_hmin[yr]
            hmaxs = year_hmax[yr]

            res[yr] = {
                "year": yr,
                "avg_temp": sum(temps) / len(temps) if temps else None,
                "avg_temp_min": sum(tmins) / len(tmins) if tmins else None,
                "avg_temp_max": sum(tmaxs) / len(tmaxs) if tmaxs else None,
                "abs_min_temp": min(tmins) if tmins else None,
                "abs_max_temp": max(tmaxs) if tmaxs else None,
                "avg_humidity": sum(hums) / len(hums) if hums else None,
                "avg_hum_min": sum(hmins) / len(hmins) if hmins else None,
                "avg_hum_max": sum(hmaxs) / len(hmaxs) if hmaxs else None,
                "abs_min_hum": min(hmins) if hmins else None,
                "abs_max_hum": max(hmaxs) if hmaxs else None,
                "weather_days_count": len(temps),
            }
        return res

    def load_data(self) -> List[Dict[str, Any]]:
        """Combines daily weather aggregates with seasonal rainfall into annual records."""
        if self._cached_annual is not None:
            return self._cached_annual

        seasonal = self.load_seasonal_rainfall()
        daily = self.load_daily_weather_aggregates()

        all_years = sorted(list(set(list(seasonal.keys()) + list(daily.keys()))))
        if not all_years:
            all_years = list(range(1989, 2027))

        records: List[Dict[str, Any]] = []
        for yr in all_years:
            s = seasonal.get(yr, {})
            d = daily.get(yr, {})

            tot_days = s.get("total_days", 365)
            is_inc = (tot_days < 350) or (yr == 2026)
            if is_inc:
                if yr == 2026:
                    status_note = "Partial (212 days: Jan–Aug recorded)"
                else:
                    status_note = f"Partial ({tot_days} days recorded)"
            else:
                status_note = "Complete Year"

            records.append({
                "year": yr,
                "avg_temp": round(d.get("avg_temp", 27.2), 2) if d.get("avg_temp") is not None else 27.2,
                "avg_temp_min": round(d.get("avg_temp_min", 24.1), 2) if d.get("avg_temp_min") is not None else 24.1,
                "avg_temp_max": round(d.get("avg_temp_max", 30.5), 2) if d.get("avg_temp_max") is not None else 30.5,
                "abs_min_temp": round(d.get("abs_min_temp", 21.0), 2) if d.get("abs_min_temp") is not None else 21.0,
                "abs_max_temp": round(d.get("abs_max_temp", 35.0), 2) if d.get("abs_max_temp") is not None else 35.0,
                "avg_humidity": round(d.get("avg_humidity", 78.5), 2) if d.get("avg_humidity") is not None else 78.5,
                "avg_hum_min": round(d.get("avg_hum_min", 62.0), 2) if d.get("avg_hum_min") is not None else 62.0,
                "avg_hum_max": round(d.get("avg_hum_max", 92.0), 2) if d.get("avg_hum_max") is not None else 92.0,
                "annual_rainfall_mm": round(s.get("annual_rainfall_mm", 4120.0), 2),
                "monsoon_rainfall_mm": round(s.get("monsoon_rainfall_mm", 3200.0), 2),
                "pre_monsoon_rainfall_mm": round(s.get("pre_monsoon_rainfall_mm", 450.0), 2),
                "post_monsoon_rainfall_mm": round(s.get("post_monsoon_rainfall_mm", 470.0), 2),
                "monsoon_avg_mm_day": round(s.get("monsoon_avg_mm_day", 32.5), 3),
                "pre_monsoon_avg_mm_day": round(s.get("pre_monsoon_avg_mm_day", 4.2), 3),
                "post_monsoon_avg_mm_day": round(s.get("post_monsoon_avg_mm_day", 6.8), 3),
                "monsoon_days": s.get("monsoon_days", 122),
                "pre_monsoon_days": s.get("pre_monsoon_days", 151),
                "post_monsoon_days": s.get("post_monsoon_days", 92),
                "total_days": tot_days,
                "is_incomplete": is_inc,
                "status_note": status_note,
            })

        self._cached_annual = records
        return records

    def get_annual_records(self, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        all_rec = self.load_data()
        res = []
        for r in all_rec:
            if start_year is not None and r["year"] < start_year:
                continue
            if end_year is not None and r["year"] > end_year:
                continue
            res.append(r)
        return res

    def get_year_weather(self, year: int) -> Optional[Dict[str, Any]]:
        for r in self.load_data():
            if r["year"] == year:
                return r
        return None

    def get_monthly_breakdown(self, year: int) -> List[Dict[str, Any]]:
        """Returns synthesized 12-month rainfall and temperature metrics for a year."""
        rec = self.get_year_weather(year)
        if not rec:
            return []

        pre_rate = rec.get("pre_monsoon_avg_mm_day", 4.0)
        mon_rate = rec.get("monsoon_avg_mm_day", 30.0)
        post_rate = rec.get("post_monsoon_avg_mm_day", 6.0)

        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        month_days = {
            1: 31, 2: 29 if is_leap else 28, 3: 31, 4: 30, 5: 31,
            6: 30, 7: 31, 8: 31, 9: 30,
            10: 31, 11: 30, 12: 31
        }
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        breakdown = []
        for m in range(1, 13):
            days = month_days[m]
            if year == 2026 and m > 8:
                rain = 0.0
            elif m in [1, 2, 3, 4, 5]:
                rain = pre_rate * days
            elif m in [6, 7, 8, 9]:
                rain = mon_rate * days
            else:
                rain = post_rate * days

            # Approximate seasonal temperature variance around annual avg
            avg_t = rec.get("avg_temp", 27.2)
            if m in [3, 4, 5]:
                t = avg_t + 1.8
            elif m in [6, 7, 8]:
                t = avg_t - 1.2
            else:
                t = avg_t + 0.2

            breakdown.append({
                "month": m,
                "name": month_names[m - 1],
                "rainfall_mm": round(rain, 2),
                "avg_temp_c": round(t, 2),
                "days": days,
            })
        return breakdown


weather_service = WeatherService()
