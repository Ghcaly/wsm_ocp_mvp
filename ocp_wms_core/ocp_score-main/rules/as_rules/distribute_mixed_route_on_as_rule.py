from typing import Callable
import logging

from ...domain.base_rule import BaseRule
from ...domain.context import Context


class DistributeMixedRouteOnASRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def should_execute(self, context: Context, item_predicate: Callable = None, mounted_space_predicate: Callable = None) -> bool:
        if context.get_setting('DistributeMixedRouteOnASCalculus', False):
            return True

        self.logger.debug('Configuracao para distribuir rotas mistas no calculo AS nao habilitada. Parando execucao da regra.')
        return False

    def execute(self, context: Context) -> Context:
        self.logger.debug('Executando distribuicao de rotas mistas no calculo AS')

        lower_order = min((o.delivery_order for o in context.orders), default=None)
        if lower_order is None:
            return context

        order = next((o for o in context.orders if o.delivery_order == lower_order), None)
        quantity_spaces_needed_to_delivery02 = sum((o.quantity_of_pallets_needed for o in context.orders))
        quantity_of_spaces = len(context.spaces)

        if quantity_spaces_needed_to_delivery02 >= quantity_of_spaces:
            self.logger.debug('Quantidade de pallets necessarios para a entrega dois eh maior que a quantidade de espaco no caminhao. Parando execucao da regra.')
            return context

        def get_quantity_spaces_needed_to_delivery01(spaces, spaces_needed_delivery02, order):
            return spaces - (spaces_needed_delivery02 - order.quantity_of_pallets_needed)

        quantity_spaces_needed_to_delivery01 = get_quantity_spaces_needed_to_delivery01(quantity_of_spaces, quantity_spaces_needed_to_delivery02, order)
        self.logger.debug('Setando a quantidade pallets necessarios para a entrega 01.')
        order.set_quantity_of_pallets_needed(quantity_spaces_needed_to_delivery01)

        return context
