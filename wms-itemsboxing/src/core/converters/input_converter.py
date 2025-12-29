import logging 
from typing import List
from .errors import InputConversionError, UnexpectedType


class InputConverter:
    """Realiza a conversão dos dados do model de entrada para formato usado na biblioteca"""

    def _convert_client_and_skus(self, client: dict) -> dict:
        skus = {}
        for sku in client['skus']:
            skus.update({str(sku['code']): sku['quantity']})
            
        return {str(client['code']): skus}

    def _convert_maps(self, maps: List[dict]) -> dict:
        result = {}
        for map in maps:
            clients = {}
            for client in map['clients']:
                clients.update(self._convert_client_and_skus(client))
            result.update({str(map['code']): clients})
        return result

    def _convert_skus(self, name: str, items: List[dict]) -> dict:
        result = {}
        for item in items:
            cat = '00000000-0000-0000-0000-000000000000' if 'subcategory' not in item or item['subcategory'] is None else item['subcategory']
            new = {
                'length': item['length'],
                'height': item['height'],
                'width': item['width'],
                'units_in_boxes': item['units_in_boxes'],
                'tipo_garrafa': int(item['is_bottle']),
                'gross_weight': item.get('gross_weight', 0),                
                'subcategory': cat,
            }
           
            result.update({str(item['code']): new})
        return {name: result}

    def _convert_boxes(self, name: str, items: List[dict]) -> dict:
        result = {}
        for item in items:
            new = {
                'length': item['length'],
                'height': item['height'],
                'width': item['width'],
                'box_slots': item['box_slots'],
                'box_slot_diameter': item['box_slot_diameter'],
            }
            result.update({str(item['code']): new})
        return {name: result}

    def _convert_family_groups(self, name: str, items: List[dict]) -> dict:
        result = []
        if items is None:
            empty_category = {
            'subcategory': '00000000-0000-0000-0000-000000000000',
            'cant_go_with': [],
            }
            result.append(empty_category)
            return {name: result}

        for item in items:
            new = {
                'subcategory': item['subcategory'],
                'cant_go_with': item['cant_go_with'],
            }
            result.append(new)
        return {name: result}

    def convert(self, input: dict) -> dict:
        try:            
            if not isinstance(input, dict):
                raise UnexpectedType(input, 'dict')
            result = self._convert_maps(input['maps'])            
            result.update(self._convert_skus('skus', input['skus']))
            result.update(self._convert_boxes('boxes', input['boxes']))
            result.update(self._convert_family_groups('family_groups', input['family_groups']))            
            return result
        except Exception as ex:
            err = InputConversionError(ex)
            logging.exception(err)
            raise err from ex
