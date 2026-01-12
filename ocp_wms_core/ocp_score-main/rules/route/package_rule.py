from domain.itemList import ItemList
from domain.space_list import SpaceList
from domain.base_rule import BaseRule


class PackageRule(BaseRule):
    def __init__(self, factor_converter = None):
        super().__init__()
        self.factor_converter = factor_converter

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
    
        items = ItemList(context.get_items()).is_package().with_amount_remaining().ordered_by_amount_remaining_desc()
        if not items:
            context.add_execution_log("Não foram encontrados itens marketplace com quantidade a paletizar, parando execução da regra")
            return False

        available_spaces = SpaceList(context.get_not_full_spaces()).ordered_by_package_then_occupation(context)
        if not available_spaces:
            context.add_execution_log("Não foram encontradas baias não cheias para paletizar os itens marketplace, parando execução da regra")
            return False
        
        return True

    def execute(self, context):

        items = ItemList(context.get_items()).is_package().with_amount_remaining().ordered_by_amount_remaining_desc()
        
        available_spaces = SpaceList(context.get_not_full_spaces()).ordered_by_package_then_occupation(context)

        for item in items:
            units_per_box = item.product.units_per_box
            if units_per_box == 0:
                continue

            for space in available_spaces:
                if item.amount_remaining < units_per_box:
                    break

                mounted_space = context.get_mounted_space(space)

                min_occupation = self.factor_converter.occupation(units_per_box, space.size, item, context.get_setting('OccupationAdjustmentToPreventExcessHeight'))
                packages_quantity = 1
                retries = 0

                # while CanPalletizePackage equivalent
                while (context.domain_operations.can_add(context, space, item, units_per_box)
                       and item.amount_remaining >= units_per_box
                       and min_occupation <= space.size
                       and (mounted_space is None or mounted_space.occupation_remaining >= min_occupation)):

                    first_layer = mounted_space.get_next_layer() if mounted_space is not None else 0
                    quantity_of_layer = item.product.get_quantity_of_layer_to_space(space.size, units_per_box)
                    mounted_space = context.AddProduct(space, item, units_per_box, first_layer, quantity_of_layer, min_occupation, packages_quantity)
                    retries += 1
                    context.add_execution_log(f"Paletizando o item: {item.Code} na quantidade: {units_per_box} na baia: {mounted_space.Space.Number} / {mounted_space.Space.sideDesc} e ocupação {min_occupation}")
