from collections import defaultdict
from typing import List, Iterable

from domain.itemList import ItemList
from domain.mounted_space_list import MountedSpaceList
from domain.mounted_product import MountedProduct
from domain.mounted_space import MountedSpace
from domain.container import Container
from domain.base_rule import BaseRule
from domain.context import Context


class DetachedUnitRule(BaseRule):
    def __init__(self, factor_converter=None):
        super().__init__(name='DetachedUnitRule')
        self._factor_converter = factor_converter
        self._detached_items = []
        self._mounted_space_selected = None
    
    def should_execute(self, context: Context) -> bool:
        if not context.get_setting('PalletizeDetached', False):
            context.add_execution_log('Regra desativada, nao sera executada.')
            return False

        # collect detached items (faithful to C#: check DetachedAmount > 0)
        self._detached_items = ItemList(context.GetItems()).WithDetachedAmount()

        if not self._detached_items:
            context.add_execution_log('Nenhum item com quantidade avulsa encontrado. Regra nao sera executada.')
            return False

        return True

    def execute(self, context: Context) -> Context:

        mounted_spaces = MountedSpaceList(context.MountedSpaces).NotFull()

        all_pallets_full = not bool(mounted_spaces)
        has_empty_space = bool(context.Spaces)

        if all_pallets_full and not has_empty_space:
            self._not_palletize(context)
        else:
            self._realocate(context, mounted_spaces)

        return context

    def _not_palletize(self, context: Context):
        context.add_execution_log('Todos os espacos estao completos. Os itens avulsos nao serao paletizados.')
        for item in self._detached_items:
            item.SetRealocated(False)
            item.Product.SetUnPalletized()

    def _realocate(self, context: Context, mounted_spaces: Iterable):
        # Get sorted items by total detached amount (grouped by code, ordered desc)
        ordered_items = self._get_sorted_items_by_total_detached_amount()

        # distinct codes
        detached_codes = {i.Code for i in ordered_items}

        # choose a mounted space that doesn't have the same item codes and has some occupation (>0)
        candidates = [ms for ms in mounted_spaces if self._ignore_spaces_with_items_code(ms, detached_codes)]
        candidates = MountedSpaceList(candidates).OrderByOccupation().ToList()
        self._mounted_space_selected = None
        for ms in candidates:
            if ms.Occupation > 0:
                self._mounted_space_selected = ms
                break

        for detached_item in ordered_items:
            item = detached_item

            orders_number = item.DeliveryOrdersWithDetachedAmount()
            
            # C#: Realocate(context, item, ordersNumber) - intermediate method with logging
            for order_number in orders_number:
                context.add_execution_log(f"Tentando realocar item: {item.Code}/{item.Product.Name} com quantidade avulsa: {item.DetachedAmount} da Ordem de entrega: {order_number}.")
                
                # C#: Check if unit amount is greater than container
                is_unit_amount_greater_than_container = item.DetachedAmount > item.Factor
                if is_unit_amount_greater_than_container:
                    context.add_execution_log(f"[WARNING] Quantidade avulsa: {item.DetachedAmount} do item: {item.Product.Name} maior que a quantidade da caixa: {item.Factor}.")
                
                self._realocate_item_order(context, item, order_number)

    def _realocate_item_order(self, context: Context, item, order_number: int):
        # find order that contains the item
        order = next((o for o in context.Orders if item in getattr(o, 'Items', [])), None)

        if not self._has_available_mounted_space():
            space = next(iter(context.Spaces), None)
            if space is None:
                context.add_execution_log(f'Nenhum espaco disponivel. Item: {item.Code}/{item.Product.Name} nao realocado')
                # faithful: mark not realocated and call not palletize
                item.SetRealocated(False)
                item.Product.SetUnPalletized()
                return

            # C#: SetNewMontedSpace - create new mounted space with pallet
            self._set_new_mounted_space(context, order, space)

        detached_amount = item.DetachedAmount
        pallet_setting = item.Product.PalletSetting
        old_pallet_occupation = self._mounted_space_selected.Occupation
        unit_detached_amount = detached_amount / item.Factor
        factor = item.Product.GetFactor(self._mounted_space_selected.Space.Size)
        occupation_calculated = self._factor_converter.Occupation(unit_detached_amount, factor, item, context.get_setting('OccupationAdjustmentToPreventExcessHeight'))
        first_layer_index = item.Product.GetQuantityOfLayerToSpace(self._mounted_space_selected.Space.Size, int(round(occupation_calculated, 1)))
        if item.Amount > 0:
            occupation_calculated /= item.AmountPerContainer

        item.SetRealocated(True)

        mounted_product = MountedProduct.Build(item.Product, order, first_layer_index, self._mounted_space_selected.GetNextLayer())
        product_amount = occupation_calculated - item.AdditionalOccupation
        mounted_product.SetOccupation(product_amount)
        mounted_product.SetRealocated(True)

        self._mounted_space_selected.GetFirstPallet().AddMountedProduct(mounted_product, detached_amount)
        self._mounted_space_selected.IncreaseOccupation(occupation_calculated)

        # C#: WriteLogDebug with Side (ITruckBayRoute cast)
        side = getattr(self._mounted_space_selected.Space, 'Side', '?')
        context.add_execution_log(
            f"Realocando item: {item.Code}/{item.Product.Name} na baia: {self._mounted_space_selected.Space.Number} / {side}, "
            f"com quantidade avulsa: {detached_amount}, "
            f"com ocupacao calculada de: {occupation_calculated} "
            f"e nova ocupacao de: {old_pallet_occupation:.2f} para: {self._mounted_space_selected.Occupation:.2f}."
        )

        item.SubtractDeliveryOrderAmountDetached(order_number, detached_amount)
    
    def _set_new_mounted_space(self, context: Context, order, space):
        """
        C#: SetNewMontedSpace - Create new mounted space with pallet.
        Faithful port including Pallet.Build() and AddContainer.
        """
        # C#: MountedBay.Build(space, order)
        new_mounted_space = MountedSpace(space=space, order=order)
        context.AddMountedSpace(new_mounted_space)
        
        # C#: Pallet.Build() -> Python: Container()
        pallet = Container()
        new_mounted_space.AddContainer(pallet)
        
        side = getattr(space, 'Side', '?')
        context.add_execution_log(
            f"Nenhum espaço montado disponível. Criando novo espaço: {space.Number}/{side}"
        )
        
        self._mounted_space_selected = new_mounted_space

    def _has_available_mounted_space(self) -> bool:
        return self._mounted_space_selected is not None

    def _get_sorted_items_by_total_detached_amount(self):
        """
        C#: GetSortedItemsByTotalDetachedAmount
        Faithful port: OrderByDescending(x => x.DetachedAmount).GroupBy(x => x.Code)
                      .Select(g => new { Code, TotalQuantity = Sum, Items })
                      .OrderByDescending(g => g.TotalQuantity)
                      .SelectMany(g => g.Items)
        """
        # First order by DetachedAmount descending (before grouping)
        ordered = sorted(self._detached_items, key=lambda x: x.DetachedAmount, reverse=True)
        
        # Group by Code
        groups = defaultdict(lambda: {'total': 0, 'items': []})
        for it in ordered:
            groups[it.Code]['total'] += it.DetachedAmount
            groups[it.Code]['items'].append(it)
        
        # Order groups by TotalQuantity descending
        grouped = sorted(groups.items(), key=lambda kv: kv[1]['total'], reverse=True)
        
        # SelectMany - flatten preserving order
        result = []
        for _, g in grouped:
            result.extend(g['items'])
        
        return result

    def _ignore_spaces_with_items_code(self, mounted_space, detached_item_codes: Iterable):
        return not any(y.Code in detached_item_codes for y in mounted_space.GetItems())
