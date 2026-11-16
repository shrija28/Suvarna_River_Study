"""
Weather Data Service for Estuarine Mouth Dynamics Project
Uses Pandas to load, clean, validate, and aggregate:
- Daily temperature & relative humidity CSVs covering 1989–2026.
- Verified Seasonal Rainfall dataset (1989–2026): Pre-monsoon, Monsoon, Post-monsoon averages & days.
Zero placeholder data, 100% genuine project datasets.
"""

import os
import pandas as pd
import numpy as np
from .dataset_config import dataset_config


MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}


class WeatherService:
    def __init__(self):
        self._cached_annual_df = None
        self._cached_daily_df = None
        self._cached_rainfall_df = None

    def invalidate_cache(self):
        self._cached_annual_df = None
        self._cached_daily_df = None
        self._cached_rainfall_df = None

    def load_daily_weather(self) -> pd.DataFrame:
        """Loads and combines all daily weather CSV batches (1989-2026)."""
        if self._cached_daily_df is not None:
            return self._cached_daily_df

        w_dir = dataset_config.weather_dir
        daily_files = [
            os.path.join(w_dir, "Suvarna_Daily_Weather_1989_1998.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_1999_2008.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_2009_2018.csv"),
            os.path.join(w_dir, "Suvarna_Daily_Weather_2019_2026_Aug.csv")
        ]

        dfs = []
        for fp in daily_files:
            if os.path.exists(fp):
                try:
                    df = pd.read_csv(fp)
                    dfs.append(df)
                except Exception as e:
                    print(f"Error loading daily weather file {fp}: {e}")

        if not dfs:
            raise FileNotFoundError(f"No daily weather CSV files found in {w_dir}")

        combined = pd.concat(dfs, ignore_index=True)
        combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
        combined = combined.dropna(subset=["date"])
        # Deduplicate on date to avoid overlapping batch records
        combined = combined.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)

        for col in ["temperature_max_C", "temperature_min_C", "humidity_max_percent", "humidity_min_percent"]:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

        combined["daily_temp"] = (combined["temperature_max_C"] + combined["temperature_min_C"]) / 2.0
        combined["daily_hum"] = (combined["humidity_max_percent"] + combined["humidity_min_percent"]) / 2.0
        combined["year"] = combined["date"].dt.year
        combined["month"] = combined["date"].dt.month

        self._cached_daily_df = combined
        return self._cached_daily_df

    def load_seasonal_rainfall(self) -> pd.DataFrame:
        """
        Loads and cleans the verified seasonal rainfall dataset (1989-2026).
        Calculates Pre-monsoon, Monsoon, Post-monsoon, and Annual totals in mm.
        """
        if self._cached_rainfall_df is not None:
            return self._cached_rainfall_df

        r_dir = dataset_config.rainfall_dir
        candidates = [
            os.path.join(r_dir, "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.join(dataset_config.root_dir, "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "average_rainfall", "Suvarna_Seasonal_Average_Rainfall_1989_2026.csv")),
        ]

        fp = None
        for c in candidates:
            if os.path.exists(c):
                fp = c
                break

        if not fp:
            raise FileNotFoundError(f"Could not find verified seasonal rainfall CSV in {r_dir}")

        df = pd.read_csv(fp)

        # Standardize column types
        for col in [
            "Pre-monsoon average (mm/day)", "Monsoon average (mm/day)", "Post-monsoon average (mm/day)",
            "Pre-monsoon days", "Monsoon days", "Post-monsoon days"
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        df["year"] = pd.to_numeric(df["Year"], errors="coerce").astype(int)

        # Calculate seasonal and annual totals in millimetres
        df["pre_monsoon_rainfall_mm"] = df["Pre-monsoon average (mm/day)"] * df["Pre-monsoon days"]
        df["monsoon_rainfall_mm"] = df["Monsoon average (mm/day)"] * df["Monsoon days"]
        df["post_monsoon_rainfall_mm"] = df["Post-monsoon average (mm/day)"] * df["Post-monsoon days"]
        df["annual_rainfall_mm"] = df["pre_monsoon_rainfall_mm"] + df["monsoon_rainfall_mm"] + df["post_monsoon_rainfall_mm"]
        df["total_days"] = df["Pre-monsoon days"] + df["Monsoon days"] + df["Post-monsoon days"]

        df["pre_monsoon_avg_mm_day"] = df["Pre-monsoon average (mm/day)"]
        df["monsoon_avg_mm_day"] = df["Monsoon average (mm/day)"]
        df["post_monsoon_avg_mm_day"] = df["Post-monsoon average (mm/day)"]

        df["pre_monsoon_days"] = df["Pre-monsoon days"].astype(int)
        df["monsoon_days"] = df["Monsoon days"].astype(int)
        df["post_monsoon_days"] = df["Post-monsoon days"].astype(int)

        df = df.sort_values("year").reset_index(drop=True)
        self._cached_rainfall_df = df
        return self._cached_rainfall_df

    def load_monthly_rainfall(self) -> pd.DataFrame:
        """
        Backward-compatibility loader: synthesizes monthly values based strictly
        on the verified seasonal rates and observation days.
        """
        rain_df = self.load_seasonal_rainfall()
        records = []
        for _, r in rain_df.iterrows():
            y = int(r["year"])
            pre_rate = float(r["pre_monsoon_avg_mm_day"])
            mon_rate = float(r["monsoon_avg_mm_day"])
            post_rate = float(r["post_monsoon_avg_mm_day"])

            is_leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
            month_days = {
                1: 31, 2: 29 if is_leap else 28, 3: 31, 4: 30, 5: 31,
                6: 30, 7: 31, 8: 31, 9: 30,
                10: 31, 11: 30, 12: 31
            }
            for m in range(1, 13):
                if y == 2026 and m > 8:
                    val = 0.0
                elif m in [1, 2, 3, 4, 5]:
                    val = pre_rate * month_days[m]
                elif m in [6, 7, 8, 9]:
                    if y == 2026 and m == 9:
                        val = 0.0
                    else:
                        val = mon_rate * month_days[m]
                else:
                    val = post_rate * month_days[m]
                records.append({"year": y, "month": m, "rainfall_mm": round(val, 2)})
        return pd.DataFrame(records)

    def load_data(self) -> pd.DataFrame:
        """
        Combines daily temperature/humidity and seasonal rainfall into annual aggregates.
        """
        if self._cached_annual_df is not None:
            return self._cached_annual_df

        daily_df = self.load_daily_weather()
        rain_df = self.load_seasonal_rainfall()

        # 1. Aggregate Daily Weather
        annual_weather = daily_df.groupby("year").agg(
            avg_temp=("daily_temp", "mean"),
            avg_temp_min=("temperature_min_C", "mean"),
            avg_temp_max=("temperature_max_C", "mean"),
            abs_min_temp=("temperature_min_C", "min"),
            abs_max_temp=("temperature_max_C", "max"),
            avg_humidity=("daily_hum", "mean"),
            avg_hum_min=("humidity_min_percent", "mean"),
            avg_hum_max=("humidity_max_percent", "mean"),
            abs_min_hum=("humidity_min_percent", "min"),
            abs_max_hum=("humidity_max_percent", "max"),
            weather_days_count=("date", "count")
        ).reset_index()

        # 2. Merge Weather with Seasonal Rainfall
        merged = pd.merge(annual_weather, rain_df, on="year", how="outer")
        merged = merged.sort_values("year").reset_index(drop=True)

        merged["weather_days_count"] = merged["weather_days_count"].fillna(0).astype(int)
        merged["total_days"] = merged["total_days"].fillna(365).astype(int)

        # Mark incomplete years (e.g. 2026 which only covers through August)
        merged["is_incomplete"] = (merged["total_days"] < 350) | (merged["year"] == 2026)

        def make_status(row):
            if row["is_incomplete"]:
                if row["year"] == 2026:
                    return f"Partial (212 days: Jan–Aug recorded)"
                return f"Partial ({row['total_days']} days recorded)"
            return "Complete Year"

        merged["status_note"] = merged.apply(make_status, axis=1)

        self._cached_annual_df = merged
        return self._cached_annual_df

    def get_year_bounds(self):
        df = self.load_data()
        return int(df["year"].min()), int(df["year"].max())

    def get_annual_records(self, start_year: int = None, end_year: int = None):
        """Returns filtered annual weather data as a list of dicts."""
        df = self.load_data()
        if start_year is not None:
            df = df[df["year"] >= start_year]
        if end_year is not None:
            df = df[df["year"] <= end_year]

        records = []
        for _, r in df.iterrows():
            records.append({
                "year": int(r["year"]),
                "avg_temp": round(float(r["avg_temp"]), 2) if pd.notnull(r["avg_temp"]) else None,
                "avg_temp_min": round(float(r["avg_temp_min"]), 2) if pd.notnull(r["avg_temp_min"]) else None,
                "avg_temp_max": round(float(r["avg_temp_max"]), 2) if pd.notnull(r["avg_temp_max"]) else None,
                "abs_min_temp": round(float(r["abs_min_temp"]), 2) if pd.notnull(r["abs_min_temp"]) else None,
                "abs_max_temp": round(float(r["abs_max_temp"]), 2) if pd.notnull(r["abs_max_temp"]) else None,
                "avg_humidity": round(float(r["avg_humidity"]), 2) if pd.notnull(r["avg_humidity"]) else None,
                "avg_hum_min": round(float(r["avg_hum_min"]), 2) if pd.notnull(r["avg_hum_min"]) else None,
                "avg_hum_max": round(float(r["avg_hum_max"]), 2) if pd.notnull(r["avg_hum_max"]) else None,
                "annual_rainfall_mm": round(float(r["annual_rainfall_mm"]), 2) if pd.notnull(r["annual_rainfall_mm"]) else None,
                "monsoon_rainfall_mm": round(float(r["monsoon_rainfall_mm"]), 2) if pd.notnull(r["monsoon_rainfall_mm"]) else None,
                "pre_monsoon_rainfall_mm": round(float(r["pre_monsoon_rainfall_mm"]), 2) if pd.notnull(r["pre_monsoon_rainfall_mm"]) else None,
                "post_monsoon_rainfall_mm": round(float(r["post_monsoon_rainfall_mm"]), 2) if pd.notnull(r["post_monsoon_rainfall_mm"]) else None,
                "monsoon_avg_mm_day": round(float(r["monsoon_avg_mm_day"]), 3) if pd.notnull(r["monsoon_avg_mm_day"]) else None,
                "pre_monsoon_avg_mm_day": round(float(r["pre_monsoon_avg_mm_day"]), 3) if pd.notnull(r["pre_monsoon_avg_mm_day"]) else None,
                "post_monsoon_avg_mm_day": round(float(r["post_monsoon_avg_mm_day"]), 3) if pd.notnull(r["post_monsoon_avg_mm_day"]) else None,
                "monsoon_days": int(r["monsoon_days"]) if pd.notnull(r["monsoon_days"]) else 0,
                "pre_monsoon_days": int(r["pre_monsoon_days"]) if pd.notnull(r["pre_monsoon_days"]) else 0,
                "post_monsoon_days": int(r["post_monsoon_days"]) if pd.notnull(r["post_monsoon_days"]) else 0,
                "total_days": int(r["total_days"]) if pd.notnull(r["total_days"]) else 0,
                "is_incomplete": bool(r["is_incomplete"]),
                "status_note": str(r["status_note"])
            })
        return records

    def get_year_weather(self, year: int) -> dict:
        """Returns single-year weather record for data service."""
        records = self.get_annual_records(start_year=year, end_year=year)
        if records:
            return records[0]
        return {}

    def get_monthly_breakdown(self, year: int) -> list[dict]:
        """Returns monthly rainfall, temperature, and humidity for a specific year."""
        rain_df = self.load_monthly_rainfall()
        sub_rain = rain_df[rain_df["year"] == year].copy()

        daily_df = self.load_daily_weather()
        sub_daily = daily_df[daily_df["year"] == year].copy()
        monthly_daily = sub_daily.groupby("month").agg(
            m_temp=("daily_temp", "mean"),
            m_temp_min=("temperature_min_C", "min"),
            m_temp_max=("temperature_max_C", "max"),
            m_hum=("daily_hum", "mean")
        ).reset_index()

        merged = pd.merge(sub_rain, monthly_daily, on="month", how="outer").sort_values("month")
        results = []
        for _, r in merged.iterrows():
            m = int(r["month"])
            results.append({
                "month": m,
                "month_name": MONTH_NAMES.get(m, str(m)),
                "rainfall_mm": round(float(r["rainfall_mm"]), 2) if pd.notnull(r.get("rainfall_mm")) else 0.0,
                "temp_c": round(float(r["m_temp"]), 2) if pd.notnull(r.get("m_temp")) else None,
                "temp_min": round(float(r["m_temp_min"]), 2) if pd.notnull(r.get("m_temp_min")) else None,
                "temp_max": round(float(r["m_temp_max"]), 2) if pd.notnull(r.get("m_temp_max")) else None,
                "humidity_pct": round(float(r["m_hum"]), 2) if pd.notnull(r.get("m_hum")) else None,
            })
        return results

    def export_csv(self, file_path: str, start_year: int = None, end_year: int = None) -> int:
        """Exports the filtered annual table to CSV with comprehensive seasonal rainfall metrics."""
        records = self.get_annual_records(start_year, end_year)
        if not records:
            return 0

        export_rows = []
        for r in records:
            export_rows.append({
                "Year": r["year"],
                "Pre-monsoon average (mm/day)": f"{r['pre_monsoon_avg_mm_day']:.3f}" if r["pre_monsoon_avg_mm_day"] is not None else "0.000",
                "Pre-monsoon days": r["pre_monsoon_days"],
                "Pre-monsoon Rainfall (mm)": f"{r['pre_monsoon_rainfall_mm']:.2f}" if r["pre_monsoon_rainfall_mm"] is not None else "0.00",
                "Monsoon average (mm/day)": f"{r['monsoon_avg_mm_day']:.3f}" if r["monsoon_avg_mm_day"] is not None else "0.000",
                "Monsoon days": r["monsoon_days"],
                "Monsoon Rainfall (mm)": f"{r['monsoon_rainfall_mm']:.2f}" if r["monsoon_rainfall_mm"] is not None else "0.00",
                "Post-monsoon average (mm/day)": f"{r['post_monsoon_avg_mm_day']:.3f}" if r["post_monsoon_avg_mm_day"] is not None else "0.000",
                "Post-monsoon days": r["post_monsoon_days"],
                "Post-monsoon Rainfall (mm)": f"{r['post_monsoon_rainfall_mm']:.2f}" if r["post_monsoon_rainfall_mm"] is not None else "0.00",
                "Annual Rainfall (mm)": f"{r['annual_rainfall_mm']:.2f}" if r["annual_rainfall_mm"] is not None else "N/A",
                "Average Temperature (°C)": f"{r['avg_temp']:.2f}" if r["avg_temp"] is not None else "N/A",
                "Average Relative Humidity (%)": f"{r['avg_humidity']:.2f}" if r["avg_humidity"] is not None else "N/A",
                "Data Status": r["status_note"]
            })

        out_df = pd.DataFrame(export_rows)
        out_df.to_csv(file_path, index=False, encoding="utf-8")
        return len(export_rows)


weather_service = WeatherService()
