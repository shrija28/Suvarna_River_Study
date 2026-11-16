import sys, os
sys.path.insert(0, os.path.abspath("qt_version"))
from backend.deviation_service import deviation_service

res = deviation_service.calculate_deviation(1989, 2026)
print("displacement_m:", res.get("displacement_m"))
print("dx_m:", res.get("dx_m"))
print("dy_m:", res.get("dy_m"))
print("d_lat:", res.get("d_lat"))
print("d_lon:", res.get("d_lon"))
print("direction:", res.get("direction_name"), res.get("azimuth_deg"))
print("base mouth:", res["base_data"]["mouth_lat"], res["base_data"]["mouth_lon"])
print("target mouth:", res["target_data"]["mouth_lat"], res["target_data"]["mouth_lon"])

