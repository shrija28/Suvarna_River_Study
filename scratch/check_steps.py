import json

with open(r"C:\Users\LENOVO\.gemini\antigravity\brain\92f670cd-818e-4f15-aa32-6f8e546a64be\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") in [825, 828, 836, 1326]:
            print(f"Step {data.get('step_index')} [{data.get('source')}]: {str(data.get('content'))[:200]}")
            if data.get("media"):
                print("  Media:", data.get("media"))

