import logging
from domain.base_rule import BaseRule
from domain.context import Context


class ReallocateNonPalletizedItemsOnSmallerPalletRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def should_execute(self, context: Context, item_predicate=None, mounted_space_predicate=None) -> bool:
        if any(getattr(i, 'amount_remaining', 0) > 0 for i in context.get_items()):
            return True
        self.logger.debug('Nao ha nenhum item com quantidade pendente para paletizar')
        return False

    def execute(self, context: Context) -> Context:
        self.logger.debug('Iniciando execucao da regra ReallocateNonPalletizedItemsOnSmallerPalletRule')

        for order in [o for o in context.orders if any(i.amount_remaining for i in o.items)]:
            not_full_space = None
            # Attempt to find a not full space via context helper if available
            if hasattr(context, 'get_not_full_spaces'):
                ordered = context.get_not_full_spaces()
                not_full_space = ordered[0] if ordered else None

            if not not_full_space:
                self.logger.debug('Nao ha paletes nao cheios disponiveis')
                break

            self.logger.debug(f'Tentativa de adicionar items da ordem {order.delivery_order} no palete {getattr(not_full_space, "number", "?")}/{getattr(not_full_space, "side", "?")}')
            # Use a helper on context to place non-palletized items if exists
            if hasattr(context, 'place_non_palletized_on_occupied'):
                context.place_non_palletized_on_occupied(order, not_full_space)

        return context
