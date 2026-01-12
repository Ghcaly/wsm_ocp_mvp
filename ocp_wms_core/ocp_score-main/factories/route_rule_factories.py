from rules.route import *

from domain.rule_chain import RuleChain
from domain.factor_converter import FactorConverter

class RouteRuleFactories:
    def __init__(self) -> None:
        self.factor_converter = FactorConverter()

    def create_route_chain(self, name: str = "route") -> RuleChain:
        chain = RuleChain(name=name)
        # provide a real FactorConverter instance to rules that accept it; helper will fall back when not supported
        fc = self.factor_converter
        chain.add_rule(self._make_rule(BulkPalletRule, fc))
        chain.add_rule(self._make_rule(ChoppPalletizationRule, fc))
        chain.add_rule(self._make_rule(BulkPalletAdditionalOccupationRule, fc))
        chain.add_rule(self._make_rule(LayerRule, fc))
        chain.add_rule(self._make_rule(PalletGroupSubGroupRule, fc))
        chain.add_rule(self._make_rule(NonPalletizedProductsRule, fc))
        chain.add_rule(self._make_rule(SnapshotRule, fc))
        chain.add_rule(self._make_rule(NonLayerOnLayerPalletRule, fc))
        chain.add_rule(self._make_rule(ReturnableAndDisposableSplitRule, fc))
        chain.add_rule(self._make_rule(ReturnableAndDisposableSplitRemountRule, fc))
        chain.add_rule(self._make_rule(RemountRule, fc))
        chain.add_rule(self._make_rule(IsotonicWaterRule, fc))
        chain.add_rule(self._make_rule(IsotonicWaterWithoutMinimumOccupationRule, fc))
        chain.add_rule(self._make_rule(RemountSplittedRebuildPalletRule, fc))
        chain.add_rule(self._make_rule(EmptySpaceRule, fc))
        chain.add_rule(self._make_rule(BuildMountedSpacesWithFewDisposableProductsRule, fc))
        chain.add_rule(self._make_rule(PackageRule, fc))
        chain.add_rule(self._make_rule(BoxTemplateRule, fc))
        chain.add_rule(self._make_rule(RecalculatePalletOccupationRule, fc))
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