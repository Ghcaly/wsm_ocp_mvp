import copy
from typing import Dict, List
import logging

from boxing.logger import BoxingLogger
from boxing.items import Items
from boxing.orders import Orders

class FamilySeparator:

    def __init__(
        self, 
        items: Dict[str, Items],
        map_id: str,
        family_groups: List[Dict[str, str]],
        verbose: bool
    ) -> None:

        self._verbose = verbose
        self._logger = BoxingLogger(map_id = map_id, name =  str(map_id)+'_family_separator_log', verbose = self.verbose).logger
        self._items = items 
        self._family_compatibility = self._family_setup(family_groups)

    @property
    def verbose(self) -> bool:
        return self._verbose
    
    @property
    def logger(self) -> logging:
        return self._logger
    
    @property
    def items(self) -> Dict[str, Items]:
        return self._items 

    @property
    def family_compatibility(self) -> Dict[str, set]:
        return self._family_compatibility

    def _family_setup(
        self, 
        family_groups: Dict[int, Dict]
    ) -> Dict:
        family_compatibility = {}
        for fc in range(len(family_groups)):
            family = family_groups[fc]['subcategory']
            family_compatibility[str(family)] = set([str(cgw) for cgw in family_groups[fc]['cant_go_with']])
        return family_compatibility

    def _count_family_members(
        self, 
        orders_by_sku: Dict[str, Dict]
    ):
        f_count = {}
        skus_without_families = []
        for s in orders_by_sku.keys():
            subcat = self.items[s].subcategory
            if subcat == "-1":
                skus_without_families.append(s)
            elif subcat != "-1" and subcat in f_count.keys(): 
                f_count[subcat] = f_count[subcat] + orders_by_sku[s]
            else:
                f_count[subcat] = orders_by_sku[s]
        return f_count, skus_without_families

    def group_orders_sku(
        self, 
        orders_nf: Dict[str, Dict]
    ) -> Dict[str, int]:
        grouped_orders = {}
        for nf in orders_nf.orders_by_invoice.keys():
            for sku in orders_nf.orders_by_invoice[nf].keys():
                if sku in list(grouped_orders.keys()):
                    grouped_orders[sku] = grouped_orders[sku] +  orders_nf.orders_by_invoice[nf][sku]
                else:
                    grouped_orders[sku] =  orders_nf.orders_by_invoice[nf][sku]
        return grouped_orders
    
    def get_family(
        self, 
        groups: Dict[int, List], 
        current_family_count: int
    ):
        largest_family = max(current_family_count, key=current_family_count.get)
        fam_incompatibility = self.family_compatibility[largest_family]
        if groups == {}:
            groups[0] = [largest_family]
        else: 
            entered_existing_group = 0
            for i in range(len(list(groups.keys()))):
                if entered_existing_group == 0:
                    group = copy.deepcopy(groups[i])
                    set_group = set(group)
                    if (fam_incompatibility - set_group) == fam_incompatibility:
                        group.append(largest_family)
                        groups[i] = group
                        entered_existing_group = 1
                        break
            if entered_existing_group == 0:
                groups[len(groups)]= [largest_family]
        current_family_count.pop(largest_family)
        return groups, current_family_count

    def group_families(self, orders):
        orders_by_sku = self.group_orders_sku(orders)
        family_count, skus_without_families = self._count_family_members(orders_by_sku)
        family_count_len = len(list(family_count.keys()))
        groups = {}
        for _ in range(family_count_len):
            groups, family_count = self.get_family(groups, family_count)
        for s in skus_without_families:
            groups[len(groups)]= [s]
        return groups

    def filter_maps_no_subcategory(
        self,
        s: str,
        nf: str,
        current_family_order_nf: Dict[str, int],
        original_orders_nf: Dict[str, int],
        new_orders: Dict[str, Dict],
    ):
        if s in current_family_order_nf.keys():
            current_family_order_nf[s] = current_family_order_nf[s] + original_orders_nf[nf][s]
            new_orders[nf].pop(s)
        elif  ~(s in current_family_order_nf.keys()):
            current_family_order_nf[s] = original_orders_nf[nf][s]
            new_orders[nf].pop(s)
        return new_orders, current_family_order_nf

    def filter_maps_invoice_number(
        self, 
        original_orders_nf, 
        current_group, 
        new_orders, 
        nf
    ):
        
        current_family_order_nf = {}
        new_orders_original = copy.deepcopy(new_orders)
        for s in new_orders_original[nf].keys():
            s_subcategory = self.items[s].subcategory
            if s_subcategory == '-1':
                new_orders, current_family_order_nf = self.filter_maps_no_subcategory(s, nf, current_family_order_nf, original_orders_nf, new_orders)
            elif s_subcategory in current_group and s in current_family_order_nf.keys():
                current_family_order_nf[s] = current_family_order_nf[s] + original_orders_nf[nf][s]
                new_orders[nf].pop(s)
            elif s_subcategory in current_group and ~(s in current_family_order_nf.keys()):
                current_family_order_nf[s] = original_orders_nf[nf][s]
                new_orders[nf].pop(s)
            if nf not in new_orders.keys():
                return new_orders, current_family_order_nf
            elif new_orders[nf] == {}:
                new_orders.pop(nf)
        return new_orders, current_family_order_nf

    def filter_maps(self, orders, groups):
        new_orders = copy.deepcopy(orders.orders_by_invoice)
        orders_by_family = []
        for i in range(len(groups)):
            current_family_orders = {}
            for nf in orders.orders_by_invoice.keys():
                if nf in new_orders.keys():
                    new_orders, current_family_order_nf = self.filter_maps_invoice_number(orders.orders_by_invoice, groups[i], new_orders, nf)        
                    if current_family_order_nf != {}:
                        current_family_orders[nf] = current_family_order_nf
            if current_family_orders != {}:
                orders_by_family.append(current_family_orders)
        return orders_by_family



