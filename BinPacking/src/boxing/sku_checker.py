from typing import Dict, List

class skuChecker:

    """Represents the class that checks and takes action on missing SKUs in the run of the algorithm
    """

    def get_all_items(self, orders):
        skus_in_orders = [list(orders[k].keys()) for k in orders.keys()]
        flat_list = [item for sublist in skus_in_orders for item in sublist]
        return list(set(flat_list))

    def check_skus_missing(
        self, 
        item: str, 
        items_list: List
    ) -> bool:
        if item in items_list:
            return True
        else:
            return False

    def remove_skus(
        self, 
        orders: Dict[str, Dict], 
        items_list: List
    ):
        new_orders = {}
        current_order = {}
        items_dict = {il: 0 for il in items_list}
        for od in orders.keys():
            current_order = {}
            for sku in orders[od].keys():
                if sku in items_list:
                    items_dict[sku] = items_dict[sku] + orders[od][sku]
                else:
                    current_order[sku] = orders[od][sku]
            if current_order != {}:
                new_orders[od] = current_order
        return new_orders, items_dict

    def check_all_skus_missing(
        self,
        map_config,
        algo_items
    ):
        all_items = self.get_all_items(map_config)
        missing_items = []
        items_list = list(algo_items.keys())
        nao_paletizados = {}
        for ai in all_items:
            if self.check_skus_missing(ai, items_list) == False:
                missing_items.append(ai)
        if missing_items != []:
            new_map_config, nao_paletizados = self.remove_skus(
                map_config, missing_items)
        else:
            new_map_config = map_config
        return new_map_config, nao_paletizados
