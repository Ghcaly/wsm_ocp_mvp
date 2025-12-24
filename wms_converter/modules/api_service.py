import tempfile
import json
from pathlib import Path
from .converter import XmlConverter
from .file_handler import FileHandler


class ApiService:
    def __init__(self):
        self.converter = XmlConverter()
    
    def convert_xml_content(self, xml_content: str, overrides: dict = None):
        if overrides is None:
            overrides = {}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as tmp_xml:
            tmp_xml.write(xml_content)
            tmp_xml_path = tmp_xml.name
        
        try:
            result = self.converter.convert(tmp_xml_path, '', **overrides)
            return result
        finally:
            Path(tmp_xml_path).unlink(missing_ok=True)
    
    def convert_xml_file(self, file_path: str, overrides: dict = None):
        if overrides is None:
            overrides = {}
        
        result = self.converter.convert(file_path, '', **overrides)
        return result
