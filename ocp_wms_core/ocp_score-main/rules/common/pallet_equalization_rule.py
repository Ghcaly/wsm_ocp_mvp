from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass
from typing import List, Any

from ...domain.mounted_space_list import MountedSpaceList
from ...domain.space_list import SpaceList


# ================= DTO =================

@dataclass
class PalletEqualizeDto:
    MoveOccupation: Decimal
    StayOccupation: Decimal
    SourceSpace: Any
    ProductsToMove: List[Any]
    IsEqualized: bool = False


# ================= RULE =================

class PalletEqualizationRule:

    def __init__(self, factor_converter=None):
        self._factor_converter = factor_converter

    # ---------- SHOULD EXECUTE ----------

    def should_execute(self, context) -> bool:
        if not context.get_setting('PalletEqualizationRule'):
            context.add_execution_log("Regra desativada, não será executada")
            return False

        if not context.MountedSpaces:
            context.add_execution_log("Nenhuma baia montada, a regra não será executada")
            return False

        if not context.Spaces:
            context.add_execution_log("Nenhum palete vazio encontrado, a regra não será executada")
            return False

        min_division = context.get_setting('PercentOccupationMinByDivision')

        exists = any(
            ms.OccupiedPercentage >= min_division and len(ms.GetProducts()) > 1
            for ms in MountedSpaceList(context.MountedSpaces)
                .NotBulk()
                .NotContainProductComplex()
        )

        if not exists:
            context.add_execution_log(
                "Nenhum palete atende o percentual de ocupação minimo, a regra não será executada"
            )
            return False

        return True

    # ---------- EXECUTE ----------

    def execute(self, context):
        context.add_execution_log("Iniciando execução da regra")

        pallets_to_equalize: List[PalletEqualizeDto] = []
        min_percent = context.get_setting('PercentOccupationMinBySelectionPalletDisassembly')

        self.SelectPalletsToEqualizeWithMultipleGroups(context, pallets_to_equalize, min_percent)
        self.SelectPalletsToEqualizeWithMultiplePackages(context, pallets_to_equalize, min_percent)
        self.SelectPalletsToEqualizeWithMultipleItems(context, pallets_to_equalize, min_percent)

        if not pallets_to_equalize:
            context.add_execution_log(
                "Nenhum palete atende a configuração de ocupação minima na divisão dos paletes"
            )
            return

        self.EqualizePallets(context, pallets_to_equalize)

        context.add_execution_log("Finalizado a execução da regra.")

    # ---------- EQUALIZATION ----------

    def EqualizePallets(self, context, pallets: List[PalletEqualizeDto]):
        empty_spaces = SpaceList(context.Spaces).OrderedBySizeAndNumber()
        pallets = self.OrderPalletsByOptimalOccupation(pallets)

        context.add_execution_log(
            "Paletes selecionados para equalização: " +
            ", ".join(
                f"[Palete: ({p.SourceSpace}), "
                f"Ocupação a permanecer: {p.StayOccupation:.2f}%, "
                f"Ocupação a mover: {p.MoveOccupation:.2f}%]"
                for p in pallets
            )
        )

        for target_space in empty_spaces:
            for pallet in [p for p in pallets if not p.IsEqualized]:
                source_space = context.GetMountedSpace(pallet.SourceSpace)

                if not self.CanAddProductsInSpace(
                    pallet.ProductsToMove,
                    target_space,
                    context.get_setting('OccupationAdjustmentToPreventExcessHeight')
                ):
                    continue

                context.add_execution_log(
                    f"Movendo os produtos "
                    f"[{', '.join(str(p.Product.Code) for p in pallet.ProductsToMove)}] "
                    f"do Palete: ({pallet.SourceSpace}) "
                    f"para o Palete: ({target_space})"
                )

                context.domain_operations.move_mounted_products(
                    context,
                    target_space,
                    source_space,
                    pallet.ProductsToMove
                )

                pallet.IsEqualized = True
                break

    # ---------- CAN ADD PRODUCTS ----------

    def CanAddProductsInSpace(self, products, space, occupation_adjustment):
        total = Decimal(0)

        for product in products:
            occupation = Decimal(
                self._factor_converter.Occupation(
                    product,
                    space.Size,
                    product.Item,
                    occupation_adjustment
                )
            )

            occupation = (
                occupation * Decimal(100)
            ).to_integral_value(rounding=ROUND_DOWN) / Decimal(100)

            total += occupation

        return total <= Decimal(space.Size)

    # ---------- MULTIPLE GROUPS ----------

    def SelectPalletsToEqualizeWithMultipleGroups(self, context, out_list, min_percent):
        spaces = (
            MountedSpaceList(context.MountedSpaces)
            .NotBulk()
            .NotContainProductComplex()
            .WithMultipleGroups()
            .Matching(lambda x: x.OccupiedPercentage >= context.get_setting('PercentOccupationMinByDivision'))
        )

        for mounted_space in spaces:
            products = mounted_space.GetProducts()

            groups = {}
            for p in products:
                key = p.Product.PackingGroup.GroupCode
                groups[key] = groups.get(key, Decimal(0)) + p.PercentOccupationIntoDefaultPalletSize

            group_key, group_val = max(groups.items(), key=lambda x: x[1])
            remaining = sum(v for k, v in groups.items() if k != group_key)

            if not self.CanEqualizePallet(min_percent, remaining, group_val):
                continue

            out_list.append(
                PalletEqualizeDto(
                    MoveOccupation=group_val,
                    StayOccupation=remaining,
                    SourceSpace=mounted_space.Space,
                    ProductsToMove=[
                        p for p in products
                        if p.Product.PackingGroup.GroupCode == group_key
                    ]
                )
            )

    # ---------- MULTIPLE PACKAGES ----------

    def SelectPalletsToEqualizeWithMultiplePackages(self, context, out_list, min_percent):
        spaces = (
            MountedSpaceList(context.MountedSpaces)
            .NotBulk()
            .NotContainProductComplex()
            .WithSameGroupAndMultiplePackages()
            .Matching(lambda x: x.OccupiedPercentage >= context.get_setting('PercentOccupationMinByDivision'))
        )

        specific_groups = None
        if context.get_setting('ProductGroupSpecific'):
            specific_groups = list(map(int, context.get_setting('ProductGroupSpecific').split(",")))

        for mounted_space in spaces:
            products = mounted_space.GetProducts()

            if specific_groups and all(
                p.Product.PackingGroup.GroupCode in specific_groups
                for p in products
            ):
                ordered = sorted(products, key=lambda p: p.Product.PackingGroup.PackingCode)
                self.PalletEqualizationSplit(
                    context, out_list, mounted_space, ordered, min_percent
                )
                continue

            packages = {}
            for p in products:
                key = p.Product.PackingGroup.PackingCode
                packages[key] = packages.get(key, Decimal(0)) + p.PercentOccupationIntoDefaultPalletSize

            pack_key, pack_val = max(packages.items(), key=lambda x: x[1])
            remaining = sum(v for k, v in packages.items() if k != pack_key)

            if not self.CanEqualizePallet(min_percent, remaining, pack_val):
                continue

            out_list.append(
                PalletEqualizeDto(
                    MoveOccupation=pack_val,
                    StayOccupation=remaining,
                    SourceSpace=mounted_space.Space,
                    ProductsToMove=[
                        p for p in products
                        if p.Product.PackingGroup.PackingCode == pack_key
                    ]
                )
            )

    # ---------- MULTIPLE ITEMS ----------

    def SelectPalletsToEqualizeWithMultipleItems(self, context, out_list, min_percent):
        spaces = (
            MountedSpaceList(context.MountedSpaces)
            .NotBulk()
            .NotContainProductComplex()
            .WithSameGroupAndPackageAndMultipleItems()
            .Matching(lambda x: x.OccupiedPercentage >= context.get_setting('PercentOccupationMinByDivision'))
        )

        for mounted_space in spaces:
            products = mounted_space.GetProducts()
            if len(products) <= 1:
                continue

            ordered = sorted(
                products,
                key=lambda p: p.PercentOccupationIntoDefaultPalletSize,
                reverse=True
            )

            self.PalletEqualizationSplit(
                context, out_list, mounted_space, ordered, min_percent
            )

    # ---------- SPLIT ----------

    def PalletEqualizationSplit(self, context, out_list, mounted_space, products, min_percent):
        total = sum(p.PercentOccupationIntoDefaultPalletSize for p in products)
        half = total / Decimal(2)

        if half < Decimal(min_percent):
            return

        first, second = [], []
        occupation = Decimal(0)

        for product in products:
            if occupation + product.PercentOccupationIntoDefaultPalletSize <= half:
                first.append(product)
                occupation += product.PercentOccupationIntoDefaultPalletSize
            else:
                second.append(product)

        stay = sum(p.PercentOccupationIntoDefaultPalletSize for p in first)
        move = sum(p.PercentOccupationIntoDefaultPalletSize for p in second)

        if not self.CanEqualizePallet(min_percent, stay, move):
            return

        out_list.append(
            PalletEqualizeDto(
                StayOccupation=stay,
                MoveOccupation=move,
                SourceSpace=mounted_space.Space,
                ProductsToMove=second
            )
        )

    # ---------- HELPERS ----------

    def CanEqualizePallet(self, min_percent, stay, move):
        return stay >= Decimal(min_percent) and move >= Decimal(min_percent)

    def OrderPalletsByOptimalOccupation(self, pallets):
        return sorted(
            pallets,
            key=lambda x: max(
                abs(x.StayOccupation - Decimal(50)),
                abs(x.MoveOccupation - Decimal(50))
            )
        )