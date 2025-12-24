from ...domain.base_rule import BaseRule
from ...domain.context import Context

class VehicleCapacityOverflowRule(BaseRule):
    def __init__(self):
        super().__init__(name='VehicleCapacityOverflowRule')

    def debug(self, message: str):
        # Simple debug print, can be replaced with proper logging
        print(f"[{self.name}] {message}")

    def execute(self, context: Context, *args, **kwargs) -> Context:
        # Faithful to the C# implementation:
        # if (!context.GetItems().WithAmountRemaining().Any()) { return; }
        if not context.get_items_with_amount_remaining():
            self.debug('Todos os produtos foram montados, parando execucao da regra')
            return context

        # context.SetStatus(ContextStatus.VehicleCapacityOverflow)
        self.debug('O status do contexto foi alterado para VehicleCapacityOverflow')
        context.set_status('VehicleCapacityOverflow')
        return context
