import re
import json
from pathlib import Path

class FileHandler:
    @staticmethod
    def get_xml_files(path):
        input_path = Path(path)
        if not input_path.exists():
            return None
        
        if input_path.is_dir():
            return list(input_path.glob('*.xml'))
        else:
            return [input_path]
    
    @staticmethod
    def extract_map_number(filename):
        match = re.search(r'_[me]_mapa_(\d+)_', filename)
        return match.group(1) if match else None
    
    @staticmethod
    def generate_output_filename(input_filename, output_path):
        output_path = Path(output_path)
        input_path = Path(input_filename)
        
        map_number = FileHandler.extract_map_number(input_path.name)
        
        if output_path.is_dir():
            if map_number:
                return output_path / f"JsonInMapsV2{map_number}.json"
            else:
                return output_path / f"{input_path.stem}.json"
        else:
            return output_path
    
    @staticmethod
    def save_json(data, output_file):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
