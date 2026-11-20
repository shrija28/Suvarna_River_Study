import os
import urllib.request
import time

files = {
  "LULC_1989.png": "1VPVPU27eLRXt1lc2UXdFK5zGUFJ21OQk",
  "LULC_1990.png": "1Y0Ka0cuyIVMxeIhng43mjktAw1LX010k",
  "LULC_1991.png": "1QAknvLjEitj0RydfljCDV-7gnf2WCVc9",
  "LULC_1992.png": "1E-xoll9ekVwOX0QFPrAC9UBFEN9fLv1L",
  "LULC_1993.png": "1Tk70vPwOgOjxK8-EOEPuZLc7Xxui-oWV",
  "LULC_1994.png": "1CzWDr40WmTpK28l3rRZsOyj9jWckL46Y",
  "LULC_1996.png": "1ek-W125syIqFewsEwVDZHVAtENoyuw4l",
  "LULC_1997.png": "1o-y6fkGeHDbebVuyZXdq0FoKoo4S7AjR",
  "LULC_1998.png": "1gz24caOTVDw2RLEaUxKVmKYVPpOa6OCB",
  "LULC_1999.png": "1lzVYqXsu5bqTkgyib0vbXxvaEpOZ3v26",
  "LULC_2000.png": "1BH8YF_qsg7QmsyuKVmgztpXgDDH1e1uS",
  "LULC_2001.png": "13xu-v_H4RRIkGldTKERH3d8XyGcPP1pa",
  "LULC_2002.png": "1AUGdYpZ2v7ATqJREGM-QjpTCrbIuJC9z",
  "LULC_2004.png": "1LpALo5SwNiK_DP2yXHNbstcXvuXFU1jh",
  "LULC_2005.png": "1VIrgDW03f3jvsKRoqcJNTppQsYwonhJH",
  "LULC_2006.png": "1vlJ59GeRiqPcre45qUIIP9mgbC2wTfFQ",
  "LULC_2007.png": "1_ZbLg1cwNJvjRfsaXh0i7sHjvSNCVNbm",
  "LULC_2008.png": "1Pl6PZCHyb9suSDUJST6rhR_NIjYOra6-",
  "LULC_2009.png": "1rAMf3tMq5WpmO2KDwTgektsCmAkL3iMA",
  "LULC_2010.png": "1iTJ3eqzaWClo-uNKhbekIn8RWTB81U_R",
  "LULC_2011.png": "19qumv8MXvM2iQgg7YF6SyPqVz_PO13oL",
  "LULC_2012.png": "1nkGeo1I2fgN-ai_L0PfkF9JqEAu7Fxig",
  "LULC_2013.png": "1OSolEvkh6EGjjpgn9HrvxJBSI3ZuzVMp",
  "LULC_2014.png": "1NSNFgT1Cq43eJ4KHTJzJkiNSFgUXqXqB",
  "LULC_2015.png": "1-FYq-P8VnXE9BKCp_dHNDSPvQuQQicy3",
  "LULC_2016.png": "1x5C7dpUZLQF0gXDjwFXxb2k_16oC-4_J",
  "LULC_2017.png": "1Vp28_bFrgFDxq0FLRbTdKJYfUi158_RK",
  "LULC_2018.png": "1Q95kkAzB18CXIUyWAAwYBN5yn9S1aSbE",
  "LULC_2019.png": "1gMtmmFPCgdYqHSLxLVwwJJuFkW55zbrR",
  "LULC_2020.png": "1PpdzCwsv3F7qzi2o2uJvGGGdTVS7L3y9",
  "LULC_2021.png": "1FfhnNN5MwA2RYyjyubVD1_BuvdaiYRAa",
  "LULC_2022.png": "1vqWokr-lYS07ryu9UhhPFBPNGrK4FbXf",
  "LULC_2023.png": "1KCtqLBaTHG_dAlmkU3QMrkKuVZcB4iVo",
  "LULC_2024.png": "1qIo6Qx9pGuxJbhELCJSHhIcokI1UuWmB",
  "LULC_2025.png": "1YeMg7Tn4nnY4DEnS30UpNYIJA4A7qN_b",
  "LULC_2026.png": "1b856KGhW6lzGQsZF71csAIzZTPrPxCBK"
}

target_dir = os.path.abspath(os.path.join("SuvarnaProject_data", "LULC_images"))
os.makedirs(target_dir, exist_ok=True)
print(f"Target directory: {target_dir}")

success_count = 0
for idx, (filename, fid) in enumerate(sorted(files.items()), 1):
    out_file = os.path.join(target_dir, filename)
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100000:
        print(f"[{idx}/{len(files)}] Already exists: {filename} ({os.path.getsize(out_file)} bytes)")
        success_count += 1
        continue

    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download"
    print(f"[{idx}/{len(files)}] Downloading {filename}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    retries = 3
    downloaded = False
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 1000 and data.startswith(b'\x89PNG'):
                    with open(out_file, 'wb') as f:
                        f.write(data)
                    print(f"  -> Saved {filename} ({len(data)} bytes)")
                    success_count += 1
                    downloaded = True
                    break
                else:
                    print(f"  -> Attempt {attempt+1}: Not a valid PNG (got {len(data)} bytes)")
        except Exception as e:
            print(f"  -> Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    if not downloaded:
        print(f"  FAILED to download {filename}")

print(f"\nFinished: Successfully downloaded {success_count}/{len(files)} LULC images into {target_dir}")
