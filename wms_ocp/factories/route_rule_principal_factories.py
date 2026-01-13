from ..rules.route.principal import *

from ..domain.rule_chain import RuleChain
from ..domain.factor_converter import FactorConverter

class RouteRulePrincipalFactories:
    def __init__(self) -> None:
        self.factor_converter = FactorConverter()

    def create_principal_route_chain(self, name: str = "principal_route") -> RuleChain:
        chain = RuleChain(name=name)
        fc = self.factor_converter
        chain.add_rule(self._make_rule(ComplexGroupLoadRule, fc))
        chain.add_rule(self._make_rule(FilteredRouteRule, fc))
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