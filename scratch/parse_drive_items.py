import re

with open("scratch/callback_3_ds:3.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's extract all matches of ID and Name
# In Drive data, items appear with an alphanumeric ID (e.g., 15Y2km4gxhbdCVPf7PqQDOVi5fUdOZW0H)
# followed or preceded by title, mimeType, dates, etc.
# Find all Google Drive item IDs (28-44 chars)
item_ids = re.findall(r'\"(1[a-zA-Z0-9_-]{27,45})\"', text)
print(f"Total IDs matching pattern: {len(item_ids)}")
print("Unique IDs:", set(item_ids))

# Let's see the structure surrounding these IDs
for i_id in set(item_ids):
    pos = text.find(i_id)
    snippet = text[max(0, pos - 150): min(len(text), pos + 300)]
    print(f"\n--- Context for ID: {i_id} ---")
    print(snippet)

