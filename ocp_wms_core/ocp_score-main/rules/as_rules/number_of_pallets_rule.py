from typing import List
from decimal import Decimal
import math

from domain.itemList import ItemList
from domain.order_list import OrderList

from domain.space_size import SpaceSize
from domain.base_rule import BaseRule


# Conservative constant (same as C# CalculatorConstants.BOXES_QUANTITY_IN_PALLET)
BOXES_QUANTITY_IN_PALLET = 42


class NumberOfPalletsRule(BaseRule):
    def __init__(self, factor_converter):
        self._factor_converter = factor_converter

    def execute(self, context) -> None:
        # Apply ordering strategy
        if context.get_setting("OrderProductsForAutoServiceMap"):
            self._order_products_for_auto_service_map(context)
        elif context.Kind == 'CrossDocking':
            self._order_orders_by_license_plate(context)
        elif context.Kind == 'Mixed':
            self._order_orders_by_order_number(context)
        else:
            self._order_orders_by_order_number_descending(context)

        # Group items by SupportPoint and calculate pallets per support point
        items = context.GetItems()
        groups = {}
        for item in items:
            sp = item.Product.SupportPoint
            groups.setdefault(sp, []).append(item)

        for support_point in groups.keys():
            orders = self._get_orders_from_same_support_point(support_point, context.Orders)
            self._calculate_map_pallet_quantity(context, orders)

    def _calculate_map_pallet_quantity(self, context, orders: List[object]) -> None:
        for order in orders:
            occupation_in_1x1_box = Decimal('0')
            for item in self._get_items_from_order(context, order):
                # faithful to C# logging call — rely on logger implemented on context if present
                print(f"Buscando o fator do item {item.Product.Code} do mapa {order.MapNumber}")

                factor = item.Product.GetFactor(SpaceSize.Size42)

                occ = self._factor_converter.Occupation(item.Amount, factor, item.Product.PalletSetting, item, context.get_setting("OccupationAdjustmentToPreventExcessHeight"))
                occupation_in_1x1_box += Decimal(str(occ))

            pallets_needed_for_delivery = occupation_in_1x1_box / Decimal(BOXES_QUANTITY_IN_PALLET)

            if context.get_setting("DistributeMixedRouteOnASCalculus"):
                rounded = int(math.ceil(float(pallets_needed_for_delivery)))
                context.SetQuantityOfPalletsNeededOnOrder(order, Decimal(rounded))
            else:
                context.SetQuantityOfPalletsNeededOnOrder(order, pallets_needed_for_delivery)

    @staticmethod
    def _get_items_from_order(context, order):
        return [i for i in context.GetItems() if i in order.Items]

    def _get_orders_from_same_support_point(self, support_point: str, orders: List) -> List:
        return [order for order in orders if any(d.Product.SupportPoint == support_point for d in order.Items)]

    # --- Ordering helpers (mirror C# flow) ---
    @staticmethod
    def _get_filters(context):
        return context.GetOrderFilter(), context.GetOnlyOrder(), context.GetOnlySpace()

    @staticmethod
    def _apply_filters(context, order_filter, only_order, only_space):
        context.WithOnlyOrder(only_order)
        context.WithOnlySpace(only_space)
        context.WithOrderFilter(order_filter)

    def _order_orders_by_license_plate(self, context):
        order_filter, only_order, only_space = self._get_filters(context)
        context.ClearFilters()
        context.ClearOrderFilters()
        context.SetOrders(OrderList(context.Orders).OrderedByLicensePlate())
        self._apply_filters(context, order_filter, only_order, only_space)

    def _order_orders_by_order_number(self, context):
        order_filter, only_order, only_space = self._get_filters(context)
        context.ClearFilters()
        context.ClearOrderFilters()
        context.SetOrders(OrderList(context.Orders).OrderedByNumber())
        self._apply_filters(context, order_filter, only_order, only_space)

    def _order_orders_by_order_number_descending(self, context):
        order_filter, only_order, only_space = self._get_filters(context)
        context.ClearFilters()
        context.ClearOrderFilters()
        context.SetOrders(OrderList(context.Orders).OrderedByNumberDescending())
        self._apply_filters(context, order_filter, only_order, only_space)

    def _order_products_for_auto_service_map(self, context):
        order_filter, only_order, only_space = self._get_filters(context)
        context.SetOrders(OrderList(context.Orders).OrderedByNumber())
        for order in context.Orders:
            order.SetItems(ItemList(order.Items).OrderedByReturnablesAndGroupSubGroup())
        self._apply_filters(context, order_filter, only_order, only_space)

