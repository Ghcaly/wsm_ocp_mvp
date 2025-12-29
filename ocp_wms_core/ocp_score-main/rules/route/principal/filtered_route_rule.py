from ....domain.base_rule import BaseRule
from ....domain.context import Context
from ....factories.route_rule_factories import RouteRuleFactories
from ....domain.itemList import ItemList


class FilteredRouteRule(BaseRule):
    def __init__(self):
        super().__init__(name='FilteredRouteRule')
        # keep parity with C# factory usage; create chain on-demand
        self._route_rules_factory = RouteRuleFactories()

    def execute(self, context: Context):
        # try to get complex load customer (C#: GetComplexLoadCustomer)
        complex_client = context.GetComplexLoadCustomer()

        # create rules chain (C#: CreateRouteRulesChain(context.Settings))
        rules_chain = self._route_rules_factory.create_route_chain()

        new_context = context
        # if there is no complex client (C# uses default == 0), execute chain and change context
        if not complex_client:
            new_context = rules_chain.execute_chain(new_context)
            self._change_context(context, new_context)
            return

        # when complex client exists, apply mounted-space filter: keep mounted spaces
        # without products that have Customer set
        # (faithful call to C# WithMountedSpaceFilter)
        new_context.WithMountedSpaceFilter(lambda ms: not any(getattr(p, 'Customer', None) for p in ms.GetProducts()))

        # execute the chain with the filter applied
        new_context = rules_chain.execute_chain(new_context)

        # clear filters and, if there are items with remaining amount, execute the chain again
        new_context.ClearFilters()
        if ItemList(new_context.GetItems()).WithAmountRemaining().Any():
            new_context = rules_chain.execute_chain(new_context)

        # finally propagate changes back to caller (C# ChangeContext(newContext))
        self._change_context(context, new_context)

    def _change_context(self, original_context: Context, new_context: Context):
        """Apply snapshot/new_context changes into original_context (parity with C# ChangeContext)."""
        original_context.Orders = new_context.Orders
        original_context.Spaces = new_context.Spaces
        original_context.MountedSpaces = new_context.MountedSpaces
