from rules.as_rules import *

from domain.rule_chain import RuleChain
from domain.factor_converter import FactorConverter

class AsRuleFactories:
    def __init__(self) -> None:
        self.factor_converter = FactorConverter()

    def create_as_chain(self, name: str = "as") -> RuleChain:
        chain = RuleChain(name=name)
        fc = self.factor_converter
        chain.add_rule(self._make_rule(NumberOfPalletsRule, fc))
        chain.add_rule(self._make_rule(DistributeMixedRouteOnASRule, fc))
        chain.add_rule(self._make_rule(BaysNeededRule, fc))
        chain.add_rule(self._make_rule(ASRouteRule, fc))
        chain.add_rule(self._make_rule(NonPalletizedRouteRule, fc))
        chain.add_rule(self._make_rule(RecalculateNonPalletizedProductsRule, fc))
        chain.add_rule(self._make_rule(ReallocateNonPalletizedItemsOnSmallerPalletRule, fc))
        chain.add_rule(self._make_rule(SeparateRemountBaysAndLayerBaysRule, fc))
        chain.add_rule(self._make_rule(GroupReorderRule, fc))
        return chain
    
    
    def _make_rule(self, rule_cls, factor_converter: FactorConverter):
        """Try to instantiate rule_cls with a factor_converter argument when accepted.

        Fallbacks:
        - rule_cls(factor_converter=factor_converter)
        - rule_cls(factor_converter)
        - rule_cls()
        """
        try:
            return rule_cls(factor_converter=factor_converter)
        except TypeError:
            try:
                return rule_cls(factor_converter)
            except TypeError:
                return rule_cls()