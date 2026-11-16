import re
import json

with open("gdrive_folder.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

callbacks = re.findall(r"AF_initDataCallback\((\{.*?\})\);", text, re.DOTALL)
print(f"Total callbacks: {len(callbacks)}")

for i, cb in enumerate(callbacks):
    print(f"\n--- Callback {i} (len {len(cb)}) ---")
    # Extract key and data
    key_m = re.search(r"key:\s*'([^']+)'", cb)
    key = key_m.group(1) if key_m else "unknown"
    print(f"Key: {key}")
    
    # Save to file for inspection
    with open(f"scratch/callback_{i}_{key}.txt", "w", encoding="utf-8") as out:
        out.write(cb)

