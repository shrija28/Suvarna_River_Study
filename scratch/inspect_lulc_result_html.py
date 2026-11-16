import re

for yr in ["1990", "2020"]:
    fname = f"scratch/lulc_result_{yr}.html"
    try:
        with open(fname, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        files = re.findall(r'\"([^\"]+\.(?:tif|csv|png|jpg|pdf|json))\"', text)
        print(f"Files in LULC_Result/{yr}:", set(files))
    except Exception as e:
        print(e)

