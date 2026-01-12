from typing import Any
import logging

from domain.base_rule import BaseRule
from domain.context import Context
from factories.as_rule_factories import AsRuleFactories

class CrossBaseRule(BaseRule):
    """Base helper for cross-docking rules. Provides ExecuteAsRules helper that
    invokes AS rules chain for a given order filter and clears filters afterwards.
    """
    def __init__(self):
        super().__init__(name='CrossBaseRule')
        # Keep a factory instance (mirrors dependency in C#)
        self._as_rules_factory = AsRuleFactories()
        self.logger = logging.getLogger(__name__)

    def execute_as_rules(self, context: Context, order_filter: Any) -> Context:
        # create AS rules chain from factory (faithful to C# CreateRulesChain(context.Settings))
        as_chain = self._as_rules_factory.create_as_chain()

        # Apply filter using the same shape as C# lambda: y.Items.All(z => z.MapNumber == orderFilter || z.LicensePlate == orderFilter)
        # Note: intentionally call attributes/methods directly (no defensive checks) to remain faithful.
        context.with_order_filter(lambda y: all(z.MapNumber == order_filter or z.LicensePlate == order_filter for z in y.Items))

        new_context = as_chain.execute_chain(context)

        new_context.clear_filters()

        return new_context
