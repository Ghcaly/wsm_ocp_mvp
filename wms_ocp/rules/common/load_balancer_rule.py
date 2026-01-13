from ...domain.mounted_space_list import MountedSpaceList
from ...domain.base_rule import BaseRule
from ...domain.context import Context
from dataclasses import dataclass
from typing import List, Optional
from ...domain.calculator_constants import CalculatorConstants

@dataclass
class SpaceWithMountedSpaceDto:
    Space: object
    MountedSpace: object


class LoadBalancerRule(BaseRule):
    """Faithful, organized port of the C# LoadBalancerRule.

    This implementation follows the C# control flow and calls domain
    operations to switch spaces. It assumes the project's domain objects
    expose the same helper methods used by the original C# rule.
    """

    def __init__(self):
        super().__init__(name='LoadBalancerRule')

    def should_execute(self, context: Context) -> bool:
        if context.get_setting('SideBalanceRule', False):
            context.add_execution_log('Regra SideBalanceRule ativada, LoadBalancerRule nao sera executada')
            return False
        return True

    def execute(self, context: Context) -> Context: 

        # Skip AS contexts (mirror C# type check)
        try:
            if context.__class__.__name__ == 'ASRuleContext':
                context.add_execution_log('Mapas de AS nao executam balanceamento de carga, finalizando execucao')
                return context
        except Exception:
            pass

        min_spaces = CalculatorConstants.MINIMUM_MOUNTED_SPACES_TO_BALANCE
        if len(getattr(context, 'mounted_spaces', []) or []) <= min_spaces:
            context.add_execution_log(f'Necessario ter mais baias montadas para balancear, o mapa tem {len(getattr(context, "mounted_spaces", []) or [])}')
            return context

        total_weight = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [])
        if total_weight == 0:
            context.add_execution_log('Necessario ter peso total maior que zero. Parando execucao da regra')
            return context

        percentage_weight_driver_side = self._get_percentage_weight_of_driver_side(context)

        if not self._should_try_balance(context, percentage_weight_driver_side):
            return context

        percentage_initial = percentage_weight_driver_side

        current_pallet_weights = self._get_pallet_weight_log_message(context)

        # Work on a snapshot as C# does
        if hasattr(context, 'create_snapshot'):
            context.create_snapshot()

        snapshot = getattr(context, 'snapshot', context)
        percentage_balanced = self._balance_context(snapshot, percentage_weight_driver_side, heavy_first=False)

        if self._before_balancer_has_better(context, percentage_initial, percentage_balanced):
            if hasattr(context, 'create_snapshot'):
                context.create_snapshot()
            snapshot2 = getattr(context, 'snapshot', context)
            new_percentage_balanced = self._balance_context(snapshot2, percentage_weight_driver_side, heavy_first=True)

            if self._before_balancer_has_better(context, percentage_initial, new_percentage_balanced):
                context.add_execution_log(f'Finalizada execução da regra sem efetivar o balaceamento pois o resultado foi o mesmo ou pior')
                return context

        # Apply the snapshot into the real context (C# ChangeContext)
        try:
            if hasattr(context, 'change_context'):
                context.change_context(getattr(context, 'snapshot', context))
        except Exception:
            pass

        snapshot_pallet_weights = self._get_pallet_weight_log_message(getattr(context, 'snapshot', context))
        context.add_execution_log(f'Finalizada execução da regra, {snapshot_pallet_weights}')
        return context

    # ---------------- helper methods ------------------------------------
    def _before_balancer_has_better(self, context: Context, initial: float, balanced: float) -> bool:
        best = float(CalculatorConstants.BEST_DISTRIBUTION_PER_SIDE)
        return abs(best - float(initial)) <= abs(best - float(balanced))

    def _balance_context(self, ctx, percentage_weight_driver_side: float, heavy_first: bool) -> float:
        retries = 0
        pct = float(percentage_weight_driver_side)

        while True:
            ctx.add_execution_log(f'Tentativa nº {retries} de balancear o mapa, atualmente com {pct:.2f} Lado Motorista')

            driver_space = self._get_selected_driver_side_space(ctx, pct, heavy_first)
            if not driver_space:
                ctx.add_execution_log('Nao foi localizada uma baia do lado do motorista que atenda aos requisitos para balancear. Parando execução da regra')
                break

            helper_space = self._get_selected_helper_side_space(ctx, driver_space, pct)
            if not helper_space:
                ctx.add_execution_log('Nao foi localizada uma baia do lado do passageiro que atenda aos requisitos para balancear. Parando execução da regra')
                break

            if self._allow_to_change_sides(driver_space, helper_space, ctx):
                ctx.add_execution_log(f'Balanceando a baia nº:{getattr(driver_space.Space, "Number", getattr(driver_space.Space, "number", "?"))} com a baia nº:{getattr(helper_space.Space, "Number", getattr(helper_space.Space, "number", "?"))}')
                try:
                    # delegate to domain operations to switch spaces
                    ctx.domain_operations.switch_spaces(ctx, driver_space.Space, helper_space.Space)
                except Exception:
                    try:
                        # alternative signature
                        ctx.domain_operations.switch_spaces(driver_space.Space, helper_space.Space)
                    except Exception:
                        pass

                pct = self._get_percentage_weight_of_driver_side(ctx)

            # mark spaces as balanced if they expose SetBalanced / set_balanced
            try:
                if hasattr(driver_space.Space, 'SetBalanced'):
                    driver_space.Space.SetBalanced()
                elif hasattr(driver_space.Space, 'set_balanced'):
                    driver_space.Space.set_balanced()
            except Exception:
                pass

            try:
                if hasattr(helper_space.Space, 'SetBalanced'):
                    helper_space.Space.SetBalanced()
                elif hasattr(helper_space.Space, 'set_balanced'):
                    helper_space.Space.set_balanced()
            except Exception:
                pass

            retries += 1

            if not self._should_try_balance(ctx, pct):
                break

        return pct

    def _get_percentage_weight_of_driver_side(self, context: Context) -> float:
        total_weight = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [])
        if total_weight == 0:
            return 0.0
        # determine driver side using space.side attribute where 'driver' startswith 'd'
        weight_driver = 0.0
        for ms in getattr(context, 'mounted_spaces', []) or []:
            side = getattr(getattr(ms, 'space', None), 'side', '')
            try:
                if isinstance(side, str) and side.strip().lower().startswith('d'):
                    weight_driver += float(getattr(ms, 'weight', 0) or 0)
            except Exception:
                continue
        return (weight_driver * 100.0) / float(total_weight)

    def _should_try_balance(self, context: Context, percentage_weight_driver_side: float) -> bool:
        max_d = float(CalculatorConstants.MAXIMUM_DISTRIBUTION_PER_SIDE)
        min_d = float(CalculatorConstants.MINIMUM_DISTRIBUTION_PER_SIDE)
        # fallback to a mounted-spaces filter if available
        try:
            has_spaces = context.HasNotChoppNotBalancedSpaces()
        except Exception:
            # best-effort: check if any mounted space is not chopp and not balanced
            has_spaces = any((not getattr(ms, 'is_chopp', False)) and (not getattr(getattr(ms, 'space', None), 'balanced', False)) for ms in getattr(context, 'mounted_spaces', []) or [])

        return ((percentage_weight_driver_side > max_d or percentage_weight_driver_side < min_d) and has_spaces)

    def _get_selected_driver_side_space(self, context, percentage_weight_driver_side: float, heavy_first: bool) -> Optional[SpaceWithMountedSpaceDto]:
        # Try to use domain helpers if they exist, otherwise filter manually
        try:
            selected_spaces = MountedSpaceList(context.GetNotChoppNotBalancedSpaces()).DriverSide()
        except Exception:
            selected_spaces = [ms.space for ms in getattr(context, 'mounted_spaces', []) or [] if (not getattr(ms, 'is_chopp', False)) and (not getattr(getattr(ms, 'space', None), 'balanced', False)) and (getattr(ms.space, 'side', '').strip().lower().startswith('d'))]

        spaces_dto = self._get_spaces_dto(context, selected_spaces)

        if not spaces_dto:
            return None

        # order by mounted space weight
        try:
            if heavy_first:
                spaces_dto = sorted(spaces_dto, key=lambda x: getattr(x.MountedSpace, 'weight', 0))
            else:
                spaces_dto = sorted(spaces_dto, key=lambda x: getattr(x.MountedSpace, 'weight', 0), reverse=True)
        except Exception:
            pass

        maximum = float(CalculatorConstants.MAXIMUM_DISTRIBUTION_PER_SIDE)
        if percentage_weight_driver_side > maximum:
            # return heaviest
            return next((s for s in sorted(spaces_dto, key=lambda x: getattr(x.MountedSpace, 'weight', 0), reverse=True)), None)
        return spaces_dto[0]

    def _get_selected_helper_side_space(self, context, driver_space_dto: SpaceWithMountedSpaceDto, percentage_weight_driver_side: float) -> Optional[SpaceWithMountedSpaceDto]:
        try:
            selected_spaces = MountedSpaceList(context.GetNotChoppNotBalancedSpaces()).HelperSide().MaxTwoSpacesOfDistanceTo(driver_space_dto.Space)
        except Exception:
            # fallback: helper spaces are those on opposite side and not balanced
            selected_spaces = [ms.space for ms in getattr(context, 'mounted_spaces', []) or [] if (not getattr(ms, 'is_chopp', False)) and (not getattr(getattr(ms, 'space', None), 'balanced', False)) and (not getattr(ms.space, 'side', '').strip().lower().startswith('d'))]

        spaces_dto = self._get_spaces_dto(context, selected_spaces)

        # filter by type compatibility if supported
        try:
            spaces_dto = [s for s in spaces_dto if self._can_swap_sides_by_type(driver_space_dto, s)]
        except Exception:
            pass

        maximum = float(CalculatorConstants.MAXIMUM_DISTRIBUTION_PER_SIDE)
        if percentage_weight_driver_side > maximum:
            # prefer helper with weight < driver and pick heaviest among them
            candidates = [s for s in spaces_dto if getattr(s.MountedSpace, 'weight', 0) < getattr(driver_space_dto.MountedSpace, 'weight', 0)]
            if candidates:
                return sorted(candidates, key=lambda x: getattr(x.MountedSpace, 'weight', 0), reverse=True)[0]
        else:
            candidates = [s for s in spaces_dto if getattr(s.MountedSpace, 'weight', 0) > getattr(driver_space_dto.MountedSpace, 'weight', 0)]
            if candidates:
                return sorted(candidates, key=lambda x: getattr(x.MountedSpace, 'weight', 0))[0]

        return spaces_dto[0] if spaces_dto else None

    def _get_spaces_dto(self, context, selected_spaces) -> List[SpaceWithMountedSpaceDto]:
        lst = []
        for sp in selected_spaces or []:
            try:
                ms = context.get_mounted_space(sp)
            except Exception:
                ms = None
            lst.append(SpaceWithMountedSpaceDto(Space=sp, MountedSpace=ms))
        return lst

    def _can_swap_sides_by_type(self, driver_space_dto: SpaceWithMountedSpaceDto, helper_space_dto: SpaceWithMountedSpaceDto) -> bool:
        try:
            driver_pallet = driver_space_dto.MountedSpace.GetFirstPallet()
            helper_pallet = helper_space_dto.MountedSpace.GetFirstPallet()

            if getattr(driver_space_dto.Space, 'number', None) == getattr(helper_space_dto.Space, 'number', None) or getattr(driver_pallet, 'remount', False) or getattr(helper_pallet, 'remount', False):
                return True

            if driver_pallet is None or helper_pallet is None:
                return False

            dtype = getattr(driver_pallet.ProductBase, 'ContainerType', None)
            htype = getattr(helper_pallet.ProductBase, 'ContainerType', None)

            if dtype in ('Disposable', 'IsotonicWater'):
                return htype in ('Disposable', 'IsotonicWater')
            if dtype == 'Returnable':
                return htype == 'Returnable'
            return False
        except Exception:
            return False

    def _allow_to_change_sides(self, driver_space_dto: SpaceWithMountedSpaceDto, helper_space_dto: SpaceWithMountedSpaceDto, context: Context) -> bool:
        if getattr(driver_space_dto.Space, 'size', None) == getattr(helper_space_dto.Space, 'size', None):
            return True

        if getattr(driver_space_dto.Space, 'size', 0) < getattr(helper_space_dto.Space, 'size', 0):
            return self._products_fit_into_smaller_space(driver_space_dto, helper_space_dto, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))
        else:
            return self._products_fit_into_smaller_space(helper_space_dto, driver_space_dto, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))

    def _products_fit_into_smaller_space(self, small_space_dto: SpaceWithMountedSpaceDto, big_space_dto: SpaceWithMountedSpaceDto, calculate_additional_occupation: bool) -> bool:
        try:
            products = big_space_dto.MountedSpace.get_first_pallet().Products
            # FactorConverter usage: assume product objects provide occupation calculation method via context.factor_converter
            fc = None
            try:
                from ...domain.factor_converter import FactorConverter
                fc = FactorConverter()
            except Exception:
                fc = None

            total = 0.0
            for p in products:
                try:
                    if fc:
                        occ = fc.occupation(p, getattr(small_space_dto.Space, 'size', 0), getattr(p, 'item', None), calculate_additional_occupation)
                    else:
                        occ = getattr(p, 'percent_occupation_into_default_pallet_size', 0) or getattr(p, 'PercentOccupationIntoDefaultPalletSize', 0)
                    total += float(occ)
                except Exception:
                    continue

            return total <= float(getattr(small_space_dto.Space, 'size', 0) or 0)
        except Exception:
            return False

    def _get_pallet_weight_log_message(self, context: Context) -> str:
        parts = []
        for ms in sorted(getattr(context, 'mounted_spaces', []) or [], key=lambda x: getattr(x.space, 'number', 0)):
            side = getattr(ms.space, 'side', '?')
            number = getattr(ms.space, 'number', '?')
            weight = getattr(ms, 'weight', 0) or 0
            parts.append(f"{side}/{number} weight: {weight:.2f}")
        return '; '.join(parts)
