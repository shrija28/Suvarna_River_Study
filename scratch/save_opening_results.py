import os
import csv
import shutil
import zipfile
import xml.etree.ElementTree as ET

src_xlsx = "scratch/Suvarna_First_Opening_Results.xlsx"
dest_xlsx = "SuvarnaProject_data/Suvarna_First_Opening_Results.xlsx"
dest_csv = "SuvarnaProject_data/Suvarna_First_Opening_Results.csv"

# Copy XLSX
shutil.copyfile(src_xlsx, dest_xlsx)
print(f"Copied {src_xlsx} -> {dest_xlsx} ({os.path.getsize(dest_xlsx)} bytes)")

# Copy Width plot if exists
if os.path.exists("scratch/Width_vs_Year.png"):
    dest_png = "SuvarnaProject_data/Width_vs_Year.png"
    shutil.copyfile("scratch/Width_vs_Year.png", dest_png)
    print(f"Copied scratch/Width_vs_Year.png -> {dest_png}")

# Convert XLSX Sheet1 to CSV for fast pandas/csv reading
with zipfile.ZipFile(src_xlsx, "r") as z:
    shared_strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
            text = "".join(t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text)
            shared_strings.append(text)

    sheet_root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row_elem in sheet_root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
        row_cells = []
        for c in row_elem.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
            t = c.get("t")
            v_elem = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
            val = v_elem.text if v_elem is not None else ""
            if t == "s" and val:
                val = shared_strings[int(val)]
            row_cells.append(val)
        if row_cells:
            # Clean numeric years
            if rows: # data rows
                try:
                    row_cells[0] = str(int(float(row_cells[0])))
                except Exception:
                    pass
            rows.append(row_cells)

with open(dest_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Generated {dest_csv} ({len(rows)} rows)")

