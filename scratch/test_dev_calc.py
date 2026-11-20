import sys
import os
sys.path.insert(0, r"d:\Suvarna_River_Study\qt_version")
sys.path.insert(0, r"d:\Suvarna_River_Study")

from backend.deviation_service import deviation_service

print("Available years in deviation_service:", deviation_service.get_available_years())

years_to_test = [
    (1989, 2000),
    (1989, 2026),
    (1990, 2024),
    (2015, 2024),
    (1989, 1989),
    (2000, 2000),
    (1995, 2005),
]

for b, t in years_to_test:
    try:
        res = deviation_service.calculate_deviation(b, t)
        print(f"calculate_deviation({b}, {t}) -> {'SUCCESS' if res else 'None'}")
    except Exception as e:
        print(f"calculate_deviation({b}, {t}) -> EXCEPTION: {e}")
