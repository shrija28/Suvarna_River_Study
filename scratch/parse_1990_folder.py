import re

with open("scratch/folder_1990.html", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pattern = re.compile(
    r'\[null,\"(1[a-zA-Z0-9_-]{25,50})\"\]'
    r'.*?\"(application/vnd\.google-apps\.folder|image/tiff|image/png|application/vnd\.openxmlformats-officedocument\.[^\"]+|\w+/[^\"]+)\"'
    r'.*?\[\[\[\"([^\"]+)\"',
    re.DOTALL
)

items = {}
for m in pattern.finditer(text):
    iid, mime, name = m.group(1), m.group(2), m.group(3)
    items[iid] = {"name": name, "mime": mime}

print(f"Items inside folder 1990: {len(items)}")
for k, v in items.items():
    print(f"  {v['name']} | id: {k} | mime: {v['mime']}")

# Also search for any png/tif files in general
direct = re.findall(r'\"([^\"]+\.(?:png|tif|jpg))\"', text)
print("Direct filename regex:", set(direct))

