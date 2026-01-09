from pathlib import Path
import json

config_route = Path(r'C:\prd_debian\ocp_wms_core\ocp_score-main\data\route\126056\config.json')

if config_route.exists():
    data = json.loads(config_route.read_text(encoding='utf-8-sig'))
    print(f'Settings: {len(data.get("Settings", {}))} params')
    print(f'Keys: {list(data.keys())}')
    print(f'MapNumber: {data.get("MapNumber")}')
    
    if len(data.get("Settings", {})) > 0:
        print(f'\nPrimeiros 5 Settings:')
        for i, key in enumerate(list(data["Settings"].keys())[:5]):
            print(f'  {key}: {data["Settings"][key]}')
    else:
        print('\nSettings está VAZIO!')
else:
    print('Arquivo não existe')
