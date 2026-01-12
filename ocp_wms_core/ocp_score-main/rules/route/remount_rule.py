from domain.itemList import ItemList
from .non_palletized_products_rule import NonPalletizedProductsRule
from .returnable_and_disposable_split_remount_rule import ReturnableAndDisposableSplitRemountRule
from domain.base_rule import BaseRule
from domain.factor_converter import FactorConverter

class RemountRule(BaseRule):
    """Faithful port of C# RemountRule.

    This port is direct: it implements ShouldExecute by checking for items
    (not marketplace, not chopp, not isotonic water, with amount remaining)
    and Execute calls the injected rules' ExecuteChain methods exactly as
    the C# implementation.
    """

    def __init__(self):
        super().__init__()
        self.non_palletized_rule = NonPalletizedProductsRule(factor_converter=FactorConverter())
        self.returnable_remount_rule = ReturnableAndDisposableSplitRemountRule(factor_converter=FactorConverter())

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        items = (ItemList(context.get_items())
            .not_marketplace().not_chopp().not_isotonic_water()
            .with_amount_remaining()
        )
        
        if not items:
            context.add_execution_log("Nenhum item elegivel para remount encontrado, pulando regra de remount.")
            return False
        
        context.add_execution_log(f"Items elegiveis para remount: {len(items)}")
        return True

    def execute(self, context):
        # follow C# ordering: first run non-palletized products rule with the item predicate
        item_pred = lambda x: (
                        x.NotChopp() and 
                        x.NotMarketplace() and 
                        x.NotIsotonicWater() and 
                        x.HasAmountRemaining()
                    )
        # item_pred = x => x.NotChopp() && x.NotMarketplace() && x.NotIsotonicWater() && x.HasAmountRemaining();
        # call the non-palletized products rule's ExecuteChain
        self.non_palletized_rule.execute(context, item_predicate=item_pred)

        # then call the returnable/disposable remount rule's ExecuteChain
        self.returnable_remount_rule.execute(context)
