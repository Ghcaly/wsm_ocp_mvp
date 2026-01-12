import logging

from domain.space_size import SpaceSize
from domain.base_rule import BaseRule
from domain.context import Context


class RecalculateNonPalletizedProductsRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def should_execute(self, context: Context, item_predicate=None, mounted_space_predicate=None) -> bool:
        if any(i.amount_remaining for i in context.get_items()):
            return True
        self.logger.debug('Todos os produtos ja foram paletizados. Nao ira executar a regra de recalculo de nao paletizados.')
        return False

    def execute(self, context: Context) -> Context:
        self.logger.debug('Iniciando execucao da regra RecalculateNonPalletizedProductsRule')

        for order in context.orders:
            if sum(i.amount_remaining for i in order.items) == 0:
                self.logger.debug(f'Todos os produtos da ordem {order.delivery_order} ja foram paletizados')
                continue

            pallet_with_less_occupation = None
            mounted = getattr(context, 'mounted_spaces', [])
            if mounted:
                # Simplified: pick first mounted space not exclusive
                pallet_with_less_occupation = mounted[0]

            if not pallet_with_less_occupation:
                self.logger.debug(f'Nao foi possivel encontrar um palete para alocar os itens da ordem {order.delivery_order}')
                continue

            occupation_in_1x1_boxes = 0
            for item in order.items:
                # try to use a factor converter if present
                if hasattr(context, 'factor_converter') and context.factor_converter:
                    factor = item.Product.get_factor(SpaceSize.Size42)

                    if not factor:
                        self.logger.debug(f'Nao existe fator 42 cadastrado para o item {getattr(item, "code", "?")}')
                        continue

                    occupation_in_1x1_boxes += context.factor_converter.occupation(item.amount, factor, item.Product.PalletSetting, item, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))
                else:
                    occupation_in_1x1_boxes += getattr(item, 'amount', 0)

                if occupation_in_1x1_boxes <= (pallet_with_less_occupation.space.size - pallet_with_less_occupation.occupation):
                    if hasattr(context, 'place_non_palletized_on_occupied'):
                        context.place_non_palletized_on_occupied(order, pallet_with_less_occupation.space if hasattr(pallet_with_less_occupation, 'space') else pallet_with_less_occupation)

        return context
