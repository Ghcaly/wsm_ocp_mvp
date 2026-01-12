from domain.base_rule import BaseRule
from domain.context import Context

class RecalculatePalletOccupationRule(BaseRule):
    def __init__(self, factor_converter=None):
        super().__init__(name='RecalculatePalletOccupationRule')
        self._factor_converter = factor_converter

    def execute(self, context: Context) -> Context:
        factor = self._factor_converter or getattr(context, 'factor_converter', None) 

        for ms in getattr(context, 'mounted_spaces', []) or []:
            # skip bulk if attribute present
            if getattr(ms, 'is_bulk', False):
                continue

            setattr(ms, 'occupation', 0)
            context.add_execution_log('Setando ocupacao do palete para zero')

            for container in getattr(ms, 'containers', []) or []:
                # treat as pallet-like container if has products
                for mounted_product in getattr(container, 'products', []) or []:
                    space_size = getattr(ms.space, 'size', None)
                    try:
                        total_occupation = factor.occupation(mounted_product.amount, space_size, getattr(mounted_product, 'item', None), context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))
                    except Exception:
                        total_occupation = 0

                    product_occupation = total_occupation - getattr(getattr(mounted_product, 'item', None), 'additional_occupation', 0)
                    setattr(mounted_product, 'occupation', product_occupation)
                    # increase mounted space occupation
                    ms.occupation = getattr(ms, 'occupation', 0) + total_occupation

        return context
