import sys
import os

sys.path.insert(0, os.path.abspath(r"d:\Suvarna_River_Study\qt_version"))

from PySide6.QtWidgets import QApplication
from app import MainWindow
from backend.lulc_service import lulc_service

def test():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Authenticate into main application
    window.on_login_success({"username": "admin", "role": "Administrator"})

    home = window.home_page
    result = window.result_page

    # -------------------------------------------------------------
    # Scenario 1: Base Year 1989, Prediction Year 2000
    # -------------------------------------------------------------
    print("=== Testing Scenario 1: Base Year 1989, Prediction Year 2000 ===")
    home.set_selected_years([1989, 2000])

    window.go_to_lulc()

    print("Result Base Year:", result.base_year)
    print("Result Target Year:", result.target_year)
    assert result.base_year == 1989, f"Expected 1989, got {result.base_year}"
    assert result.target_year == 2000, f"Expected 2000, got {result.target_year}"

    # Verify Year Dropdown is strictly 1989..2000
    combo_items = [result.year_combo.itemText(i) for i in range(result.year_combo.count())]
    print("Year Dropdown Items:", combo_items)
    expected_combo = [str(y) for y in range(1989, 2001)]
    assert combo_items == expected_combo, f"Expected {expected_combo}, got {combo_items}"

    # Verify Table Rows
    table = result.files_card.table
    print("Table Row Count:", table.rowCount())
    table_years = [int(table.item(r, 0).text()) for r in range(table.rowCount())]
    print("Table Years:", table_years)
    assert all(1989 <= y <= 2000 for y in table_years), "Found years outside 1989-2000 in table!"
    assert 1989 in table_years and 2000 in table_years
    assert 2001 not in table_years and 2026 not in table_years
    assert 1988 not in table_years
    print("Download button text:", result.files_card.btn_export_csv.text())
    assert "11-Yr" in result.files_card.btn_export_csv.text()

    # Verify Comparison Chart
    chart = result.chart_widget
    chart_years = [r["year"] for r in chart.all_records]
    print("Chart Years:", chart_years)
    assert all(1989 <= y <= 2000 for y in chart_years), "Found years outside 1989-2000 in chart!"
    assert len(chart.all_records) == 11
    assert "11-Year Timeseries" in chart.btn_mode_ts.text()

    # Verify Summary Cards & Map for valid year (1989)
    result.load_year(1989)
    print("1989 Veg text:", result.card_veg.area_lbl.text(), result.card_veg.pct_badge.text())
    assert result.card_veg.area_lbl.text() == "619.13 km²"
    assert result.card_veg.pct_badge.text() == "41.2 %"
    assert result.card_water.area_lbl.text() == "744.08 km²"
    assert result.card_water.pct_badge.text() == "49.5 %"
    assert result.map_card.image_container.pixmap() is not None

    # Verify missing year handling (1995 has no data)
    result.load_year(1995)
    print("1995 Missing Year Display - Veg:", result.card_veg.area_lbl.text(), result.card_veg.pct_badge.text())
    print("1995 Missing Year Display - Map text:", result.map_card.image_container.text())
    assert result.card_veg.area_lbl.text() == "--"
    assert result.card_veg.pct_badge.text() == "N/A"
    assert "LULC data unavailable for this year" in result.map_card.image_container.text()

    # Test filtered CSV export
    test_csv_path = os.path.abspath(r"scratch\test_export_1989_2000.csv")
    ok, msg = lulc_service.export_filtered_years_csv(1989, 2000, test_csv_path)
    assert ok, f"Export failed: {msg}"
    import pandas as pd
    exp_df = pd.read_csv(test_csv_path)
    print("Exported CSV rows:", len(exp_df), "Years:", exp_df["year"].tolist())
    assert len(exp_df) == 11
    assert all(1989 <= y <= 2000 for y in exp_df["year"])

    # -------------------------------------------------------------
    # Scenario 2: Base Year 2015, Prediction Year 2026
    # -------------------------------------------------------------
    print("\n=== Testing Scenario 2: Base Year 2015, Prediction Year 2026 ===")
    home.set_selected_years([2015, 2026])

    window.go_to_lulc()

    print("Result Base Year:", result.base_year)
    print("Result Target Year:", result.target_year)
    assert result.base_year == 2015
    assert result.target_year == 2026

    # Verify Year Dropdown is strictly 2015..2026
    combo_items_2 = [result.year_combo.itemText(i) for i in range(result.year_combo.count())]
    print("Year Dropdown Items (2015-2026):", combo_items_2)
    expected_combo_2 = [str(y) for y in range(2015, 2027)]
    assert combo_items_2 == expected_combo_2

    # Verify Table Rows
    table_years_2 = [int(table.item(r, 0).text()) for r in range(table.rowCount())]
    print("Table Years (2015-2026):", table_years_2)
    assert all(2015 <= y <= 2026 for y in table_years_2)
    assert len(table_years_2) == 12
    assert 1989 not in table_years_2 and 2000 not in table_years_2

    # Verify Comparison Chart
    chart_years_2 = [r["year"] for r in chart.all_records]
    print("Chart Years (2015-2026):", chart_years_2)
    assert all(2015 <= y <= 2026 for y in chart_years_2)
    assert len(chart.all_records) == 12
    assert "12-Year Timeseries" in chart.btn_mode_ts.text()

    # Reset to 1989 -> 2000
    home.set_selected_years([1989, 2000])

    print("\nALL LULC FILTERING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test()
