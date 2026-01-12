"""CalculatorPalletizingService - lightweight orchestrator for palletizing rules.

This class provides a clean, DI-friendly surface that the `PalletizingProcessor`
can use. It does not move or modify existing rule implementations; instead it
uses `service.factories` and `service.rules_registry` to instantiate chains.

The implementation keeps constructor injection points for a factor_converter
and a custom rules_registry if you want to override them in tests.
"""
from typing import Optional
import logging

from domain.rule_chain  import RuleChain
from domain.factories import RuleFactories
from factories.route_rule_principal_factories import RouteRulePrincipalFactories
# from . import rules_registry

logger = logging.getLogger(__name__)


class CalculatorPalletizingService:
    """Orchestrates creation and execution of the rule chains.

    Constructor args:
        factor_converter: optional object used by AS rules; stored and injected
                          by callers that create rule instances from registry.
        rules_registry: optional registry to use instead of the default.
    """

    def __init__(self, factor_converter: Optional[object] = None, registry=None, logger: Optional[logging.Logger] = None):
        self.factor_converter = factor_converter
        self.factories = RuleFactories()
        self.registry = registry #or rules_registry
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.route_chain = self.factories.create_route_chain()
        self.principal_route_chain = RouteRulePrincipalFactories().create_principal_route_chain()
        self.as_chain = self.factories.create_as_chain()
        self.mixed_chain = self.factories.create_mixed_chain()
        self.crossdocking_chain = self.factories.create_crossdocking_chain()
        self.t4_chain = self.factories.create_t4_chain()
        self.common_chain = self.factories.create_common_chain()

    def execute_chain(self, chain: RuleChain, context):
        """Convenience runner for a chain."""
        self.logger.debug(f"Executing chain '{chain.name}'")
        return chain.execute_chain(context)

__all__ = ['CalculatorPalletizingService']
