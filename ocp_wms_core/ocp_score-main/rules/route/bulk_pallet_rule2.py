from domain.base_rule import BaseRule

class BulkPalletRule_old(BaseRule):
    def __init__(self, complex_customer: int = None):
        super().__init__()
        self._complex_customer = complex_customer

    def with_complex_customer(self, complex_customer: int):
        self._complex_customer = complex_customer
        return self

    def execute(self, context):
        # process items that are not chopp/marketplace
        items = []
        if hasattr(context, 'get_items'):
            items = [i for i in context.get_items() if not getattr(i, 'is_chopp', False) and getattr(i, 'amount_remaining', 0) > 0]

        for item in items:
            bays = getattr(context, 'spaces', [])
            for bay in bays:
                self._add_bulk_pallet(context, item, bay)

    def _add_bulk_pallet(self, context, item, bay):
        # simplified: add product if quantity >= factor
        factor_quantity = getattr(item, 'product', {}).get('pallet_quantity', 1) if isinstance(getattr(item, 'product', None), dict) else item.product.PalletSetting.get('quantity', 1) if getattr(item, 'product', None) else 1
        bulk_quantity = factor_quantity if getattr(item, 'amount_remaining', 0) >= factor_quantity else None
        if bulk_quantity is not None:
            if self._complex_customer is None:
                context.add_product(bay, item, bulk_quantity)
            else:
                context.add_complex_load_product(bay, item, bulk_quantity, getattr(bay, 'size', 0), self._complex_customer)
