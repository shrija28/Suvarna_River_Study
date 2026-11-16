with open("scratch/gdrive_page.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# Find surrounding context around 'river mouth images'
pos = 0
while True:
    idx = html.lower().find("river mouth images", pos)
    if idx == -1:
        break
    start = max(0, idx - 500)
    end = min(len(html), idx + 500)
    print(f"\n--- Context around index {idx} ---")
    print(html[start:end])
    pos = idx + len("river mouth images")
