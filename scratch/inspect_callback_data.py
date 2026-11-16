import re
import json

for i, fn in enumerate(["scratch/callback_1_ds:1.txt", "scratch/callback_3_ds:3.txt"]):
    with open(fn, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"\n================ Callback {fn} ================")
    # Extract the data field: data: function(){return [...]} or data: [...]
    # Try finding the data block
    m = re.search(r"data:\s*(function\(\)\{return\s*(.*?);?\}\s*\}|\s*(\[.*?\])\s*\})", content, re.DOTALL)
    if m:
        raw_json = m.group(2) or m.group(3)
        try:
            parsed = json.loads(raw_json)
            print(f"Successfully parsed JSON! Type: {type(parsed)}")
            with open(f"scratch/parsed_data_{i}.json", "w", encoding="utf-8") as out:
                json.dump(parsed, out, indent=2)
            print(f"Saved scratch/parsed_data_{i}.json")
        except Exception as e:
            print("JSON parse error:", e)
            # Find all strings inside content
            strs = re.findall(r'"([^"\\]{3,100})"', content)
            print("Extracted strings sample (first 40):", strs[:40])
    else:
        print("Data block regex didn't match directly, searching strings:")
        strs = re.findall(r'"([^"\\]{3,100})"', content)
        print("Sample strings (first 40):", strs[:40])

