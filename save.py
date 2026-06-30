import json

with open("save.json", "r", encoding="utf-8") as f:
    save = json.load(f)

print(save)