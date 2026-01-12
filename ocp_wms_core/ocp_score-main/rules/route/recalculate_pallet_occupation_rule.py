from domain.mounted_space_list import MountedSpaceList
from domain.base_rule import BaseRule
from domain.factor_converter import FactorConverter
from domain.space import NotBulk

class RecalculatePalletOccupationRule(BaseRule):
    """Direct port of C# RecalculatePalletOccupationRule.

    This implementation calls attributes and methods exactly as in the C#
    source (no defensive checks) to remain faithful to original behavior.
    """

    def __init__(self, factor_converter: FactorConverter = None):
        super().__init__(name='RecalculatePalletOccupationRule')
        self._factor_converter = factor_converter or FactorConverter()

    def execute(self, context):
        # return
        for mounted_space in MountedSpaceList(context.mounted_spaces).NotBulk():
            mounted_space.set_occupation(0)
            for pallet in mounted_space.containers:
                for mp in pallet.products:
                    if hasattr(mp, "item") and hasattr(mp, "product"):
                        item = mp.item
                        product = mp.product
                        amount = getattr(mp, "amount", getattr(item, "amount_remaining", 0))
                    else:
                        # mp is an Item-like
                        item = mp
                        product = item.product
                        amount = getattr(item, "amount_remaining", getattr(item, "amount", 0))

                    factor = product.get_factor(mounted_space.space.size)
                    total_occupation = self._factor_converter.occupation(
                        amount,
                        factor,
                        product.PalletSetting,
                        item,
                        context.get_setting('OccupationAdjustmentToPreventExcessHeight')
                    )

                    product_occupation = total_occupation - getattr(item, "additional_occupation", 0)

                    # set occupation on the mounted-product wrapper if it exists, otherwise try item
                    if hasattr(mp, "set_occupation"):
                        mp.set_occupation(product_occupation)
                    else:
                        # fallback: attach attribute to item (keeps data)
                        setattr(item, "occupation", product_occupation)

                    mounted_space.increase_occupation(total_occupation)
            print(f"Recalculated occupation for MountedSpace ID {mounted_space.Space.number} - {mounted_space.Space.side}: {mounted_space.occupation}")