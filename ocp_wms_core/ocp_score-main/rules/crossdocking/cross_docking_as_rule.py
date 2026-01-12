import logging
from domain.context import Context
from .cross_base_rule import CrossBaseRule

class CrossDockingASRule(CrossBaseRule):
    def __init__(self):
        super().__init__()

    def execute(self, context: Context) -> Context:
        # Faithful port of C#:
        # var maps = context.GetAllItems().Select(x => x.MapNumber).Distinct();
        maps = set(x.MapNumber for x in context.GetAllItems())

        new_context = context

        for m in maps:
            new_context = self.execute_as_rules(new_context, m)

        # propagate changes back to original context (C# ChangeContext(newContext))
        self._change_context(context, new_context)
        return context

    def _change_context(self, original_context: Context, new_context: Context):
        """Apply snapshot/new_context changes into original_context (parity with C# ChangeContext)."""
        original_context.Orders = new_context.Orders
        original_context.Spaces = new_context.Spaces
        original_context.MountedSpaces = new_context.MountedSpaces

