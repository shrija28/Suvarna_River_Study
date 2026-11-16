import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile("scratch/Suvarna_First_Opening_Results.xlsx", "r") as z:
    # 1. Parse shared strings
    shared_strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
            text = "".join(t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text)
            shared_strings.append(text)

    # 2. Parse sheet1.xml
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
            rows.append(row_cells)

print(f"Total rows in Sheet1: {len(rows)}")
for r in rows[:45]:
    print(r)

