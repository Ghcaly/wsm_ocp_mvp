from typing import Dict

from boxing.items import Items
from boxing.boxes import Boxes

class CaixaStepWeightChecker:
   
    def calculate_box_weight(
        self,   
        box: Dict[int, int],
        items: Dict[str, Items]
    ) -> float:
        
        box_weight = 0
        for sku in box.keys():
            box_weight = box_weight + items[sku].gross_weight*box[sku]

        return box_weight

    def calculate_box_occupation_volume(
        self,   
        box: Dict[int, int],
        items: Dict[str, Items],
        box_info: Boxes
    ) -> float:
        
        box_volume = box_info.height*box_info.length*box_info.width
        box_volume_occupied = 0
        for sku in box.keys():
            item_volume_total = box[sku]*items[sku].height*items[sku].length*items[sku].width
            box_volume_occupied = box_volume_occupied + item_volume_total
        return 100*(box_volume_occupied/box_volume)
            
            



