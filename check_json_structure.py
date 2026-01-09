import json

json_path = r'C:\prd_debian\mapas\in\input.json'
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

print(f"Top-level keys: {list(data.keys())}")
print(f"MapNumber: {data.get('MapNumber')}")
print(f"Number: {data.get('Number')}")
print(f"Type: {data.get('Type')}")

if 'Map' in data:
    print(f"\nMap sub-keys: {list(data['Map'].keys())}")
    print(f"Map.Number: {data['Map'].get('Number')}")
