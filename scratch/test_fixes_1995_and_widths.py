import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, "qt_version")

from PySide6.QtWidgets import QApplication, QStackedWidget
from backend.data_service import data_service, DEFAULT_BENCHMARK_YEARS
from backend.deviation_service import deviation_service
from pages.river_mouth_page import RiverMouthImagesPage
from pages.deviation_page import RiverMouthDeviationPage

app = QApplication.instance() or QApplication(sys.argv)

print("--- 1. Testing Breach Widths (matching inside image text) ---")
widths_expected = {
    1989: 175.0,
    1990: 189.81,
    1994: 150.06,
    1995: None,
    2000: 127.33,
    2015: 1271.87,
    2020: 127.33,
    2024: 169.77,
    2026: 134.22,
}

for yr, exp in widths_expected.items():
    pix, meta = data_service.get_raster_image_for_year(yr, view_mode="first_opening")
    w = meta.get("width_m")
    if exp is None:
        print(f"Year {yr}: Breach width is {w} (Expected: None / No Data)")
        assert w is None, f"Expected None for {yr}, got {w}"
    else:
        print(f"Year {yr}: Breach width = {w:.2f} m (Expected: {exp:.2f} m)")
        assert abs(w - exp) < 0.1, f"Mismatch for {yr}: {w} != {exp}"

print("\n--- 2. Testing Benchmark Years (1994 replaced 1995) ---")
print("DEFAULT_BENCHMARK_YEARS:", DEFAULT_BENCHMARK_YEARS)
assert 1994 in DEFAULT_BENCHMARK_YEARS, "1994 should be in benchmark years"
assert 1995 not in DEFAULT_BENCHMARK_YEARS, "1995 should not be in default benchmark years"

print("\n--- 3. Testing Deviation Time-series (1995 is zero, no spike) ---")
dev = deviation_service.calculate_deviation(1989, 2026)
for row in dev["timeseries"]:
    if row["year"] in [1993, 1994, 1995, 1996]:
        print(f"Year {row['year']}: disp={row['displacement_m']:.2f} m, dx={row['dx_m']:.2f} m, dy={row['dy_m']:.2f} m, has_data={row.get('has_data')}")
        if row["year"] == 1995:
            assert row["displacement_m"] == 0.0, f"1995 displacement should be 0.0, got {row['displacement_m']}"
            assert row["has_data"] is False, "1995 has_data should be False"
        if row["year"] == 1994:
            assert row["displacement_m"] > 0, "1994 displacement should be > 0"

print("\n--- 4. Render Gallery Page ---")
stack = QStackedWidget()
gallery_page = RiverMouthImagesPage(stack=stack)
stack.addWidget(gallery_page)
stack.resize(1300, 850)
stack.show()
gallery_page.set_view_mode("first_opening")
app.processEvents()

# Verify card labels
for card in gallery_page.cards:
    lbl = card.meta_lbl.text()
    print(f"Gallery Card {card.year}: {lbl}")
    if card.year == 1989:
        assert "175.0 m" in lbl, f"1989 card label expected 175.0 m, got {lbl}"
    if card.year == 1990:
        assert "189.8 m" in lbl, f"1990 card label expected 189.8 m, got {lbl}"
    if card.year == 1994:
        assert "150.1 m" in lbl, f"1994 card label expected 150.1 m, got {lbl}"

pix_gal = gallery_page.grab()
os.makedirs("scratch", exist_ok=True)
pix_gal.save("scratch/test_gallery_verified.png")
print("Gallery screenshot saved.")

print("\n--- 5. Render Deviation Page ---")
dev_page = RiverMouthDeviationPage()
dev_page.resize(1300, 850)
dev_page.show()
app.processEvents()

pix_dev = dev_page.grab()
pix_dev.save("scratch/test_deviation_verified.png")
print("Deviation page screenshot saved.")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
