from ...domain.factor_converter import FactorConverter
from ...domain.base_rule import BaseRule
from .reassignment_non_palletized_items_rule import ReassignmentNonPalletizedItemsRule
from ...domain.itemList import ItemList

class ReassignmentNonPalletizedItemsWithSplitItemRule(BaseRule):
    def __init__(self, factor_converter=None):
        super().__init__(name='ReassignmentNonPalletizedItemsWithSplitItemRule')
        self._reassignmentNonPalletizedItemsRule = ReassignmentNonPalletizedItemsRule(FactorConverter())

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        # Port of C# ShouldExecute: check setting and presence of items with amount remaining
        if not context.get_setting('ReassignmentOfNonPalletizedItems'):
            context.add_execution_log(f"Regra desativada, não será executada")
            return False

        # Use ItemList helper to mirror C# extension semantics
        if not ItemList(context.get_items()).with_amount_remaining().any():
            context.add_execution_log("Não foram encontrados itens não paletizados, a regra não será executada")
            return False

        return True

    def execute(self, context, *args, **kwargs):
        # Enable split item option then execute the inner rule's chain
        self._reassignmentNonPalletizedItemsRule.enable_split_item().execute(context)
        return context
