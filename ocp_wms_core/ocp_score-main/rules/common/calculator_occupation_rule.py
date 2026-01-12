from domain.base_rule import BaseRule
from domain.context import Context


class CalculatorOccupationRule(BaseRule):
    def __init__(self, factor_converter=None):
        super().__init__(name='CalculatorOccupationRule')
        self._factor_converter = factor_converter

    def execute(self, context: Context) -> Context:
        # Use provided factor converter or fall back to context/factory
        factor = self._factor_converter or getattr(context, 'factor_converter', None)

        # Mirror the C# loop: foreach order in context.Orders -> foreach item in order.Items
        for order in context.orders:
            for item in order.items:
                # Check product factors for size 42 (SpaceSize.Size42 in C#)
                if not item.product.factors:
                    # faithful to C#: if no factor for size 42, skip with a debug
                    context.add_execution_log(f"Nenhum produto com tamanho 42 order {getattr(order, 'identifier', getattr(order, 'id', ''))}")
                    continue

                # get factor for size 42 like C#'s Product.GetFactor(42)
                factor_obj = item.product.get_factor(42)

                # compute occupation default per unit (C# uses _factorConverter.Occupation)
                occupation_default_per42 = factor.occupation(
                    getattr(item, 'amount_remaining', 0),
                    factor_obj,
                    item,
                    context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)
                )

                # call the domain method to set the calculated value (faithful to C#)
                item.SetOcpDefaultPerUni42(occupation_default_per42)
                # context.add_execution_log('Calculado com sucesso')

        return context
