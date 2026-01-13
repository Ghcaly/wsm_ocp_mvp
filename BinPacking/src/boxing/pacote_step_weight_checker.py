from typing import Dict
import logging
import traceback


from boxing.items import Items
from boxing.logger import BoxingLogger

class PacoteStepWeightChecker:
   

    def calculate_package_weight(
        self,   
        sku: str,
        items: Dict[str, Items],
        max_weight: float
    ) -> bool:
        
        package_weight = items[sku].units_in_boxes*items[sku].gross_weight
        if package_weight <= max_weight:
            return True
        else: 
            return False
            
            