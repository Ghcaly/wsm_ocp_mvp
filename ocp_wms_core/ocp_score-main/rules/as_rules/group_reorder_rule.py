from ..common.reorder_rule import ReorderRule
from domain.base_rule import BaseRule
from domain.mounted_product_list import MountedProductList


class GroupReorderRule(BaseRule):
    """Faithful Python port of C# GroupReorderRule.
    
    Reorders products within containers by product group code to optimize assembly sequence.
    Uses the OrderPalletByProductGroup setting to determine if group-based ordering is enabled.
    
    Flow:
    1. Check if OrderPalletByProductGroup is enabled
    2. If disabled, execute fallback ReorderRule
    3. For each container in each mounted space:
       - Reset all assembly sequences to 0
       - Group products by type (chopp, returnable, disposable, isotonic water, top of pallet)
       - Set assembly sequence for each group ordered by group code
    """

    def __init__(self):
        super().__init__()
        self.reorder_rule = ReorderRule()

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        """Always execute - either group reorder or fallback to route reorder"""
        return True

    def execute(self, context, item_predicate=None, mounted_space_predicate=None):
        """C#: Execute - reorder products by group code or fallback to route reorder"""
        # Check if group-based ordering is enabled
        if not context.get_setting('OrderPalletByProductGroup', False):
            # Fallback to route reorder rule
            if self.reorder_rule:
                self.reorder_rule.execute(context)
            return

        # For each mounted space and each container, set assembly sequence by groups
        for mounted_space in context.MountedSpaces:
            for container in mounted_space.Containers:
                products = MountedProductList(container.Products)
                
                # Skip if only 1 or no products
                if products.count() <= 1:
                    continue

                # Reset all assembly sequences to 0
                for product in products:
                    product.SetAssemblySequence(0)

                # Group products by type and filter
                chopp = products.IsChopp().NotTopOfPallet().NotIsotonicWater()
                returnable = products.IsReturnable().NotTopOfPallet().NotChopp().NotIsotonicWater()
                disposable = products.NotReturnable().NotTopOfPallet().NotChopp().NotIsotonicWater()
                isotonic_water = products.IsIsotonicWater().NotTopOfPallet().NotChopp().NotBasePallet()
                top_of_pallet = products.IsTopOfPallet().NotChopp().NotIsotonicWater().NotBasePallet()

                # Set assembly sequence for each group ordered by group code
                self.set_assembly_sequence_by_group_code(container, chopp)
                self.set_assembly_sequence_by_group_code(container, returnable)
                self.set_assembly_sequence_by_group_code(container, disposable)
                self.set_assembly_sequence_by_group_code(container, isotonic_water)
                self.set_assembly_sequence_by_group_code(container, top_of_pallet)

    def set_assembly_sequence_by_group_code(self, container, products):
        """C#: SetAssemblySequenceByGroupCode - orders products by group code and sets assembly sequence"""
        # Order products by PackingGroup.GroupCode
        ordered_products = products.OrderByGroupCode()
        
        # Increase assembly sequence for each product in order
        for product in ordered_products:
            container.IncreaseAssemblySequence(product)
