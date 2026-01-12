from domain.base_rule import BaseRule
from domain.context import Context
from domain.factor_converter import FactorConverter
from dataclasses import dataclass
from typing import List, Any


@dataclass
class PalletEqualizeDto:
    MoveOccupation: float
    StayOccupation: float
    SourceSpace: Any
    ProductsToMove: List[Any]
    IsEqualized: bool = False


class PalletEqualizationRule(BaseRule):
    """Faithful Python port of the C# PalletEqualizationRule.

    This implementation follows the C# control flow and naming, but written
    in idiomatic Python. It calls domain operations and factor converter
    the same way the C# version does, assuming those helpers exist on the
    context and mounted-product objects.
    """

    def __init__(self):
        super().__init__(name='PalletEqualizationRule2')
        self._factor_converter = FactorConverter()

    def should_execute(self, context: Context, item_predicate=None, mounted_space_predicate=None) -> bool:
        if not context.get_setting('PalletEqualizationRule', True):
            context.add_execution_log('Regra desativada, nao sera executada')
            return False

        if not context.MountedSpaces:
            context.add_execution_log('Nenhuma baia montada, a regra nao sera executada')
            return False

        if not context.Spaces:
            context.add_execution_log('Nenhum palete vazio encontrado, a regra nao sera executada')
            return False

        # mirror C#: context.MountedSpaces.NotBulk().NotContainProductComplex().Any(x => x.OccupiedPercentage >= ... && x.GetProducts().Count() > 1)
        candidates = context.MountedSpaces.NotBulk().NotContainProductComplex()
        threshold = context.get_setting('PercentOccupationMinByDivision', 0)
        for ms in candidates:
            if ms.OccupiedPercentage >= threshold and len(ms.GetProducts()) > 1:
                return True

        context.add_execution_log('Nenhum palete atende o percentual de ocupacao minimo, a regra nao sera executada')
        return False

    def execute(self, context: Context) -> Context:
        context.add_execution_log('Iniciando execução da regra PalletEqualizationRule2')

        pallets_to_equalize: List[PalletEqualizeDto] = []
        min_percent = context.get_setting('PercentOccupationMinBySelectionPalletDisassembly', 0)

        # selection phases (parity with C#)
        self._select_pallets_with_multiple_groups(context, pallets_to_equalize, min_percent)
        self._select_pallets_with_multiple_packages(context, pallets_to_equalize, min_percent)
        self._select_pallets_with_multiple_items(context, pallets_to_equalize, min_percent)

        if not pallets_to_equalize:
            context.add_execution_log('Nenhum palete atende a configuracao de ocupacao minima na divisao dos paletes')
            return context

        # equalize (move products)
        self._equalize_pallets(context, pallets_to_equalize)

        context.add_execution_log('Finalizado a execucao da regra PalletEqualizationRule2')
        return context

    def _equalize_pallets(self, context: Context, pallets_to_equalize: List[PalletEqualizeDto]) -> None:
        # use context.Spaces.OrderedBySizeAndNumber() as in C# if available
        try:
            empty_spaces = context.Spaces.OrderedBySizeAndNumber()
        except Exception:
            empty_spaces = context.Spaces

        # order pallets by optimal occupation (closest to 50/50)
        pallets_to_equalize = sorted(pallets_to_equalize, key=lambda x: max(abs(x.StayOccupation - 50), abs(x.MoveOccupation - 50)))

        # debug log
        try:
            log_message = 'Paletes selecionados para equalizacao: ' + ', '.join([
                f'[Palete: ({p.SourceSpace}), Ocupacao a permanecer: {p.StayOccupation:.2f}%, Ocupacao a mover: {p.MoveOccupation:.2f}%]'
                for p in pallets_to_equalize
            ])
            context.add_execution_log(log_message)
        except Exception:
            pass

        for target_space in empty_spaces:
            for pallet in [p for p in pallets_to_equalize if not p.IsEqualized]:
                source_mounted_space = context.GetMountedSpace(pallet.SourceSpace)

                if not self._can_add_products_in_space(pallet.ProductsToMove, target_space, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)):
                    continue

                try:
                    # log intent
                    try:
                        codes = [str(x.Product.Code) for x in pallet.ProductsToMove]
                    except Exception:
                        codes = [str(getattr(x, 'product', '?')) for x in pallet.ProductsToMove]

                    context.add_execution_log(f"Movendo os produtos [{', '.join(codes)}] do Palete: ({pallet.SourceSpace}) para o Palete: ({target_space})")

                    # perform the domain operation to move products (parity with C# _mountedSpaceOperations.MoveMountedProducts)
                    context.domain_operations.move_mounted_products(context, target_space, source_mounted_space, pallet.ProductsToMove)
                    pallet.IsEqualized = True
                    break
                except Exception:
                    # best-effort: ignore and try next pallet
                    continue

    def _can_add_products_in_space(self, products_to_move: List[Any], space: Any, occupation_adjustment: bool) -> bool:
        # mirror C#: sum factorConverter.Occupation(product, space.Size, product.Item, occupationAdjustmentToPreventExcessHeight)
        total = 0
        for p in products_to_move:
            try:
                occ = self._factor_converter.Occupation(p, space.Size, p.Item, occupation_adjustment)
            except Exception:
                try:
                    # fallback to alternate signature if required by python port
                    qty = getattr(p, 'Amount', getattr(p, 'amount', 0))
                    factor = getattr(p.Product, 'GetFactor', lambda s: None)(space.Size)
                    occ = self._factor_converter.occupation(qty, factor, getattr(p.Product, 'PalletSetting', None), getattr(p, 'Item', None), occupation_adjustment)
                except Exception:
                    occ = 0
            try:
                # truncate two decimals like C# Math.Truncate(100 * occupation) / 100
                total += float(int(occ * 100) / 100)
            except Exception:
                try:
                    total += float(getattr(occ, 'value', 0))
                except Exception:
                    total += 0

        try:
            return total <= float(space.Size)
        except Exception:
            return total <= float(getattr(space, 'size', getattr(space, 'Size', 0)))

    # ---------------- selection helpers ---------------------------------
    def _select_pallets_with_multiple_groups(self, context: Context, out_list: List[PalletEqualizeDto], min_percent: int) -> None:
        mounted_spaces = context.MountedSpaces.NotBulk().NotContainProductComplex().WithMultipleGroups()
        for ms in mounted_spaces:
            products = ms.GetProducts()
            if len(products) <= 1:
                continue

            groups = {}
            for p in products:
                key = p.Product.PackingGroup.GroupCode
                val = getattr(p, 'PercentOccupationIntoDefaultPalletSize', getattr(p, 'percent_occupation_into_default_pallet_size', 0))
                groups.setdefault(key, 0)
                groups[key] += float(val)

            if not groups:
                continue

            # group with max occupation
            group_key, group_val = max(groups.items(), key=lambda kv: kv[1])
            remaining = sum(v for k, v in groups.items() if k != group_key)

            if not (remaining >= min_percent and group_val >= min_percent):
                continue
            products_to_move = [p for p in products if p.Product.PackingGroup.GroupCode == group_key]
            try:
                codes = [str(p.Product.Code) for p in products_to_move]
                context.add_execution_log(f"PalletEqualizationRule - selecionado grupo {group_key} no palete {ms.Space} - produtos: {', '.join(codes)} - stay={remaining:.2f} move={group_val:.2f}")
            except Exception:
                pass
            out_list.append(PalletEqualizeDto(MoveOccupation=group_val, StayOccupation=remaining, SourceSpace=ms.Space, ProductsToMove=products_to_move))

    def _select_pallets_with_multiple_packages(self, context: Context, out_list: List[PalletEqualizeDto], min_percent: int) -> None:
        mounted_spaces = context.MountedSpaces.NotBulk().NotContainProductComplex().WithSameGroupAndMultiplePackages()
        specific_groups = None
        gps = context.get_setting('ProductGroupSpecific')
        if isinstance(gps, str) and gps.strip():
            try:
                specific_groups = [int(x) for x in gps.split(',')]
            except Exception:
                specific_groups = None

        for ms in mounted_spaces:
            products = ms.GetProducts()
            if len(products) <= 1:
                continue

            is_specific = specific_groups is not None and all(p.Product.PackingGroup.GroupCode in specific_groups for p in products)
            if is_specific:
                ordered = sorted(products, key=lambda x: x.Product.PackingGroup.PackingCode)
                self._pallet_equalization_split(context, out_list, ms, ordered, min_percent)
                continue

            packs = {}
            for p in products:
                key = p.Product.PackingGroup.PackingCode
                val = getattr(p, 'PercentOccupationIntoDefaultPalletSize', getattr(p, 'percent_occupation_into_default_pallet_size', 0))
                packs.setdefault(key, 0)
                packs[key] += float(val)

            if not packs:
                continue

            pack_key, pack_val = max(packs.items(), key=lambda kv: kv[1])
            remaining = sum(v for k, v in packs.items() if k != pack_key)

            if not (remaining >= min_percent and pack_val >= min_percent):
                continue
            products_to_move = [p for p in products if p.Product.PackingGroup.PackingCode == pack_key]
            try:
                codes = [str(p.Product.Code) for p in products_to_move]
                context.add_execution_log(f"PalletEqualizationRule - selecionado packing {pack_key} no palete {ms.Space} - produtos: {', '.join(codes)} - stay={remaining:.2f} move={pack_val:.2f}")
            except Exception:
                pass
            out_list.append(PalletEqualizeDto(MoveOccupation=pack_val, StayOccupation=remaining, SourceSpace=ms.Space, ProductsToMove=products_to_move))

    def _select_pallets_with_multiple_items(self, context: Context, out_list: List[PalletEqualizeDto], min_percent: int) -> None:
        mounted_spaces = context.MountedSpaces.NotBulk().NotContainProductComplex().WithSameGroupAndPackageAndMultipleItems()
        for ms in mounted_spaces:
            products = ms.GetProducts()
            if len(products) <= 1:
                continue
            ordered = sorted(products, key=lambda p: getattr(p, 'PercentOccupationIntoDefaultPalletSize', getattr(p, 'percent_occupation_into_default_pallet_size', 0)), reverse=True)
            self._pallet_equalization_split(context, out_list, ms, ordered, min_percent)

    def _pallet_equalization_split(self, context: Context, out_list: List[PalletEqualizeDto], mounted_space: Any, products: List[Any], min_percent: int) -> None:
        total = sum(getattr(p, 'PercentOccupationIntoDefaultPalletSize', getattr(p, 'percent_occupation_into_default_pallet_size', 0)) for p in products)
        half = total / 2

        if half < min_percent:
            return

        first = []
        second = []
        occ = 0.0
        for p in products:
            v = float(getattr(p, 'PercentOccupationIntoDefaultPalletSize', getattr(p, 'percent_occupation_into_default_pallet_size', 0)))
            if occ + v <= total / 2:
                first.append(p)
                occ += v
            else:
                second.append(p)

        stay = sum(float(getattr(x, 'PercentOccupationIntoDefaultPalletSize', getattr(x, 'percent_occupation_into_default_pallet_size', 0))) for x in first)
        move = sum(float(getattr(x, 'PercentOccupationIntoDefaultPalletSize', getattr(x, 'percent_occupation_into_default_pallet_size', 0))) for x in second)

        if not (stay >= min_percent and move >= min_percent):
            return
        try:
            codes = [str(p.Product.Code) for p in second]
            context.add_execution_log(f"PalletEqualizationRule - divisao por itens no palete {mounted_space.Space} - manter={stay:.2f} mover={move:.2f} produtos: {', '.join(codes)}")
        except Exception:
            pass

        out_list.append(PalletEqualizeDto(MoveOccupation=move, StayOccupation=stay, SourceSpace=mounted_space.Space, ProductsToMove=second))
