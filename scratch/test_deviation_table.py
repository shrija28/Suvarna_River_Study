import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, "qt_version")

from PySide6.QtWidgets import QApplication
from pages.deviation_page import RiverMouthDeviationPage
from backend.deviation_service import deviation_service

app = QApplication.instance() or QApplication(sys.argv)

page = RiverMouthDeviationPage()
page.resize(1300, 850)
page.show()

table = page.table
print(f"Table columns count: {table.columnCount()}")
headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
print(f"Table headers: {headers}")

print(f"Table rows count: {table.rowCount()}")

expected_headers = [
    "Index", "Year", "Mouth Width (m)", "Longitude", "Latitude",
    "East Shift (m)", "North Shift (m)"
]
assert headers == expected_headers, f"Headers mismatch: {headers} != {expected_headers}"
assert table.rowCount() == 38, f"Rows count is {table.rowCount()}, expected 38"

# Print first 5 rows
print("\n--- First 5 rows ---")
for r in range(5):
    vals = [table.item(r, c).text() for c in range(table.columnCount())]
    print(f"Row {r}: {vals}")

# Print row 6 (1995 NaN)
print("\n--- Row 6 (1995) ---")
vals_1995 = [table.item(6, c).text() for c in range(table.columnCount())]
print(f"Row 6 (1995): {vals_1995}")
assert vals_1995[1] == "1995", f"Expected year 1995, got {vals_1995[1]}"
assert vals_1995[2] == "NaN", f"Expected NaN for Mouth Width, got {vals_1995[2]}"

# Print last 5 rows
print("\n--- Last 5 rows ---")
for r in range(33, 38):
    vals = [table.item(r, c).text() for c in range(table.columnCount())]
    print(f"Row {r}: {vals}")

# Verify 2026
vals_2026 = [table.item(37, c).text() for c in range(table.columnCount())]
assert vals_2026[1] == "2026"
assert vals_2026[2] == "210.0"

# Test filter functionality
print("\n--- Testing Filter ---")
page.filter_input.setText("1995")
app.processEvents()
visible_count = sum(not table.isRowHidden(r) for r in range(table.rowCount()))
print(f"Visible rows with filter '1995': {visible_count}")
assert visible_count == 1, f"Expected 1 visible row, got {visible_count}"

# Clear filter
page.filter_input.setText("")
app.processEvents()
visible_count = sum(not table.isRowHidden(r) for r in range(table.rowCount()))
print(f"Visible rows after clearing filter: {visible_count}")
assert visible_count == 38

# Grab screenshot
pix = page.grab()
os.makedirs("scratch", exist_ok=True)
pix.save("scratch/test_deviation_table_screenshot.png")
print("\nScreenshot successfully saved to scratch/test_deviation_table_screenshot.png")
print("\nALL VERIFICATION CHECKS PASSED!")
