from ...domain.mounted_product_list import MountedProductList
from ...domain.itemList import ItemList
from ...domain.base_rule import BaseRule
from ...domain.context import Context
from typing import Iterable


class NewReorderRule(BaseRule):
    """Faithful port of the C# NewReorderRule.

    This implementation closely follows the C# execution sequence and calls
    domain/container helper methods directly as the original does (no
    defensive existence checks). It's organized into small helpers to mirror
    the C# private methods and remains idiomatic Python where straightforward.
    """

    def __init__(self):
        super().__init__(name='NewReorderRule')
        # flags populated per execution pass
        self._include_top_of_pallet = False
        self._order_pallet_by_product_group = False
        self._order_pallet_by_group_subgroup_and_packaging_item = False
        
    def should_execute(self, context: Context) -> bool:
        # Mirror the C# checks: require three settings to be True
        order_pkg = context.get_setting('OrderPalletByPackageCodeOccupation', False)
        order_cancha = context.get_setting('OrderPalletByCancha', False)
        isotonic = context.get_setting('IsotonicTopPalletCustomOrderRule', False)

        if not order_pkg or not order_cancha or not isotonic:
            context.add_execution_log('Regra desativada, nao sera executada')
            return False

        return True

    def execute(self, context: Context) -> Context:

        # Reset assembly sequence for all mounted products (match C# first step)
        # for p in context.get_all_products():
        #     p.set_assembly_sequence(0)
        for mounted_space in context.MountedSpaces:
            for container in mounted_space.GetContainers():
                for product in container.GetProducts():
                    product.SetAssemblySequence(0)

        # Two passes: layer-validated then non-layer (C# does two passes)
        self._reorder_pallets(context, validate_layer=True)
        self._reorder_pallets(context, validate_layer=False)

        context.add_execution_log('Finalizado execucao da regra')
        return context

    # ---------------- main flow helpers ---------------------------------
    def _reorder_pallets(self, context: Context, validate_layer: bool = False):
        # populate flags from context settings (C# stores them in fields)
        self._include_top_of_pallet = context.get_setting('IncludeTopOfPallet', False)
        self._order_pallet_by_product_group = context.get_setting('OrderPalletByProductGroup', False)
        self._order_pallet_by_group_subgroup_and_packaging_item = context.get_setting('OrderPalletByGroupSubGroupAndPackagingItem', False)

        for mounted_space in context.mounted_spaces:

            context.add_execution_log(f"Reordenando produtos do espaco {mounted_space.space.number} / {mounted_space.space.sideDesc}")

            for container in mounted_space.containers:
                # container.get_products() expected to return an iterable of mounted products
                products = MountedProductList(container.get_products())#.OrderByOrderNumber()
                
                # C# applies layer validation by using helper filters; we call them directly
                if validate_layer:
                    products = MountedProductList(products).OnlyLayer()
                else:
                    products = MountedProductList(products).NotLayer()

                # If nothing remains, continue
                if not products:
                    continue

                # Apply the canonical sequence for ordering by cancha
                self._order_pallet_by_cancha(validate_layer, container, products)

    def _order_pallet_by_cancha(self, validate_layer: bool, container, products: Iterable):
        # Order base products -> core products -> top-of-pallet sequence
        self._order_base_products(container, products)
        self._order_core_products(validate_layer, container, products)
        self._order_top_pallet(container, products)

    def _order_core_products(self, validate_layer: bool, container, products: Iterable):
        # Core products exclude base pallet items
        core = MountedProductList(products).NotBasePallet()
        self._order_pallet(validate_layer, container, core)

    def _order_top_pallet(self, container, products: Iterable):
        same_cancha = MountedProductList(products).NotBasePallet()
        self._top_of_pallet(container, same_cancha)

    def _order_pallet(self, validate_layer: bool, container, products: Iterable):
        self._order_layer_products(validate_layer, container, products)
        self._order_chopp(container, products)
        self._order_returnable(container, products)
        self._order_disposable(container, products)

    # ---------------- specific ordering stages ---------------------------
    def _order_layer_products(self, validate_layer: bool, container, products: Iterable):
        if not validate_layer:
            return

        # context.add_execution_log(f"Reordenando {len(products)} produtos layer")

        # original C# selects the first item then possibly moves the one with bigger ballast
        first_layer = MountedProductList(products).First()
        bigger_ballast = MountedProductList(products).WithoutAssemblySequence().Matching(lambda p: (p.Amount / p.Product.PalletSetting.QuantityBallast) != (first_layer.Amount / first_layer.Product.PalletSetting.QuantityBallast))
        if bigger_ballast:
            layer_product = MountedProductList(products).WithoutAssemblySequence().OrderByDescIsReturnableAndLayers().First()
            container.increase_assembly_sequence(layer_product)

    def _order_chopp(self, container, products: Iterable):
        chopps = MountedProductList(products).NotMarketplace().IsChopp().NotTopOfPallet().NotIsotonicWater().NotBasePallet()
        # context.add_execution_log(f"Reordenando {len(chopps)} produtos chopp")
        if not chopps:
            return
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, chopps)
            return
        self._order_products(container, chopps)

    def _order_base_products(self, container, products: Iterable):
        """Order base pallet products (port of C# OrderBaseProducts)."""
        base_pallet = MountedProductList(products).IsBasePallet().NotIsotonicWater().NotTopOfPallet()
        if (not base_pallet.Any()):
            return
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, base_pallet)
            return
        self._order_products(container, base_pallet)

    def _order_returnable(self, container, products: Iterable):
        returnables = MountedProductList(products).NotMarketplace().IsReturnable().NotTopOfPallet().NotChopp().NotIsotonicWater().NotBasePallet()
        # context.add_execution_log(f"Reordenando {len(returnables)} produtos retornaveis")
        if not returnables:
            return
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, returnables)
            return
        if self._order_pallet_by_product_group:
            self._order_by_product_group(returnables, container)
            return
        self._order_products(container, returnables)

    def _order_disposable(self, container, products: Iterable):
        disposables = MountedProductList(products).NotMarketplace().NotReturnable().NotTopOfPallet().NotChopp().NotIsotonicWater().NotBasePallet()
        # context.add_execution_log(f"Reordenando {len(disposables)} produtos descartaveis")
        if not disposables:
            return
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, disposables)
            return
        if self._order_pallet_by_product_group:
            self._order_by_product_group(disposables.WithoutAssemblySequence(), container)
            return
        self._order_products(container, disposables)

    def _order_marketplace(self, container, products):
        """C#: OrderMarketplace - order marketplace products"""
        self._order_package(container, products)
        self._order_template_box(container, products)

    def _order_package(self, container, products):
        """C#: OrderPackage - order Package marketplace products"""
        package = products.IsPackage()
        self._order_products(container, package)

    def _order_template_box(self, container, products):
        """C#: OrderTemplateBox - order BoxTemplate marketplace products"""
        box_template = products.IsBoxTemplate()
        self._order_products(container, box_template)

    def _order_isotonic_water(self, container, products: Iterable):
        isotonic = MountedProductList(products).NotMarketplace().IsIsotonicWater().NotTopOfPallet().NotChopp().NotBasePallet()
        # context.add_execution_log(f"Reordenando {len(isotonic)} produtos de agua isotonico")
        if not isotonic:
            return
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, isotonic)
            return
        if self._order_pallet_by_product_group:
            self._order_by_product_group(isotonic, container)
            return
        self._order_products(container, isotonic)

    def _top_of_pallet(self, container, products: Iterable):
        self._order_isotonic_water(container, products)
        self._top_of_pallet_final(container, products)
        self._order_marketplace(container, products)

    def _top_of_pallet_final(self, container, products: Iterable): 
        top = MountedProductList(products).IsTopOfPallet().NotChopp().NotBasePallet().NotMarketplace()
        # context.add_execution_log(f"Reordenando {len(top)} produtos topo do pallet")
        if not top:
            return
        if self._include_top_of_pallet:
            top = MountedProductList(products).IsTopOfPallet().NotChopp()
        if self._order_pallet_by_group_subgroup_and_packaging_item:
            self._order_by_group_subgroup_and_packaging(container, top)
            return
        self._order_products(container, top)

    # ---------------- ordering utilities ---------------------------------
    def _order_products(self, container, products: Iterable):
        # container.increase_assembly_sequence is used to tag a mounted product
        for product in MountedProductList(products).WithAmount().OrderByPackageOccupationDescThenByAmountDesc():
            container.increase_assembly_sequence(product)

    def _order_by_product_group(self, products: Iterable, container):
        # Group by packing group code and order by aggregated amount descending (Python)
        from collections import defaultdict
        groups = defaultdict(int)
        for p in list(products):
            gc = p.Product.PackingGroup.GroupCode
            groups[gc] += int(p.Amount)

        ordered = sorted(groups.items(), key=lambda kv: kv[1], reverse=True)
        for group_code, _ in ordered:
            products_in_package_type = MountedProductList(products).WithoutAssemblySequence().matching(lambda x: x.Product.PackingGroup.GroupCode == group_code)
            for product in products_in_package_type.WithAmount().OrderByAmountDesc():
                self._distribute_item(product, products_in_package_type, container)

    def _distribute_item(self, item, item_list, container):
        # Find similar items by packing group and packing code (C# SimilarItems)
        all_items = list(item_list)
        similar_item_list = [p for p in all_items if p.Product.PackingGroup.GroupCode == item.Product.PackingGroup.GroupCode and p.Product.PackingGroup.PackingCode == item.Product.PackingGroup.PackingCode]

        for mp in MountedProductList(similar_item_list).WithoutAssemblySequence().WithAmount().to_list():
            self._order_similar_items(container, similar_item_list, mp.Product)

    def _order_similar_items(self, container, similar_item_list, product):
        item_type_list = MountedProductList(similar_item_list).matching(lambda p: p.Product.PackingGroup.GroupCode == product.PackingGroup.GroupCode and
                                                 p.Product.PackingGroup.PackingCode == product.PackingGroup.PackingCode and
                                                 p.Product.PackingGroup.TypeCode == product.PackingGroup.TypeCode)
        item_type_list = item_type_list.WithoutAssemblySequence().OrderByAmountDesc()
        self._order_products(container, item_type_list)

    def _order_by_group_subgroup_and_packaging(self, container, products):
        same_groups = self._get_same_group_products_sorted_by_occupation(products)
        for same_group in same_groups:
            grouped = self._get_grouped_products_by_subgroup_sorted_by_occupation(same_group)
            for subgroup in grouped:
                self._order_products(container, subgroup)

    # ---------------- grouping helpers (C# LINQ ports) -----------------
    @staticmethod
    def _get_same_group_products_sorted_by_occupation(products: Iterable):
        """Group products by PackingGroup.GroupCode and order groups by total percent occupation desc."""
        from collections import defaultdict
        groups = defaultdict(list)
        for p in list(products):
            key = p.Product.PackingGroup.GroupCode
            groups[key].append(p)

        def sum_percent(lst):
            return sum(float(getattr(m, 'PercentOccupationIntoDefaultPalletSize', 0) or 0) for m in lst)

        ordered = sorted(groups.values(), key=lambda g: sum_percent(g), reverse=True)
        return ordered

    @staticmethod
    def _get_grouped_products_by_subgroup_sorted_by_occupation(products: Iterable):
        """Group a list of mounted products by PackingGroup.SubGroupCode and order subgroups by total percent occupation desc."""
        from collections import defaultdict
        groups = defaultdict(list)
        for p in list(products):
            key = p.Product.PackingGroup.SubGroupCode
            groups[key].append(p)

        def sum_percent(lst):
            return sum(float(getattr(m, 'PercentOccupationIntoDefaultPalletSize', 0) or 0) for m in lst)

        ordered = sorted(groups.values(), key=lambda g: sum_percent(g), reverse=True)
        return ordered
