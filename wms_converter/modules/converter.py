import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
from pathlib import Path
import csv

class XmlConverter:
    def __init__(self):
        self.bay_sizes_cache = None
        self.bay_csv_path = Path(__file__).parent.parent / 'data' / 'VehichelBay.csv'
    def convert(self, input_file, output_file, **overrides):
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        filename = Path(input_file).name
        
        result = {
            "Type": 1,
            "Number": overrides.get('number', self._extract_number(root)),
            "DeliveryDate": overrides.get('delivery_date', self._extract_delivery_date(root)),
            "Warehouse": {
                "UnbCode": self._extract_unbcode(root),
                "FileName": filename,
                "Company": root.get('empresa', ''),
                "Branch": root.get('filial', '')
            },
            "Vehicle": {
                "Plate": overrides.get('plate', self._extract_plate(root)),
                "Bays": self._extract_bays(root)
            },
            "Orders": self._extract_orders(root, overrides),
            "UniqueKey": overrides.get('unique_key', self._generate_unique_key(filename))
        }
        
        return result
    
    def _generate_unique_key(self, filename):
        return hashlib.md5(filename.encode()).hexdigest()
    
    def _extract_number(self, root):
        return root.findtext('.//nrMapa', 'UNKNOWN')
    
    def _extract_delivery_date(self, root):
        date_str = root.findtext('.//dataEntrega')
        if date_str and len(date_str) == 8:
            try:
                year = date_str[0:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}T00:00:00"
            except:
                pass
        return datetime.now().isoformat()
    
    def _extract_unbcode(self, root):
        filial = root.get('filial', '')
        return filial[-3:] if len(filial) >= 3 else filial
    
    def _extract_plate(self, root):
        return root.findtext('.//cdPlaca', '')
    
    def _load_bay_sizes(self):
        """Carrega tamanhos de baias do CSV"""
        if self.bay_sizes_cache is not None:
            return self.bay_sizes_cache
        
        self.bay_sizes_cache = {}
        
        if not self.bay_csv_path.exists():
            return self.bay_sizes_cache
        
        try:
            with open(self.bay_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Id'] == '--':  # Skip header separator
                        continue
                    key = (int(row['Side']), int(row['Number']))
                    self.bay_sizes_cache[key] = int(row['BaySize'])
        except Exception:
            pass
        
        return self.bay_sizes_cache
    
    def _get_bay_size(self, side_code, bay_number):
        """Busca tamanho da baia no CSV ou retorna tamanho padrão"""
        bay_sizes = self._load_bay_sizes()
        key = (side_code, bay_number)
        return bay_sizes.get(key, 35)  # 35 é o tamanho padrão
    
    def _extract_bays(self, root):
        bays = []
        for baia_elem in root.findall('.//baia'):
            bay_number = int(baia_elem.findtext('nrBaiaGaveta', '0'))
            side_letter = baia_elem.findtext('cdLado', 'A')
            side_code = ord(side_letter)
            
            # Converte Side de ord() para 0, 1, 2... (A=65->0, B=66->1, etc)
            side_index = side_code - ord('A')
            
            bay = {
                "Number": bay_number,
                "Side": side_code,
                "Size": self._get_bay_size(side_index, bay_number)
            }
            bays.append(bay)
        return bays
    
    def _extract_orders(self, root, overrides):
        orders = []
        
        for nota_elem in root.findall('.//nota_fiscal'):
            order = {
                "RoadShow": int(nota_elem.findtext('ordemRoadshow', '0')),
                "Cross": {
                    "Vehicle": {
                        "Plate": nota_elem.findtext('nrPlacaEntrega', ''),
                        "Bays": []
                    },
                    "SupportPoint": overrides.get('support_point', nota_elem.findtext('cdPa', '')),
                    "MapNumber": nota_elem.findtext('nrMapaEntrega', '')
                },
                "Client": {
                    "Code": nota_elem.findtext('cdCliente', '')
                },
                "Items": self._extract_items(nota_elem)
            }
            orders.append(order)
        
        return orders
    
    def _extract_items(self, nota_elem):
        items = []
        
        for item_elem in nota_elem.findall('.//item'):
            item = {
                "Code": item_elem.findtext('cdItem', ''),
                "Quantity": {
                    "Sales": int(item_elem.findtext('qtUnVenda', '0')),
                    "Unit": int(item_elem.findtext('qtUn', '0')),
                    "Detached": int(item_elem.findtext('qtUnAvulsa', '0'))
                },
                "UnitOfMeasurement": None
            }
            items.append(item)
        
        return items
