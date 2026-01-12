from rules.route.bulk_pallet_rule import BulkPalletRule
from rules.route.chopp_palletization_rule import ChoppPalletizationRule
from domain.base_rule import BaseRule
from typing import List


class ComplexGroupLoadRule(BaseRule):
    """Faithful port of the C# ComplexGroupLoadRule.

    This class calls attributes and methods directly (no defensive checks)
    to stay as close as possible to the original C# implementation.
    """

    def __init__(self, factor_converter):
        super().__init__()
        self._factor_converter = factor_converter
        self._bulk_pallet_rule = BulkPalletRule()
        self._chopp_palletization_rule = ChoppPalletizationRule()

    def _get_items_that_can_be_grouped(self, context):
        # Equivalent to: var smallerSpace = context.GetNotFullSpaces().OrderByDescending(x => (int)x.Size).FirstOrDefault();
        smaller_spaces = sorted(context.get_not_full_spaces(), key=lambda x: int(x.size), reverse=True)
        smaller_space = smaller_spaces[0] if smaller_spaces else None
        if smaller_space is None:
            return None

        clients = set()
        for o in context.orders:
            for it in o.items:
                for k in it.client_quantity.keys():
                    clients.add(k)

        grouped_loads = []
        for client in clients:
            items = []
            for o in context.orders:
                for it in o.items:
                    # C#: .Where(x => x.Items.CanBePalletized().SelectMany(y => y.ClientQuantity.Keys).Contains(client))
                    # Here assume item.can_be_palletized() exists and item.client_quantity is a dict
                    if it.can_be_palletized():
                        if client in it.client_quantity:
                            items.append(it)

            sku_quantity = len(set([y.code for y in items]))
            if sku_quantity < context.get_setting('QuantitySkuInComplexLoads'):
                continue

            total_occupation = 0
            for y in items:
                total_occupation += self._factor_converter.occupation(y.client_quantity[client], smaller_space.size, y, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))

            if total_occupation < context.get_setting('MinimumVolumeInComplexLoads'):
                continue

            load = type('GroupLoadDto', (), {})()
            load.items = items
            load.client_code = client
            load.total_occupation = total_occupation
            load.sku_quantity = sku_quantity

            grouped_loads.append(load)

        return grouped_loads

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None) -> bool:

        if context.context_kind in ('as', 'crossdock'):
            context.add_execution_log("Regra de agrupamento de cargas complexas não aplicável para contextos AS ou Crossdock, não será executada")  
            return False
            
        if not context.get_setting('GroupComplexLoads'):
            context.add_execution_log("Regra de agrupamento de cargas complexas desativada, não será executada")
            return False

        clients_quantity = len(set(k for o in context.orders for it in o.items for k in it.client_quantity.keys()))
        if clients_quantity <= 1:
            context.add_execution_log("Não há clientes suficientes para agrupar cargas complexas, a regra não será executada")
            return False

        any_complex_client = bool(self._get_items_that_can_be_grouped(context))

        if not any_complex_client:
            context.add_execution_log("Não há clientes complexos suficientes para agrupar cargas complexas, a regra não será executada")
            
        return any_complex_client

    def execute(self, context):
        client = sorted(self._get_items_that_can_be_grouped(context), key=lambda x: x.total_occupation, reverse=True)[0]
        mounted_spaces = []

        # call dependent rules as the C# implementation does
        self._bulk_pallet_rule.with_complex_customer(client.client_code).execute(context, lambda x: client.client_code in x.client_quantity)
        self._chopp_palletization_rule.with_complex_customer(client.client_code).without_group_limit().execute(context, lambda x: client.client_code in x.client_quantity)

        for item in client.items:
            self._mount_complex_space(context, client, mounted_spaces, item)

        for ms in [m for m in context.mounted_spaces if m.occupied_percentage >= 90]:
            ms.Block()

    def _mount_complex_space(self, context, client, mounted_spaces: List[object], item):
        palletized_mounted_space = None
        retries = 0

        while True:
            if not mounted_spaces:
                space = self._get_next_space(context)
            else:
                candidates = [m for m in mounted_spaces if m.occupation_remaining >= self._factor_converter.occupation(item.client_quantity[client.client_code], m.space.size, item, context.get_setting('occupation_adjustment_to_prevent_excess_height', False))]
                if candidates:
                    space = sorted(candidates, key=lambda x: x.occupation_remaining)[0].space
                else:
                    space = self._get_next_space(context)

            if space is None:
                break

            palletized_mounted_space = self._mount_product(client.client_code, context, space, item)
            if palletized_mounted_space and palletized_mounted_space not in mounted_spaces:
                mounted_spaces.append(palletized_mounted_space)

            retries += 1
            if not (palletized_mounted_space and space and item.client_quantity[client.client_code] > 0):
                break

    def _get_next_space(self, context):
        return sorted(context.spaces, key=lambda x: (int(x.size), int(x.number), getattr(x, 'side', 0)))[0]

    def _mount_product(self, client, context, space, item):
        mounted_space = context.get_mounted_space(space)
        factor = item.product.get_factor(space.size)

        quantity = item.client_quantity[client]
        if mounted_space is None:
            factor_quantity = int(self._factor_converter.quantity_per_factor(int(space.size), quantity, factor, item, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)))
            if factor_quantity < quantity:
                quantity = factor_quantity
        else:
            quantity = int(self._factor_converter.quantity_to_remaining_space(mounted_space, item, quantity, context.Settings))

        occupation = self._factor_converter.occupation(quantity, factor, item.product.PalletSetting, item, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))

        remaining_occupation = int(space.size) - (mounted_space.occupation if mounted_space else 0)
        if quantity == 0 or occupation > remaining_occupation:
            return None

        new_mounted_space = context.add_complex_load_product(space, item, quantity, occupation, client)
        for container in new_mounted_space.containers:
            container.block()

        return new_mounted_space
